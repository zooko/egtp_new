#!/usr/bin/env python

__author__   = 'EGFABT'
__revision__ = "$Id: test_tcpconnection.py,v 1.2 2003/02/28 04:35:53 artimage Exp $"

import unittest
import struct

from egtp.TCPConnection import *

class TCPConnectionTestCase(unittest.TestCase):
    def setUp(self):
        DoQ.doq = DoQ.DoQ()

    def tearDown(self):
        pass

    def test_close_on_bad_length(self, pack=struct.pack):
        outputholder = [None]
        def inmsg(tcpc, msg, outputholder=outputholder):
            outputholder[0] = msg

        t = TCPConnection(inmsg, idlib.new_random_uniq())
        msg = "hellbo"
        str = pack('>L', 2**30) + msg
        DoQ.doq.do(t._chunkify, args=(str,))
#       t._chunkify(str)
        DoQ.doq.flush()
        assert t._closing

    def test_chunkify(self):
        outputholder = [None]
        def inmsg(tcpc, msg, outputholder=outputholder):
            outputholder[0] = msg

        t = TCPConnection(inmsg, idlib.new_random_uniq())

        def help_test(msgs, iseq, t=t, outputholder=outputholder, pack=struct.pack):
            str = ''
            for msg in msgs:
                str = str + pack('>L', len(msg)) + msg
            oldi = 0
            for i in iseq:
                t._chunkify(str[oldi:i])
                oldi = i
                DoQ.doq.flush() # the upward inmsg push happens on the DoQ.
            assert outputholder[0] == msg

        msgs = ["goodbyte",]

        help_test(msgs, range(1, len(msgs[0])+5))
        help_test(msgs, range(4, len(msgs[0])+5))
        help_test(msgs, range(5, len(msgs[0])+5))

        msgs = ["hellbo", "goodbyte",]
        help_test(msgs, range(1, 23))
        help_test(msgs, (1, 5, 9, 23,))
        help_test(msgs, (4, 9, 23,))
        help_test(msgs, (11, 12, 23,))

        msgs = ["hellbo", "goodbyte", "wheedle, wordling!",]
        help_test(msgs, (10, 20, 30, 40, 50,))
        help_test(msgs, (5, 10, 20, 30, 40, 50,))
        help_test(msgs, (15, 20, 30, 40, 50,))
        help_test(msgs, (15, 17, 23, 40, 50,))



def suite():
    suite = unittest.makeSuite(TCPConnectionTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
