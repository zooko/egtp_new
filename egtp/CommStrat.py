#  Copyright (c) 2001 Autonomous Zone Industries
#  Copyright (c) 2002 Bryce "Zooko" Wilcox-O'Hearn
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__version__ = "$Revision: 1.19 $"
# $Source: /home/zooko/playground/egtp_new/rescue-party/gw/../egtp_new/egtp_new/egtp/CommStrat.py,v $

True = 1 == 1
False = 0 == 1

# Python Standard Library modules
import exceptions, string, types
import traceback # actually just for debugging
import types
import string

# pyutil modules
from pyutil.assertutil import _assert, precondition, postcondition
from pyutil.config import DEBUG_MODE
from pyutil.debugprint import debugprint, debugstream
from pyutil.humanreadable import hr

# egtp modules
from egtp import DataTypes, MojoMessage, OurMessages, TCPConnection, idlib, ipaddresslib, keyutil, mencode
from egtp.CommHints import HINT_EXPECT_RESPONSE, HINT_EXPECT_MORE_TRANSACTIONS, HINT_EXPECT_NO_MORE_COMMS, HINT_NO_HINT
from egtp.DataTypes import UNIQUE_ID, ANY, ASCII_ARMORED_DATA, NON_NEGATIVE_INTEGER, MOD_VAL, INTEGER, ListMarker, OptionMarker
from egtp.OurMessagesCommStrat import *
from egtp.crypto import modval

from egtp.CommHints import HINT_EXPECT_RESPONSE, HINT_EXPECT_MORE_TRANSACTIONS, HINT_EXPECT_NO_MORE_COMMS, HINT_NO_HINT


class Error(exceptions.StandardError): pass
class UnsupportedTypeError(exceptions.StandardError): pass


"""
TCP(host, port, asyncsock) - a strategy for opening tcp connections or else using a currently open tcp socket

Relay(relay_server) - makes a strategy which routes through the given relay server

Crypto(pubkey, lowerstrategy) - a combination of a pub key and another strategy for transmitting ciphertext

Pickup() - if you have a message for this person, store it and she will contact you and pick it up;  Relay servers use a Pickup strategy to give messages to their clients currently.  (Not really -- they currently implement pickup behavior in RelayServerHandlers.py, but perhaps it would be cleaner if they used Pickup ?  --Zooko 2001-09-02)
"""

