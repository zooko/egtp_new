#!/usr/bin/env python

__author__   = 'Myers Carpenter'
__revision__ = "$Id: test_crypto.py,v 1.2 2003/03/23 16:15:53 myers_carpenter Exp $"

import unittest

import egtp.crypto.aesctr

class SampleTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSample1(self):

        text = 'Ripley is a annoying cat' * 5000
        
        print len(text)


        key = '1'*16
        
        aeskey = egtp.crypto.aesctr.new(key)
        aeskey2 = egtp.crypto.aesctr.new(key)
        
        ciphertext = aeskey.encrypt('\x00'*16, text)
        text2 = aeskey2.decrypt('\x00'*16, ciphertext)
        
        assert text == text2



def suite():
    suite = unittest.makeSuite(SampleTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
