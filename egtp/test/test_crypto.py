#!/usr/bin/env python

__author__   = 'Myers Carpenter'
__revision__ = "$Id: test_crypto.py,v 1.1 2003/03/22 20:51:00 myers_carpenter Exp $"

import unittest

import egtp.crypto.aesctr

class SampleTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def longtobytes(self, n,block=1): #Slow!
        r = ""
        while n>0:
            r = chr(n&0xff) + r
            n = n >> 8
        if len(r)% block:
            r = chr(0)*(block-len(r)%block) + r
        return r

    def testSample1(self):

        text = 'Ripley is a annoying cat'


        print dir(egtp.crypto.aesctr)
        aeskey = egtp.crypto.aesctr.new('0'*16)
        
        ciphertext = aeskey.encrypt('0'*16, text)
        print '%r' % ciphertext
        text2 = aeskey.decrypt('0'*16, ciphertext)
        
        assert text == text2



def suite():
    suite = unittest.makeSuite(SampleTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
