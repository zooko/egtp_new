#!/usr/bin/env python

#  Copyright (c) 2002 Bryce "Zooko" Wilcox-O'Hearn
#  portions Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.
#
# XXX FIXME: this unit test leaves behind permanent files in your "${EGTPDIR}/broker/mtmdb" directory.  It should be fixed to clean them up on exit.  --Zooko 2002-08-03
__cvsid = '$Id: test_system.py,v 1.1 2002/11/28 00:49:56 myers_carpenter Exp $'

# standard Python modules
import threading, types, unittest

# pyutil modules
from pyutil import DoQ
from pyutil import config
from pyutil.debugprint import debugprint
from pyutil.timeutil import timer

# (old) MN modules
from egtp import idlib

# EGTP modules
from egtp import CommStrat
from egtp import Node
from egtp.NodeMappingVerifier import NodeMappingVerifier
from egtp.TristeroLookup import TristeroLookup
from egtp import humanreadable
from egtp.interfaces import *

true = 1
false = 0

config.MAX_VERBOSITY = 1

HARDCODED_GOOD_EGTP_ADDRESS={'sequence num': 3, 'connection strategies': [{'lowerstrategy': {'IP address': '192.168.0.2', 'port number': '15233', 'comm strat sequence num': 1, 'comm strategy type': 'TCP'}, 'pubkey': {'key header': {'usage': 'only for communication security', 'type': 'public', 'cryptosystem': 'RSA'}, 'key values': {'public modulus': 'l2RaTKzSJNJyC5EpdVy1nzxW49QIetRILxilog9OgHm-LRHCMcZRstrGBKRYK_yZPJ7f9Nx9-nTLup1coWjH43R1ib16xgSZ3P2ZsWFgPC5-3nJcm1HuE0cdupMr-HY3OG2p6LP-Yywf3G6F0pPWLG8wZZICZzAXIoV2jZVspqc', 'public exponent': '3'}}, 'comm strat sequence num': 1, 'comm strategy type': 'crypto'}]}

assert (type(HARDCODED_GOOD_EGTP_ADDRESS) is types.DictType) and (HARDCODED_GOOD_EGTP_ADDRESS.has_key("connection strategies")) and (HARDCODED_GOOD_EGTP_ADDRESS.get("connection strategies", [{}])[0].has_key("pubkey")), "precondition: `HARDCODED_GOOD_EGTP_ADDRESS' must be a dict with a [\"connection strategies\"][0][\"pubkey\"] key chain." + " -- " + "HARDCODED_GOOD_EGTP_ADDRESS: %s :: %s" % (humanreadable.hr(HARDCODED_GOOD_EGTP_ADDRESS), humanreadable.hr(type(HARDCODED_GOOD_EGTP_ADDRESS)),)

class LocalLookupMan(ILookupManager):
    """ 
    a lookup man which uses only local data; In a real app you need
    remote lookup in the form of MetaTrackers, Tristero, Chord, Plex,
    Alpine, or something.
    """
    def __init__(self, verifier):
        ILookupManager.__init__(self, verifier)
        self.data = {}
    def lookup(self, key, lookuphand):
        if self.data.has_key(key):
            lookuphand.result(self.data.get(key))
        else:
            lookuphand.done(failure_reason="unexpected failure to find value in local dict")
        return # `lookup()' never returns any return value!
    def publish(self, egtpid, egtpaddr):
        """
        @precondition egtpid must be an id.: idlib.is_id(egtpid): "egtpid: %s :: %s" % (humanreadable.hr(egtpid), humanreadable.hr(type(egtpid)),)
        @precondition egtpaddr must be a dict.: type(egtpaddr) is types.DictType: "egtpaddr: %s :: %s" % (humanreadable.hr(egtpaddr), humanreadable.hr(type(egtpaddr)),)
        @precondition egtpid must match egtpaddr.: idlib.equal(egtpid, CommStrat.addr_to_id(egtpaddr)): "egtpid: %s, egtpaddr: %s" % (humanreadable.hr(egtpid), humanreadable.hr(egtpaddr), humanreadable.hr(egtpaddr.get_id(),))
        """
        assert idlib.is_id(egtpid), "precondition: egtpid must be an id." + " -- " + "egtpid: %s :: %s" % (humanreadable.hr(egtpid), humanreadable.hr(type(egtpid)),)
        assert type(egtpaddr) is types.DictType, "precondition: egtpaddr must be a dict." + " -- " + "egtpaddr: %s :: %s" % (humanreadable.hr(egtpaddr), humanreadable.hr(type(egtpaddr)),)
        assert idlib.equal(egtpid, CommStrat.addr_to_id(egtpaddr)), "precondition: egtpid must match egtpaddr." + " -- " + "egtpid: %s, egtpaddr: %s" % (humanreadable.hr(egtpid), humanreadable.hr(egtpaddr), humanreadable.hr(egtpaddr.get_id(),))

        self.data[egtpid] = egtpaddr

class LocalDiscoveryMan(IDiscoveryManager):
    """
    a discovery man which uses only local data;  In a real app you need
    distributed discovery in the form of MetaTrackers, Tristero, Plex,
    Alpine, or something.
    """
    def __init__(self):
        self.data = {}
    def discover(self, key, discoveryhand):
        discoveryhand.result(self.data.get(key))
        return # `discover()' never returns any return value!