def choose_best_strategy(cs1, cs2):
    """
    You should pass the newer, or most recently "suggested" cs as `cs2'.  If there is a tie we will prefer that one.
    (But if they are the *same*, we will prefer the old one.  For example, if the two strategies both use the same
    crypto key and they each have an open TCP connection, then there is a *tie* in terms of which one is
    preferred, so we use the newly suggested one.  If two strategies both use the same crypto key and they both
    use the *same* open TCP connection, then they are the *same* and we keep using the current one.)

    @param cs1: an instance of CommStrat; Can be `None'.
    @param cs2: an instance of CommStrat; Can be `None'.

    @return: a reference to whichever of `cs1' or `cs2' is most preferable
    """
    # If either one is `None' then we prefer the other.
    if cs1 is None:
        return cs2
    if cs2 is None:
        return cs1

    # If they are the same then we prefer the current one.
    if cs1.same(cs2):
        return cs1

    # We always prefer open TCP sockets over anything else...
    if (isinstance(cs1, TCP) and cs1.is_open_socket()) and not (isinstance(cs2, TCP) and cs2.is_open_socket()):
        return cs1
    if (isinstance(cs2, TCP) and cs2.is_open_socket()) and not (isinstance(cs1, TCP) and cs1.is_open_socket()):
        return cs2

    # If neither is an open TCP socket, or if both are open TCP sockets (== if control reaches this line), then we always prefer a newer sequence number over and older or a None:
    cs1seqno = cs1._commstratseqno
    if cs1seqno is None:
        cs1seqno = -1
    cs2seqno = cs2._commstratseqno
    if cs2seqno is None:
        cs1seqno = -1
    if cs1seqno > cs2seqno:
        return cs1
    elif cs2seqno > cs1seqno:
        return cs2

    # We always prefer TCP over non-TCP...
    if isinstance(cs1, TCP) and not isinstance(cs2, TCP):
        return cs1
    if isinstance(cs2, TCP) and not isinstance(cs1, TCP):
        return cs2

    if isinstance(cs1, TCP):
        # Note: if control reaches here then both strats are TCP.
        # Among non-same open sockets with tieing commstratseqno, we prefer the newer one (sort of arbitrary).
        if cs1.is_open_socket():
            # Note: if control reaches here then both strats are open TCP connections.
            return cs2

        # Among IP addresses, we definitely prefer routeable ones...
        if cs1.is_routeable() and not cs2.is_routeable():
            return cs1
        if cs2.is_routeable() and not cs1.is_routeable():
            return cs2

        # Among non-same, similarly-routeable IP addresses with tieing commstratseqno, we prefer the newer one (sort of arbitrary).
        return cs2

    # Note: if control reaches here then neither strat is a TCP.
    # We always prefer Relay over "none of the above":
    if isinstance(cs1, Relay) and not isinstance(cs2, Relay):
        return cs1
    if isinstance(cs2, Relay) and not isinstance(cs1, Relay):
        return cs2

    # Among non-same Relays with the same (or unknown) commstratseqno, we prefer the newer one (sort of arbitrary):
    # Note, it would be nice to check if we have an open TCP connection to one of the relay servers, and
    # if so prefer that Relay strat.  Also it might be nice to actually handicap the Relay servers here.
    return cs2

class CommStrat:
    def __init__(self, broker_id=None, commstratseqno=None):
        """
        @precondition: broker_id must be None or an id.: (broker_id is None) or (idlib.is_id(broker_id))
        """
        precondition ((broker_id is None) or (idlib.is_id(broker_id)), "broker_id must be None or an id.", broker_id=broker_id)

        self.hint = HINT_NO_HINT
        self.hintnumexpectedresponses = 0
        self.hintnumexpectedsends = 0
        self._commstratseqno = commstratseqno
        self._broker_id = broker_id 

    def to_dict(self):
        d = {}
        if self._broker_id is not None:
            d['broker id'] = self._broker_id
        if self._commstratseqno is not None:
            d['comm strat sequence num'] = self._commstratseqno
        return d

    def get_id(self):
        return self._broker_id

class Kademlia(CommStrat.CommStat):
    def __init__(self, kademnode, broker_id):
        CommStrat.__init__(self, broker_id)
        self._kademnode = kademnode

    def send(self, msg):
        """
        @precondition: self._broker_id must be an id.: idlib.is_id(self._broker_id)
        """
        precondition(idlib.is_id(self._broker_id), "self._broker_id must be an id.", broker_id=self._broker_id)
        self._kademnode.send(self._broker_id, msg)

