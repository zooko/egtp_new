#  Copyright (c) 2001 Autonomous Zone Industries
#  Copyright (c) 2003 Bryce "Zooko" Wilcox-O'Hearn
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: Conversation.py,v 1.19 2003/03/09 18:54:57 zooko Exp $"

# Python Standard Library modules
import threading
import types
import traceback
import sys
from sha import sha
from time import time
import exceptions
import socket
import os
import types
from traceback import print_exc

# pyutil modules
from pyutil import Cache
from pyutil import DoQ, nummedobj
from pyutil.debugprint import debugprint, debugstream
from pyutil.humanreadable import hr

from pyutil import assertutil
assertutil.hr = hr
from pyutil.assertutil import _assert, precondition, postcondition

# EGTP modules
from egtp.CommHints import HINT_EXPECT_RESPONSE, HINT_EXPECT_MORE_TRANSACTIONS, HINT_EXPECT_NO_MORE_COMMS, HINT_EXPECT_TO_RESPOND, HINT_THIS_IS_A_RESPONSE, HINT_NO_HINT
from egtp import CommStrat, MojoMessage
from egtp import idlib, mencode, mojosixbit, std
from egtp.crypto import modval, randsource
import MojoTransaction

true = 1
false = 0

HANDLED = 0
EXPECTING_RESPONSE = 1

TUNING_FACTOR=float(2**8)

def is_mojo_message(thingie):
    return (type(thingie) is types.DictType) and (thingie.has_key('mojo header') or thingie.has_key('mojo message'))

class DebugDiagLoop(DoQ.DoQLoop, nummedobj.NummedObj):
    def __init__(self, cm):
        self.maxcbs = 0
        self.maxpcbs = 0
        self.maxoms = 0
        self.maxli2i = 0
        self.maxfps = 0
        DoQ.DoQLoop.__init__(self)
        nummedobj.NummedObj.__init__(self)
        self.cm = cm
        self.schedule_event()

    def event(self):
        if len(self.cm._callback_functions) > self.maxcbs:
            self.maxcbs = len(self.cm._callback_functions)
            debugprint("%s.event(): new max len(self.cm._callback_functions): %s, len(self.cm._posttimeout_callback_functions): %s, len(self.cm._map_inmsgid_to_info): %s, len(self.cm._map_cid_to_freshness_proof): %s\n", args=(self, len(self.cm._callback_functions), len(self.cm._posttimeout_callback_functions), len(self.cm._map_inmsgid_to_info), len(self.cm._map_cid_to_freshness_proof),), v=3, vs="Conversation")

        if len(self.cm._posttimeout_callback_functions) > self.maxpcbs:
            self.maxpcbs = len(self.cm._posttimeout_callback_functions)
            debugprint("%s.event(): len(self.cm._callback_functions): %s, new max len(self.cm._posttimeout_callback_functions): %s, len(self.cm._map_inmsgid_to_info): %s, len(self.cm._map_cid_to_freshness_proof): %s\n", args=(self, len(self.cm._callback_functions), len(self.cm._posttimeout_callback_functions), len(self.cm._map_inmsgid_to_info), len(self.cm._map_cid_to_freshness_proof),), v=3, vs="Conversation")

        if len(self.cm._callback_functions) > self.maxoms:
            self.maxoms = len(self.cm._callback_functions)
            debugprint("%s.event(): len(self.cm._callback_functions): %s, len(self.cm._posttimeout_callback_functions): %s, new max len(self.cm._callback_functions): %s, len(self.cm._map_inmsgid_to_info): %s, len(self.cm._map_cid_to_freshness_proof): %s\n", args=(self, len(self.cm._callback_functions), len(self.cm._posttimeout_callback_functions), len(self.cm._callback_functions), len(self.cm._map_inmsgid_to_info), len(self.cm._map_cid_to_freshness_proof),), v=3, vs="Conversation")

        if len(self.cm._map_inmsgid_to_info) > self.maxli2i:
            self.maxli2i = len(self.cm._map_inmsgid_to_info)
            debugprint("%s.event(): len(self.cm._callback_functions): %s, len(self.cm._posttimeout_callback_functions): %s, new max len(self.cm._map_inmsgid_to_info): %s, len(self.cm._map_cid_to_freshness_proof): %s\n", args=(self, len(self.cm._callback_functions), len(self.cm._posttimeout_callback_functions), len(self.cm._map_inmsgid_to_info), len(self.cm._map_cid_to_freshness_proof),), v=3, vs="Conversation")

        if len(self.cm._map_cid_to_freshness_proof) > self.maxfps:
            self.maxfps = len(self.cm._map_cid_to_freshness_proof)
            debugprint("%s.event(): len(self.cm._callback_functions): %s, len(self.cm._posttimeout_callback_functions): %s, len(self.cm._map_inmsgid_to_info): %s, new max len(self.cm._map_cid_to_freshness_proof): %s\n", args=(self, len(self.cm._callback_functions), len(self.cm._posttimeout_callback_functions), len(self.cm._map_inmsgid_to_info), len(self.cm._map_cid_to_freshness_proof),), v=3, vs="Conversation")

        self.schedule_event(delay=60)

