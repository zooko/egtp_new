#!/usr/bin/env python

__author__   = 'EGFABT'
__revision__ = "$Id: test_hashrandom.py,v 1.1 2002/12/02 19:58:55 myers_carpenter Exp $"

import unittest

from egtp import hashrandom

class HashRandomTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSHARandom(self):
        LEN = 20
        r = hashrandom.SHARandom("0123456789")
        result = r.get(LEN)
        assert len(result) == LEN
        

    def testSHARandom234(self):
        from egtp.crypto import randsource
        # ITERS=100 # for serious testing
        ITERS=4 # for fast, casual testing
        for i in range(ITERS):
            r = hashrandom.SHARandom(randsource.get(10))

            leng = (((ord(randsource.get(1)) * i * 3) + ord(randsource.get(1))) / 32) + 8
            result = r.get(leng)
            assert len(result) == leng
        
def suite():
    suite = unittest.makeSuite(HashRandomTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