class TCP(CommStrat):
    def __init__(self, tcpch, broker_id, host=None, port=None, asyncsock=None, commstratseqno=None):
        """
        @param tcpch: the TCPCommsHandler
        @param asyncsock: an instance of TCPConnection

        @precondition: asyncsock must be an instance of TCPConnection or nothing.: (asyncsock is None) or isinstance(asyncsock, TCPConnection.TCPConnection)
        @precondition: broker_id must be an id or None.: (broker_id is None) or idlib.is_id(broker_id)
        """
        precondition((asyncsock is None) or isinstance(asyncsock, TCPConnection.TCPConnection), "asyncsock must be an instance of TCPConnection or nothing.", asyncsock=asyncsock)
        precondition((broker_id is None) or idlib.is_id(broker_id), "broker_id must be an id or None.", broker_id=broker_id)

        CommStrat.__init__(self, broker_id, commstratseqno=commstratseqno)

        self._tcpch = tcpch
        self.host = host
        self.port = port
        self.asyncsock = asyncsock
   
    def __repr__(self):
        return '<%s to %s:%s via %s, %x>' % (self.__class__.__name__, self.host, self.port, self.asyncsock, id(self),)

    def send(self, msg, hint=HINT_NO_HINT, fast_fail_handler=None, timeout=None, commstratseqno=None):
        """
        @precondition: self._broker_id must be an id.: idlib.is_id(self._broker_id)
        """
        precondition(idlib.is_id(self._broker_id), "self._broker_id must be an id.", broker_id=self._broker_id)

        # debugprint("%s.send(): self._broker_id: %s\n", args=(self, self._broker_id,))
        self._tcpch.send_msg(self._broker_id, msg=msg, hint=hint, fast_fail_handler=fast_fail_handler)

    def is_routeable(self):
        return self.host and ipaddresslib.is_routable(self.host)

    def is_open_socket(self):
        return (self.asyncsock) and not self.asyncsock._closing

    def same(self, other):
        """
        Two TCP's are same iff they both have the same non-None socket object or if they both have None socket objects and the same host and port

        @return: `true' iff `self' and `other' are actually the same strategy
        """
        if not hasattr(other, 'asyncsock'):
            # `other' is not a CommStrat.TCP
            assert hasattr(self, 'asyncsock'), "self is required to be a CommStrat.TCP. self: %s :: %s" % tuple(map(hr, (self, type(self),)))
            return false
        if self.asyncsock is not None:
            return self.asyncsock is other.asyncsock
        else:
            if other.asyncsock is not None:
                return false
        if not hasattr(other, 'host'):
            # `other' is not a CommStrat.TCP
            assert hasattr(self, 'host'), "self is required to be a CommStrat.TCP. self: %s :: %s" % tuple(map(hr, (self, type(self),)))
            return false
        if not hasattr(other, 'port'):
            # `other' is not a CommStrat.TCP
            assert hasattr(self, 'port'), "self is required to be a CommStrat.TCP. self: %s :: %s" % tuple(map(hr, (self, type(self),)))
            return false
        return (self.host == other.host) and (self.port == other.port)

    def to_dict(self):
        d = CommStrat.to_dict(self)

        d['comm strategy type'] = "TCP"

        if self.host:
            d['IP address'] = self.host

        if self.port:
            d['port number'] = `self.port`

        if self.asyncsock:
            d['open connection'] = 'true'
            
            try:
                peername = self.asyncsock.getpeername()
                d['open connection peername'] = `peername`
            except:
                pass

        return d

class Crypto(CommStrat):
    def __init__(self, pubkey, lowerstrategy, broker_id=None):
        """
        @param lowerstrategy: the lower-level comms strategy, either given
            by meta-tracking or suggested by the way that the last message
            arrived (e.g. For TCP, the suggested strategy is to send a
            message back down the connection over which the last message
            arrived.)

        @precondition: pubkey must be a well-formed keyutil.: keyutil.publicKeyForCommunicationSecurityIsWellFormed(pubkey)
        @precondition: lowerstrategy must be a CommStrat.: isinstance(lowerstrategy, CommStrat)
        @precondition: broker_id must be the id of pubkey, or else it must be None.: (broker_id is None) or (idlib.equal(idlib.make_id(pubkey, 'broker'), broker_id))
        """
        precondition(keyutil.publicKeyForCommunicationSecurityIsWellFormed(pubkey), "pubkey must be a well-formed keyutil.", pubkey=pubkey)
        precondition(isinstance(lowerstrategy, CommStrat), "lowerstrategy must be a CommStrat.", lowerstrategy=lowerstrategy)
        precondition((broker_id is None) or (idlib.equal(idlib.make_id(pubkey, 'broker'), broker_id)), "broker_id must be the id of pubkey, or else it must be `None'.", broker_id=broker_id)

        CommStrat.__init__(self, idlib.make_id(pubkey, 'broker'))

        self._pubkey = pubkey
        self._lowerstrategy = lowerstrategy

    def __repr__(self):
        return '<%s pubkey_id %s at %x, lowerstrategy: %s>' % (self.__class__.__name__, idlib.to_ascii(idlib.make_id(self._pubkey)), id(self), self._lowerstrategy)

    def same(self, other):
        """
        Two Crypto's are same iff they have the same pub key and their lowerstrategies are same.

        @return: `true' iff `self' and `other' are actually the same strategy
        """
        # debugprint("%s.same(%s); stack: %s\n", args=(self, other, traceback.extract_stack(),))
        if not hasattr(other, '_pubkey'):
            assert hasattr(self, '_pubkey')
            return false
        if self._pubkey != other._pubkey:
            return false
        assert hasattr(self, '_lowerstrategy')
        if not hasattr(other, '_lowerstrategy'):
            return false
        return self._lowerstrategy.same(other._lowerstrategy)

    def to_dict(self):
        d = CommStrat.to_dict(self)
        d['comm strategy type'] = "crypto" # XXXX This should be changed to "Crypto" to match the name of the class.  --Zooko 2000-08-02
        d['pubkey'] = mencode.mdecode(self._pubkey)
        d['lowerstrategy'] = self._lowerstrategy.to_dict()
        return d