class ConversationManager:
    def __init__(self, MTM):
        self._MTM = MTM
        # maps first message ids to (counterparty_id, callback function, notes for callback, conversation type, post_timeout_callback_func, timeoutcheckerschedtime,)
        self.__callback_functions = {}

        # maps message id's of messages who's responses have timed out to (recipient_id, conversation type, time of timeout, post timeout callback function, notes [only if post timeout callback function])
        # Reminder: this indirectly holds references to the original outgoing message body as well as the metainfo used to send it.  That is often large.
        self._posttimeout_callback_functions = Cache.LRUCache(maxsize=128)

        # maps message id to (binary counterparty_id, message type, response status)
        # where status is HANDLED or EXPECTING_RESPONSE
        # This data structure is used between receiving a specific initiating message and
        # sending the response to it.  It is not used for incoming response messages.
        self._map_inmsgid_to_info = {}

        # This is a map from counterparty_id to the binary msgId of the last message you
        # received from that counterparty.  We use the msgId in outgoing messages, thus proving
        # to the counterparty that our messages are fresh (i.e., they are not replay attacks or
        # other sneaky trickery).  Actually our current software does not check the incoming
        # freshness proofs, but this code ensures that when we ship a new, replay-attack-proof
        # version which _does_ verify freshness proofs, then older apps which are running _this_
        # version of our software will be able to interoperate with it.
        self._map_cid_to_freshness_proof = Cache.LRUCache(maxsize=128)

        self._in_message_num = 0L   # used only in debugging

    def shutdown(self):
        debugprint("self._map_inmsgid_to_info: %s\n", args=(self._map_inmsgid_to_info,), v=6, vs="debug")
        self.__callback_functions = {}
        self._posttimeout_callback_functions.clear()
        self._map_inmsgid_to_info = {}
        self._map_cid_to_freshness_proof.clear()

    def initiate_and_return_first_message(self, counterparty_id, conversationtype, firstmsgbody, outcome_func, timeout = 300, notes = None, mymetainfo=None, post_timeout_outcome_func=None):
        """
        @precondition: `counterparty_id' must be  an id.: idlib.is_sloppy_id(counterparty_id): "id: %s" % hr(id)

        @return: a tuple of (message_id, binary_message_string)
        """
        assert idlib.is_sloppy_id(counterparty_id), "precondition: `counterparty_id' must be  an id." + " -- " + "id: %s" % hr(id)

        counterparty_id = idlib.canonicalize(counterparty_id, "broker")

        # Our `freshness proof' is the hash of the last message that we saw from this counterparty.

        # If we don't have such a last message, we leave it blank.

        # Currently, Mojo Nation brokers accept any freshnessproof and don't check to be
        # sure that it is really a proof of freshness, so currently either of these cases
        # will work.  In the future Mojo Nation brokers will start rejecting messages with
        # blank freshnessproofs and insisting on a hash of a recent message.  This case is
        # handled (even in the current version: v0.920) with a special handler inside
        # MojoTransaction.  --Zooko 2000-09-27

        # XXXX Zooko: add the freshness challenge handler inside MojoTransaction!  --Zooko 2000-09-29

        message = MojoMessage.makeInitialMessage(msgtype=conversationtype, msgbody=firstmsgbody, recipient_id=idlib.to_binary(counterparty_id), nonce=idlib.new_random_uniq(), freshnessproof=self._map_cid_to_freshness_proof.get(counterparty_id), mymetainfo=mymetainfo)

        msgId = idlib.make_id(message, 'msg')

        # only keep track of the message details if we have a response message handler
        if outcome_func:
            # Schedule a timeout checker.
            timeoutcheckerschedtime = DoQ.doq.add_task(self.fail_conversation, kwargs={'msgId': msgId, 'failure_reason': 'timeout', 'istimeout': 1}, delay=timeout)
            self.__callback_functions[msgId] = (counterparty_id, outcome_func, notes, conversationtype, post_timeout_outcome_func, timeoutcheckerschedtime ,)

        return msgId, message

    def fail_conversation(self, msgId, failure_reason='generic failure', istimeout=0):
        initial = self.__callback_functions.get(msgId)
        if initial is None:
            # This means that a response has been received, so it shouldn't fail.
            return
        del self.__callback_functions[msgId]
        (recipient_id, callback_function, notes, conversationtype, post_timeout_callback_function, timeoutcheckerschedtime,) = initial
        if not istimeout:
            # only include these in the failed_conversation map for later calling if it was a timeout
            post_timeout_callback_function = None
        if post_timeout_callback_function is None:
            # only needed for post timeout callback functions
            post_timeout_notes = None
        else:
            post_timeout_notes = notes
        self._posttimeout_callback_functions[msgId] = (recipient_id, conversationtype, time(), post_timeout_callback_function, post_timeout_notes,)
        if DoQ.doq.is_currently_doq():
            callback_function(failure_reason=failure_reason, notes=notes)
        else:
            DoQ.doq.add_task(callback_function, kwargs = {'failure_reason': failure_reason, 'notes': notes})

    def is_unsatisfied_message(self, msgId):
        """
        @return: `true' if and only if the msg identified by `msgId' has been sent out to a
            counterparty, and it is a message to which we expect a response, and we have not
            yet received a response, and we have not yet timed out and given up hope of
            getting a response
        """
        return self.__callback_functions.has_key(msgId)

    def drop_request_state(self, firstmsgId):
        """
        cleanup all internal state about received request firstmsgId

        @precondition firstmsgId is required to be a canonical id.: idlib.is_id(firstmsgId)
        @precondition firstmsgId is required to me the id of a message about which we are currently holding state.: self._map_inmsgid_to_info.has_key(firstmsgId)
        """
        assert idlib.is_id(firstmsgId), "precondition: " + "firstmsgId is required to be a canonical id."
        assert self._map_inmsgid_to_info.has_key(firstmsgId), "precondition: " + "firstmsgId is required to me the id of a message about which we are currently holding state."

        del self._map_inmsgid_to_info[firstmsgId]

    def send_response(self, prevmsgId, msgbody, mymetainfo=None, hint=HINT_NO_HINT):
        """
        @param msgbody: the message body to be sent back

        @precondition: `prevmsgId' must be a binary id.: idlib.is_binary_id(prevmsgId): "prevmsgId: %s" % hr(prevmsgId)
        @precondition: `msgbody' must be either None or else the full msg dict, containing either a "mojo header" subdict or a "mojo message" subdict or both.: (not msgbody) or is_mojo_message(msgbody): "msgbody: %s" % hr(msgbody)
        @precondition: internal1: self._map_inmsgid_to_info.get(prevmsgId) is not None: "prevmsgId: %s" % hr(prevmsgId)
        @precondition: internal2: (type(self._map_inmsgid_to_info.get(prevmsgId)) in (types.TupleType, types.ListType)): "self._map_inmsgid_to_info.get(prevmsgId): %s :: %s" % (hr(self._map_inmsgid_to_info.get(prevmsgId)), hr(type(self._map_inmsgid_to_info.get(prevmsgId))))
        @precondition: internal3: self._map_inmsgid_to_info.get(prevmsgId)[2] == EXPECTING_RESPONSE: "self._map_inmsgid_to_info.get(prevmsgId): %s" % hr(self._map_inmsgid_to_info.get(prevmsgId))
        @precondition: internal4: idlib.is_binary_id(self._map_inmsgid_to_info.get(prevmsgId)[0]): "self._map_inmsgid_to_info.get(prevmsgId)[0]: %s :: %s" % (hr(self._map_inmsgid_to_info.get(prevmsgId)[0]), hr(type(self._map_inmsgid_to_info.get(prevmsgId)[0])))
        """
        assert idlib.is_binary_id(prevmsgId), "precondition: `prevmsgId' must be a binary id." + " -- " + "prevmsgId: %s" % hr(prevmsgId)
        assert (not msgbody) or is_mojo_message(msgbody), "precondition: `msgbody' must be either None or else the full msg dict, containing either a \"mojo header\" subdict or a \"mojo message\" subdict or both." + " -- " + "msgbody: %s" % hr(msgbody)
        assert self._map_inmsgid_to_info.get(prevmsgId) is not None, "precondition: internal1" + " -- " + "prevmsgId: %s" % hr(prevmsgId)
        assert (type(self._map_inmsgid_to_info.get(prevmsgId)) in (types.TupleType, types.ListType)), "precondition: internal2" + " -- " + "self._map_inmsgid_to_info.get(prevmsgId): %s :: %s" % (hr(self._map_inmsgid_to_info.get(prevmsgId)), hr(type(self._map_inmsgid_to_info.get(prevmsgId))))
        assert self._map_inmsgid_to_info.get(prevmsgId)[2] == EXPECTING_RESPONSE, "precondition: internal3" + " -- " + "self._map_inmsgid_to_info.get(prevmsgId): %s" % hr(self._map_inmsgid_to_info.get(prevmsgId))
        assert idlib.is_binary_id(self._map_inmsgid_to_info.get(prevmsgId)[0]), "precondition: internal4" + " -- " + "self._map_inmsgid_to_info.get(prevmsgId)[0]: %s :: %s" % (hr(self._map_inmsgid_to_info.get(prevmsgId)[0]), hr(type(self._map_inmsgid_to_info.get(prevmsgId)[0])))

        counterparty_id, inmsgtype, status = self._map_inmsgid_to_info.get(prevmsgId)
        assert idlib.is_binary_id(counterparty_id), "`counterparty_id' must be a binary id." + " -- " + "counterparty_id: %s" % hr(counterparty_id)
        self.drop_request_state(prevmsgId)

        msgstr = MojoMessage.makeResponseMessage(inmsgtype + ' response', msgbody, prevmsgId, freshnessproof=self._map_cid_to_freshness_proof.get(counterparty_id), mymetainfo=mymetainfo)
        self._MTM.send_message_with_lookup(counterparty_id, msgstr, hint=hint | HINT_THIS_IS_A_RESPONSE)

    def _process(self, msg, msgId, counterparty_id, commstrat=None):
        """
        This gets called for all incoming messages, by `handle_raw_message()'.  It verifies the
        message's integrity and either send it to a handler func to generate a response or send
        it to the appropriate callback func.

        @return: one of MojoTransaction.NO_RESPONSE,
            MojoTransaction.ASYNC_RESPONSE, or an instance of
            MojoTransaction.ResponseAndCommHints

        @raises MojoMessage.BadFormatError: if the message isn't
            properly formatted in MojoMessage format

        @precondition: `counterparty_id' must be an id.: idlib.is_sloppy_id(counterparty_id): "counterparty_id: %s" % hr(counterparty_id)

        @postcondition: Result is required to not be `None'.: result is not None: "result: %s" % hr(result)
        @postcondition: Result is required to be either MojoTransaction.NO_RESPONSE or MojoTransaction.ASYNC_RESPONSE or else an instance of MojoTransaction.ResponseAndCommHints.: (result in (MojoTransaction.NO_RESPONSE, MojoTransaction.ASYNC_RESPONSE,)) or isinstance(result, MojoTransaction.ResponseAndCommHints): "result: %s" % hr(result)
        """
        assert idlib.is_sloppy_id(counterparty_id), "precondition: `counterparty_id' must be an id." + " -- " + "counterparty_id: %s" % hr(counterparty_id)

        counterparty_id = idlib.canonicalize(counterparty_id, "broker")

        # begin DEBUG do not uncomment this in normal code
        # save all uncompressed incoming messages to unique files to be used for post analysis
        # such as real world mdecode() performance tweaking, etc.
        # (note: this writes them in the current directory, normally localweb/webroot)
        ##_dbg_fname = 'message.%05d' % self._in_message_num
        ##_dbg_f = open(_dbg_fname, 'wb')
        ##_dbg_f.write(msg)
        ##_dbg_f.close()
        ##self._in_message_num += 1  # note: python 2.0 syntax
        # end DEBUG

        reference = MojoMessage.getReference(msg)
        nonce = MojoMessage.getNonce(msg)
        recipient_id = MojoMessage.getRecipient(msg)
        senders_metainfo = MojoMessage.getSendersMetaInfo(msg)
        extra_metainfo = MojoMessage.getExtraMetaInfo(msg)

        if nonce is not None:
            # this is a first message
            if (reference is not None) or (recipient_id is None):
                debugprint("WARNING: a Mojo Message arrived with inconsistent conversation markers: nonce: %s, reference: %s, recipient_id: %s\n", args=(nonce, reference, recipient_id), v=1, vs="conversation")
                return MojoTransaction.NO_RESPONSE
            if not idlib.is_sloppy_id(nonce):
                debugprint("WARNING: a Mojo Message arrived with badly formed nonce: %s\n", args=(nonce,), v=1, vs="conversation")
                return MojoTransaction.NO_RESPONSE
            conversationtype = MojoMessage.getType(msg)

            # We now have a hint -- we're expecting to respond to this.
            if commstrat:
                commstrat.hint = commstrat.hint | HINT_EXPECT_TO_RESPOND
                commstrat.hintnumexpectedsends = commstrat.hintnumexpectedsends + 1

            if self._map_inmsgid_to_info.has_key(msgId):
                # This can only happen if we have already started processing this unique message.
                return MojoTransaction.ASYNC_RESPONSE
            self._map_inmsgid_to_info[msgId] = (counterparty_id, MojoMessage.getType(msg), EXPECTING_RESPONSE)
            # Reminder: do not somehow change this handle_initiating_message call to be on the DoQ in the future without changing
            # the MTM.__in_message_for_you logic used in fast relay to prevent nested 'message for you' messages.  -greg
            result = self._MTM.handle_initiating_message(counterparty_id, conversationtype, MojoMessage.getBody(msg), firstmsgId=msgId)
            if result is MojoTransaction.NO_RESPONSE:
                self.drop_request_state(msgId)
            if result is None:
                result = MojoTransaction.NO_RESPONSE
            if not isinstance(result, MojoTransaction.ResponseAndCommHints) and not result in (MojoTransaction.NO_RESPONSE, MojoTransaction.ASYNC_RESPONSE,):
                result = MojoTransaction.ResponseAndCommHints(result)
            postcondition((result in (MojoTransaction.NO_RESPONSE, MojoTransaction.ASYNC_RESPONSE,)) or isinstance(result, MojoTransaction.ResponseAndCommHints), "Result is required to be either MojoTransaction.NO_RESPONSE or MojoTransaction.ASYNC_RESPONSE or else an instance of MojoTransaction.ResponseAndCommHints.", result=result)

            return result
        else:
            # this is a response message
            if (reference is None) or (recipient_id is not None):
                debugprint("WARNING: a Mojo Message arrived with inconsistent conversation markers: nonce: %s, reference: %s, recipient_id: %s\n", args=(nonce, reference, recipient_id), v=1, vs="conversation")
                return MojoTransaction.NO_RESPONSE

            responsetype = MojoMessage.getType(msg)

            # Make sure that this is a response to a message that we sent, from the person to whom we sent it.
            initial = self.__callback_functions.get(reference)
            if initial is not None:
                (recipient_id, callback_function, notes, conversationtype, post_timeout_callback_function, timeoutcheckerschedtime,) = initial
                del self.__callback_functions[reference]
                DoQ.doq.remove_task(timeoutcheckerschedtime)
            else:
                # If it wasn't in the `__callback_functions' dict, it might be in the `_posttimeout_callback_functions' dict.
                recipient_id, conversationtype, msgtimeout, post_timeout_callback_function, post_timeout_notes = self._posttimeout_callback_functions.get(reference, (None, None, None, None, None,))
                if recipient_id is not None:
                    del self._posttimeout_callback_functions[reference]  # proactively clean up this cache
                if not idlib.equal(recipient_id, counterparty_id):
                    return MojoTransaction.NO_RESPONSE
                # log the late response
                if conversationtype is not None:
                    debugprint("received %s to msgId %s %s from %s %s seconds after the timeout\n", args=(responsetype, reference, conversationtype, counterparty_id, "%0.2f" % (time() - msgtimeout)), v=2, vs='Conversation')

                if post_timeout_callback_function:
                    # recipient_id and conversationtype were set above
                    callback_function = post_timeout_callback_function
                    notes = post_timeout_notes
                    debugprint("post timeout callback for response of type %s to msgId %s\n", args=(responsetype, reference,), v=5, vs='Conversation')
                else:
                    return MojoTransaction.NO_RESPONSE

            if not idlib.equal(counterparty_id, recipient_id):
                return MojoTransaction.NO_RESPONSE

            if conversationtype + ' response' != responsetype:
                debugprint("message of unexpected type %s from %s in response to a %s\n", args=(responsetype, counterparty_id, conversationtype), v=3, vs='Conversation')
                return MojoTransaction.NO_RESPONSE

            # Do hints about expecting responses...
            if commstrat:
                if (commstrat.hint & HINT_EXPECT_RESPONSE) and (commstrat.hintnumexpectedresponses > 0):
                    commstrat.hintnumexpectedresponses = commstrat.hintnumexpectedresponses - 1
                    if commstrat.hintnumexpectedresponses == 0:
                        # No longer expecting response!
                        commstrat.hint = commstrat.hint & (~ HINT_EXPECT_RESPONSE)
                    else:
                        pass

            callback_function(outcome=MojoMessage.getBody(msg), notes=notes)
            return MojoTransaction.NO_RESPONSE

    def handle_raw_message(self, counterparty_id, inmsg, commstrat=None):
        """
        This gets called for all incoming messages.  It calls `self._process()' and sends the
        response returned, if any, back to the counterparty.
        """
        counterparty_id = idlib.to_binary(counterparty_id)   # also asserts is_sloppy_id(counterparty_id)

        if commstrat:
            assert isinstance(commstrat, CommStrat.Crypto)
        elif not hasattr(self, '_complained'):
            self._complained = true
            debugprint("complaint: I wish that I had a reference to a persistent CommStrat object that represents this particular way of talking to this counterparty, so that I could use it to store hints to optimize behaviour.  Oh well.  counterparty_id: %s\n", args=(counterparty_id,), v=5, vs="debug")

        try: # for BadFormatErrors
            msgId = idlib.make_id(inmsg, 'msg')
            def debugprintreceive(counterparty_id=counterparty_id, inmsg=inmsg, msgId=msgId):
                printstr="<=== %s: %s\n"
                theseargs=[counterparty_id, inmsg]

                maxverb = debugstream.max_verbosity
                if maxverb >= 5:
                    debugprint("<=== %s: receiving: %s, %s bytes uncomp\n", args=(counterparty_id, inmsg, len(inmsg)), v=5, vs="conversation")
                elif maxverb >= 4:
                    # XXX note, this slows sending down A LOT! calling MojoMessage.getType() calls mdecode() & template check on the message.  The mdecode part is -extremely- slow (esp on big messages).  -greg 11-oct-2000
                    # if we want to display this quickly, we'll need to pass the type in from before we called mencode()
                    debugprint("<=== %s: receiving: (id: %s, type: %s, %s bytes uncomp, ...)\n", args=(counterparty_id, msgId, MojoMessage.getType(inmsg), len(inmsg)), v=4, vs="conversation") # semi-verbose
                elif maxverb >= 3:
                    debugprint("<=== %s: receiving: (id: %s, %s bytes uncomp, ...)\n", args=(counterparty_id, msgId, len(inmsg)), v=3, vs="conversation") # semi-verbose

            debugprintreceive()

            self._map_cid_to_freshness_proof[counterparty_id] = msgId

            result = self._process(inmsg, msgId, counterparty_id, commstrat)
            postcondition((result in (MojoTransaction.NO_RESPONSE, MojoTransaction.ASYNC_RESPONSE,)) or isinstance(result, MojoTransaction.ResponseAndCommHints), "Result is required to be either MojoTransaction.NO_RESPONSE or MojoTransaction.ASYNC_RESPONSE or else an instance of MojoTransaction.ResponseAndCommHints.", result=result)
            if result not in (MojoTransaction.ASYNC_RESPONSE, MojoTransaction.NO_RESPONSE):
                self.send_response(msgId, result.response, hint=result.commhints)

        except MojoMessage.BadFormatError, le:
            debugprint("_process(): BadFormatError in message from %s, msg: %s, error: %s\n", args=(counterparty_id, inmsg, le,), v=2, vs="conversation")