class EGTPTestCaseTemplate(unittest.TestCase):
    def setUp(self):
        Node.init()

    def tearDown(self):
        Node.shutdown_and_block_until_finished()

    def _help_test_lookup_good_values(self, lm):
        """
        This tests registering an EGTP address with a lookup manager and then
        looking it up.

        @param lm an object that satisfies the ILookupMan interface
        """
        key = CommStrat.addr_to_id(HARDCODED_GOOD_EGTP_ADDRESS)
        lm.publish(key, HARDCODED_GOOD_EGTP_ADDRESS)

    def _help_test_lookup_bogus_values(self, lm):
        """
        This tests registering a bogus EGTP address with a lookup manager and
        then looking it up (the LookupManager fails the test if you find it!).

        @param lm an object that satisfies the ILookupMan interface
        """
        pass
       
    def _help_test_lookup_good_versus_bogus_values(self, lm):
        """
        This tests registering both a good EGTP address and a bogus one with a
        lookup manager and then looking it up (the LookupManager fails the test
        if you find the bogus one).

        @param lm an object that satisfies the ILookupMan interface
        """
        pass

    def _help_test_no_block_on_publish(self, lm):
        """
        This tests that calling `publish()' does not block, not even for a second.
        The real point is that `publish()' should not block at all, even for a microsecond, and especially not in a way that sometimes blocks for a long time (i.e. waiting for network traffic).

        @param lm an object that satisfies the ILookupMan interface
        """
        finishedflag = threading.Event()
        def doit(self=self, finishedflag=finishedflag, lm=lm):
            key = CommStrat.addr_to_id(HARDCODED_GOOD_EGTP_ADDRESS)
            lm.publish(key, HARDCODED_GOOD_EGTP_ADDRESS)
            finishedflag.set()
        t = threading.Thread(target=doit)
        t.start()
        TIMELIMIT=1.0
        finishedflag.wait(TIMELIMIT)
        self.failUnless(finishedflag.isSet(), "didn't return from a call to `publish()' within limit of %s seconds" % TIMELIMIT)

    def _help_test_EGTP_send_and_receive(self, lm):
        """
        This tests sending an EGTP message from one Node to another, and sending
        back a response.  Uses a LookupManager.

        @param lm an object that satisfies the ILookupMan interface
        """
        dm = LocalDiscoveryMan()
        finishedflag = threading.Event()
        d={}
        def setup(finishedflag=finishedflag, d=d, self=self, lm=lm, dm=dm):
            start = timer.time()

            # Make a listener.  He will announce his EGTP address to the lookupman `lm'.
            d['n1'] = Node.Node(allownonrouteableip=true, lookupman=lm, discoveryman=dm, datadir="/tmp/egtp_test")

            # Set a handler func: if any messages come in with message type "ping", the EGTP Node will call this function.
            def l_ping_handler(sender, msg, finishedflag=finishedflag, start=start, self=self):
                debugprint("%s(): passed in %s seconds: Got a message from %s.  The message says: %s\n", args=(self.__class__.__name__, "%0.1f" % (timer.time() - start), sender, msg,), v=0)
                finishedflag.set()

            d['n1'].set_handler_func(mtype="ping", handler_func=l_ping_handler)
            # print "EGTPunittest: get_address", d['n1'].get_address()

            # Make a sender.  He'll keep a reference to `lm' for later use.
            d['n2'] = Node.Node(allownonrouteableip=true, lookupman=lm, discoveryman=dm, datadir="/tmp/egtp_test")

        DoQ.doq.do(setup)

        # Have the second node ping the first, using only the first's id.
        try:
            d['n2'].send(CommStrat.addr_to_id(d['n1'].get_address()), mtype="ping", msg="hello there, you crazy listener!")
        except exceptions.StandardError, le:
            debugprint("le: %s\n", args=(le,))
            raise le

        # Now block until it works or times out.
        TIMEOUTLIMIT = 60
        finishedflag.wait(TIMEOUTLIMIT )
        self.failUnless(finishedflag.isSet(), "didn't complete within timeout limit of %s seconds" % TIMEOUTLIMIT)

class LocalTest(EGTPTestCaseTemplate):
    def test_local_no_block_on_publish(self):
        self._help_test_no_block_on_publish(LocalLookupMan(NodeMappingVerifier()))

    def test_local_send_and_receive(self):
        self._help_test_EGTP_send_and_receive(LocalLookupMan(NodeMappingVerifier()))

class TristeroTest(EGTPTestCaseTemplate):
    def test_tristero_no_block_on_construct(self):
        """ 
        This tests that calling `TristeroLookup()' does not block, not
        even for a second.  
        
        The real point is that `TristeroLookup()' should not block at all,
        even for a microsecond, and especially not in a way that sometimes
        blocks for a long time (i.e. waiting for network traffic).  
        """
        finishedflag = threading.Event() 
        def doit(finishedflag=finishedflag):
            TristeroLookup(NodeMappingVerifier(), "http://fnordovax.dyndns.org:10805")
            finishedflag.set()
        t = threading.Thread(target=doit)
        t.start()
        TIMELIMIT=1.0
        finishedflag.wait(TIMELIMIT)
        self.failUnless(finishedflag.isSet(), "didn't return from a call to `TristeroLookup()' within limit of %s seconds" % TIMELIMIT)

    def test_tristero_no_block_on_publish(self):
        self._help_test_no_block_on_publish(TristeroLookup(NodeMappingVerifier(), "http://fnordovax.dyndns.org:10805"))

    def test_tristero_send_and_receive(self):
        self._help_test_EGTP_send_and_receive(TristeroLookup(NodeMappingVerifier(), "http://fnordovax.dyndns.org:10805"))



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LocalTest, 'test'))
    ## commenting out the Tristero tests because we don't have a Tristero server component useful for doing unit tests (i.e., tests that don't require any other manual setup by the human tester, and that don't give failures when there are problems such as networking outages that are unrelated to the source code being tested.  --Zooko 2002-04-21
    ## suite.addTest(unittest.makeSuite(TristeroTest, 'test')

    return suite

if __name__ == '__main__':
    unittest.main()