class Pickup(CommStrat):
    def __init__(self, broker_id=None, commstratseqno=None):
        CommStrat.__init__(self, broker_id, commstratseqno=commstratseqno)
        return

    def to_dict(self):
        d = CommStrat.to_dict(self)
        d['comm strategy type'] = "pickup" # XXXX This should be changed to "Pickup" to match the name of the class.  --Zooko 2000-08-02
        return d

    def same(self, other):
        """
        Two Pickup's are always the same.

        @return: `true' iff `self' and `other' are actually the same strategy
        """
        return isinstance(other, Pickup)

def dict_to_type(dict):
    return dict['comm strategy type']

def crypto_dict_to_pub_key(dict):
    return mencode.mencode(dict['pubkey'])

def crypto_dict_to_id(adict):
    """
    @precondition: adict is required to be a dict.: isinstance(adict, dict)
    """
    precondition(isinstance(adict, dict), "adict is required to be a dict.", adict=adict)

    return idlib.make_id(mencode.mencode(adict['pubkey']), 'broker')

def addr_to_id(addr):
    """
    @deprecated in the new Kademlia comms system?
    @precondition: `addr' must be a dict with a ["connection strategies"][0]["pubkey"] key chain, or else a CommStrat instance with a broker_id.: ((type(addr) is types.DictType) and (addr.has_key("connection strategies")) and (addr.get("connection strategies", [{}])[0].has_key("pubkey"))) or ((type(addr) is types.InstanceType) and (isinstance(addr, CommStrat)) and (addr._broker_id is not None)): "addr: %s :: %s" % tuple(map(humanreadable.hr, (addr, type(addr),)))
    """
    assert ((type(addr) is types.DictType) and (addr.has_key("connection strategies")) and (addr.get("connection strategies", [{}])[0].has_key("pubkey"))) or ((type(addr) is types.InstanceType) and (isinstance(addr, CommStrat)) and (addr._broker_id is not None)), "precondition: `addr' must be a dict with a [\"connection strategies\"][0][\"pubkey\"] key chain, or else a CommStrat instance with a broker_id." + " -- " + "addr: %s :: %s" % tuple(map(humanreadable.hr, (addr, type(addr),)))

    if type(addr) is types.DictType:
        return idlib.make_id(mencode.mencode(addr["connection strategies"][0]['pubkey']), 'broker')
    else:
        return addr.get_id()

