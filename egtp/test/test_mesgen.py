#!/usr/bin/env python

__author__   = 'EGFABT'
__revision__ = "$Id: test_mesgen.py,v 1.3 2002/12/31 06:05:00 myers_carpenter Exp $"

import unittest, tempfile, os, shutil, time

# this is for a disabled test that I don't think we need -- icepick 2002-12-02
import threading

# module we are testing
from egtp import mesgen

# other egtp modules
from egtp import idlib

class MesgenTestCase(unittest.TestCase):
    def setUp(self):
        self.testdir = tempfile.mktemp('egtp_test_mesgen')

    def tearDown(self):
        if os.path.isdir(self.testdir):
            shutil.rmtree(self.testdir)
        
    def _createMessageMaker(self):
        return mesgen.create_MessageMaker(self.testdir)

    def _loadMessageMaker(self, id):
        myid_aa = idlib.to_mojosixbit(id)
        dir = os.path.normpath(os.path.join(self.testdir, myid_aa))
        return mesgen.load_MessageMaker(dir)

    def testNormalOperation(self):
        mesgen1 = self._createMessageMaker()
        mesgen2 = self._createMessageMaker()
        id1 = mesgen1.get_id()
        id2 = mesgen2.get_id()
        key1 = mesgen1.get_public_key()
        key2 = mesgen2.get_public_key()
        mesgen1.store_key(key2)
        m1 = mesgen1.generate_message(id2, 'spam1')
        m2 = mesgen1.generate_message(id2, 'spam2')
        counterparty_pub_key_sexp, message = mesgen2.parse(m2)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id1)
        assert message == 'spam2'
        counterparty_pub_key_sexp, message = mesgen2.parse(m1)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id1)
        assert message == 'spam1'
        m3 = mesgen2.generate_message(id1, 'spam3')
        counterparty_pub_key_sexp, message = mesgen1.parse(m3)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id2)
        assert message == 'spam3'

        # check to see that header is not on later messages
        m1a = mesgen1.generate_message(id2, 'spam1')
        assert len(m1a) < len(m1)
        m2a = mesgen1.generate_message(id2, 'spam2')
        assert len(m2a) < len(m2)


    def testNormalOperationWithReconstruction(self):
        mesgen1 = self._createMessageMaker()
        mesgen2 = self._createMessageMaker()
        id1 = mesgen1.get_id()
        id2 = mesgen2.get_id()
        key1 = mesgen1.get_public_key()
        key2 = mesgen2.get_public_key()
        mesgen1.store_key(key2)
        m1 = mesgen1.generate_message(id2, 'spam1')
        m2 = mesgen1.generate_message(id2, 'spam2')
        counterparty_pub_key_sexp, message = mesgen2.parse(m2)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id1)
        assert message == 'spam2'
        counterparty_pub_key_sexp, message = mesgen2.parse(m1)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id1)
        assert message == 'spam1'
        m3 = mesgen2.generate_message(id1, 'spam3')
        counterparty_pub_key_sexp, message = mesgen1.parse(m3)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id2)
        assert message == 'spam3'
        # check to see that header is not on later messages
        m1a = mesgen1.generate_message(id2, 'spam1')
        assert len(m1a) != len(m1)
        m2a = mesgen1.generate_message(id2, 'spam2')
        assert len(m2a) != len(m2)
        del mesgen1
        del mesgen2

        mesgen1 = self._loadMessageMaker(id1)
        mesgen2 = self._loadMessageMaker(id2)
        mesgen1.store_key(key2)
        m1 = mesgen1.generate_message(id2, 'spam1')
        m2 = mesgen1.generate_message(id2, 'spam2')
        counterparty_pub_key_sexp, message = mesgen2.parse(m2)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id1)
        assert message == 'spam2'
        counterparty_pub_key_sexp, message = mesgen2.parse(m1)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id1)
        assert message == 'spam1'
        m3 = mesgen2.generate_message(id1, 'spam3')
        counterparty_pub_key_sexp, message = mesgen1.parse(m3)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id2)
        assert message == 'spam3'
        m1a = mesgen1.generate_message(id2, 'spam1')
        assert len(m1a) == len(m1)
        m2a = mesgen1.generate_message(id2, 'spam2')
        assert len(m2a) == len(m2)

    def testInterlock(self):
        mesgen1 = self._createMessageMaker()
        mesgen2 = self._createMessageMaker()
        id1 = mesgen1.get_id()
        id2 = mesgen2.get_id()
        key1 = mesgen1.get_public_key()
        key2 = mesgen2.get_public_key()
        mesgen1.store_key(key2)
        mesgen2.store_key(key1)
        m1 = mesgen1.generate_message(id2, 'spam1')
        m2 = mesgen2.generate_message(id1, 'spam2')
        counterparty_pub_key_sexp, message = mesgen2.parse(m1)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id1)
        assert message == 'spam1'
        counterparty_pub_key_sexp, message = mesgen1.parse(m2)
        assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id2)
        assert message == 'spam2'

    def testSendSelf(self):
        mesgen = self._createMessageMaker()
        x = mesgen.generate_message(mesgen.get_id(), 'spam')
        pub_key_sexp, message = mesgen.parse(x)
        assert idlib.equal(idlib.make_id(pub_key_sexp, 'broker'), mesgen.get_id())
        assert message == 'spam'

    def testError(self):
        mesgenobj = self._createMessageMaker()
        x = mesgenobj.generate_message(mesgenobj.get_id(), 'spam')
        def tryToRaiseError(mesgenobj=mesgenobj, x=x):
            mesgenobj.parse(x + 'uh')
        self.failUnlessRaises(mesgen.Error, tryToRaiseError)

    def testSerializeAndReserialize(self):
        sk = mesgen.SessionKeeper(dbparentdir=self.testdir, dir=None)

        id = sk.get_id()
        key = sk.get_public_key()

        del sk

        dir = os.path.normpath(os.path.join(self.testdir, idlib.to_mojosixbit(id)))
        
        sk2 = mesgen.SessionKeeper(dbparentdir=None, dir=dir)

        assert sk2.get_public_key() == key

    def testMesgenSpeed(self, iterations=200):
        # "200 loop iterations generating and parsing 3 messages each took 2.26 seconds" -greg 2001-05-31 [333Mhz Celeron]
        mesgen1 = self._createMessageMaker()
        mesgen2 = self._createMessageMaker()
        id1 = mesgen1.get_id()
        id2 = mesgen2.get_id()
        key1 = mesgen1.get_public_key()
        key2 = mesgen2.get_public_key()
        mesgen1.store_key(key2)

        start_time = time.time()
        for x in xrange(iterations):
            m1 = mesgen1.generate_message(id2, 'spam1')
            m2 = mesgen1.generate_message(id2, 'spam2')
            counterparty_pub_key_sexp, message = mesgen2.parse(m2)
            assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id1)
            assert message == 'spam2'
            counterparty_pub_key_sexp, message = mesgen2.parse(m1)
            assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id1)
            assert message == 'spam1'
            m3 = mesgen2.generate_message(id1, 'spam3')
            counterparty_pub_key_sexp, message = mesgen1.parse(m3)
            assert idlib.equal(idlib.make_id(counterparty_pub_key_sexp, 'broker'), id2)
            assert message == 'spam3'
        stop_time = time.time()
        print "%d loop iterations generating and parsing 3 messages each took %3.2f seconds" % (iterations, stop_time-start_time)

    def disabled_testSendTwoMessagesAtOnce(self):
        """
        disabled becase we don't do multithreading mesgen for now
        
        will we ever?  -- icepick 2002-12-02
        """
        mesgen1 = self._createMessageMaker()
        mesgen2 = self._createMessageMaker()
        id1 = mesgen1.get_id()
        id2 = mesgen2.get_id()
        key1 = mesgen1.get_public_key()
        key2 = mesgen2.get_public_key()
        
        prestart1 = threading.Event()
        start1 = threading.Event()
        flag1 = threading.Event()
        def store_key1(start = start1, mesgen1 = mesgen1, key2 = key2, flag = flag1, prestart1=prestart1):
            prestart1.set()
            start.wait()
            mesgen1.store_key(key2)
            flag.set()
        prestart2 = threading.Event()
        flag2 = threading.Event()
        def store_key2(start = start1, mesgen1 = mesgen1, key2 = key2, flag = flag2, prestart2=prestart2):
            prestart2.set()
            start.wait()
            mesgen1.store_key(key2)
            flag.set()
        threading.Thread(target = store_key1).start()
        threading.Thread(target = store_key2).start()
        prestart1.wait()
        prestart2.wait()
        start1.set()
        flag1.wait(2)
        assert flag1.isSet()
        flag2.wait(2)
        assert flag2.isSet()

        m1holder = []
        m2holder = []
        start2 = threading.Event()
        flag3 = threading.Event()
        flag4 = threading.Event()
        def make_message1(start = start2, m1holder = m1holder, mesgen1 = mesgen1, id2 = id2, flag = flag3):
            start.wait()
            m1holder.append(mesgen1.generate_message(id2, 'spam'))
            flag.set()
        def make_message2(start = start2, m2holder = m2holder, mesgen1 = mesgen1, id2 = id2, flag = flag4):
            start.wait()
            m2holder.append(mesgen1.generate_message(id2, 'spam'))
            flag.set()
        threading.Thread(target = make_message1).start()
        threading.Thread(target = make_message2).start()
        xxx(time.sleep(1))
        start2.set()
        flag3.wait(2)
        assert flag3.isSet()
        assert len(m1holder) == 1
        flag4.wait(2)
        assert flag4.isSet()
        assert len(m2holder) == 1

        start3 = threading.Event()
        flag5 = threading.Event()
        flag6 = threading.Event()
        parseflag = threading.Event()
        def parse1(mesgen2 = mesgen2, wiremessage = m1holder[0], id1 = id1, flag = flag5, 
                parseflag = parseflag, start = start3):
            start.wait()
            counterparty_id, message = mesgen2.parse(wiremessage)
            assert idlib.is_sloppy_id(counterparty_id), "`counterparty_id' must be  an id." + " -- " + "id: %s" % hr(id)
            counterparty_id = idlib.canonicalize(counterparty_id, 'broker')
            if not idlib.equal(counterparty_id, id1) or (message != 'spam'):
                parseflag.set()
            flag.set()
        def parse2(mesgen2 = mesgen2, wiremessage = m2holder[0], id1 = id1, flag = flag6, 
                parseflag = parseflag, start = start3):
            start.wait()
            counterparty_id, message = mesgen2.parse(wiremessage)
            assert idlib.is_sloppy_id(counterparty_id), "`counterparty_id' must be  an id." + " -- " + "id: %s" % hr(id)
            counterparty_id = idlib.canonicalize(counterparty_id, 'broker')
            if not equal(counterparty_id, id1) or (message != 'spam'):
                parseflag.set()
            flag.set()
        threading.Thread(target = parse1).start()
        threading.Thread(target = parse2).start()
        xxx(time.sleep(1))
        start3.set()
        flag5.wait(2)
        assert flag5.isSet()
        assert not parseflag.isSet()
        flag6.wait(2)
        assert flag6.isSet()
        assert not parseflag.isSet()

        m3 = mesgen1
        mesgen1 = mesgen2
        mesgen2 = m3
        i3 = id1
        id1 = id2
        id2 = i3
        k3 = key1
        key1 = key2
        key2 = k3

        m1holder = []
        m2holder = []
        start2 = threading.Event()
        flag3 = threading.Event()
        flag4 = threading.Event()
        def make_message1(start = start2, m1holder = m1holder, mesgen1 = mesgen1, id2 = id2, flag = flag3):
            start.wait()
            m1holder.append(mesgen1.generate_message(id2, 'spam'))
            flag.set()
        def make_message2(start = start2, m2holder = m2holder, mesgen1 = mesgen1, id2 = id2, flag = flag4):
            start.wait()
            m2holder.append(mesgen1.generate_message(id2, 'spam'))
            flag.set()
        threading.Thread(target = make_message1).start()
        threading.Thread(target = make_message2).start()
        xxx(time.sleep(1))
        start2.set()
        flag3.wait(2)
        assert flag3.isSet()
        assert len(m1holder) == 1
        flag4.wait(2)
        assert flag4.isSet()
        assert len(m2holder) == 1

        start3 = threading.Event()
        flag5 = threading.Event()
        flag6 = threading.Event()
        parseflag = threading.Event()
        def parse1(mesgen2 = mesgen2, wiremessage = m1holder[0], id1 = id1, flag = flag5, 
                parseflag = parseflag, start = start3):
            start.wait()
            counterparty_id, message = mesgen2.parse(wiremessage)
            if counterparty_id != id1 or message != 'spam':
                parseflag.set()
            flag.set()
        def parse2(mesgen2 = mesgen2, wiremessage = m2holder[0], id1 = id1, flag = flag6, 
                parseflag = parseflag, start = start3):
            start.wait()
            counterparty_id, message = mesgen2.parse(wiremessage)
            if counterparty_id != id1 or message != 'spam':
                parseflag.set()
            flag.set()
        threading.Thread(target = parse1).start()
        threading.Thread(target = parse2).start()
        xxx(time. sleep(1))
        start3.set()
        flag5.wait(2)
        assert flag5.isSet()
        assert not parseflag.isSet()
        flag6.wait(2)
        assert flag6.isSet()
        assert not parseflag.isSet()



def suite():
    suite = unittest.makeSuite(MesgenTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