def dict_to_strategy(dict, mtm, broker_id=None, commstratseqno=None):
    """
    @raises UnsupportedTypeError: if `dict' is not either a TCP, Relay, Crypto, or Pickup
    
    @precondition: broker_id must be an id or None.: (broker_id is None) or (idlib.is_id(broker_id))
    """
    precondition ((broker_id is None) or (idlib.is_sloppy_id(broker_id)), "broker_id must be an id or None.", broker_id=broker_id)

    if not (dict.get('comm strategy type') in ("TCP", "relay", "Relay", "crypto", "Crypto", "pickup", "Pickup",)):
        raise UnsupportedTypeError, "dict must be either a TCP, Relay, Crypto or Pickup." + " -- " + "dict: %s" % humanreadable.hr(dict)

    dictbroker_id = dict.get('broker id')
    if (broker_id is not None) and (dictbroker_id is not None):
        assert idlib.equal(broker_id, dictbroker_id)
    if broker_id is None:
        broker_id = dictbroker_id

    if dict.get('comm strat sequence num') is not None:
        try:
            DataTypes.check_template(dict.get('comm strat sequence num'), DataTypes.INTEGER)
        except DataTypes.BadFormatError, le:
            raise DataTypes.BadFormatError, { 'cause': le, 'explanation': "comm strat sequence number is not an INTEGER", 'comm strat sequence number': dict.get('comm strat sequence num'), 'dict': dict, }
        commstratseqno = dict.get('comm strat sequence num')

    cst = dict['comm strategy type']
    if cst == "TCP":
        try:
            DataTypes.check_template(dict, TCP_COMM_STRAT_TEMPL)
        except DataTypes.BadFormatError, le:
            raise DataTypes.BadFormatError, { 'cause': le, 'explanation': "dict is not a TCP_COMM_STRAT_TEMPL", 'dict': dict, }
        return TCP(mtm._ch._tcpch, broker_id, host=dict['IP address'], port=int(dict['port number']), commstratseqno=commstratseqno)

    if (cst == "Relay") or (cst == "relay"):
        try:
            DataTypes.check_template(dict, RELAY_COMM_STRAT_TEMPL)
        except DataTypes.BadFormatError, le:
            raise DataTypes.BadFormatError, { 'cause': le, 'explanation': "dict is not a RELAY_COMM_STRAT_TEMPL", 'dict': dict, }
        return Relay(relayer_id=dict['relayer id'], mtm=mtm, broker_id=broker_id, commstratseqno=commstratseqno)

    if (cst == "Pickup") or (cst == "pickup"):
        try:
            DataTypes.check_template(dict, PICKUP_COMM_STRAT_TEMPL)
        except DataTypes.BadFormatError, le:
            raise DataTypes.BadFormatError, { 'cause': le, 'explanation': "dict is not a PICKUP_COMM_STRAT_TEMPL", 'dict': dict, }
        return Pickup(broker_id=broker_id, commstratseqno=commstratseqno)

    if (cst == "Crypto") or (cst == "crypto"):
        encodedbrokerId = dict.get('lowerstrategy', {}).get('broker id')
        if (encodedbrokerId is not None) and not idlib.is_sloppy_id(encodedbrokerId):
            raise DataTypes.BadFormatError, { 'explanation': "dict has an invalid broker id in lowerstrategy", "dict.get('lowerstrategy')": dict.get('lowerstrategy'), "dict.get('lowerstrategy', {}).get('broker id')": dict.get('lowerstrategy', {}).get('broker id'), 'dict': dict, }
        try:
            DataTypes.check_template(dict, CRYPTO_COMM_STRAT_TEMPL)
        except DataTypes.BadFormatError, le:
            raise DataTypes.BadFormatError, { 'cause': le, 'explanation': "dict is not a CRYPT_COMM_STRAT_TEMPL", 'dict': dict, }
        if broker_id is None:
            broker_id = crypto_dict_to_id(dict)
        return Crypto(mencode.mencode(dict['pubkey']), dict_to_strategy(dict['lowerstrategy'], broker_id=broker_id, mtm=mtm, commstratseqno=commstratseqno), broker_id=broker_id)
