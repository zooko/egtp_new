#!/usr/bin/env python
"""\
test_crypto_cryptutil.py
BUGBUG this file needs a license, myers wrote it.
"""

__author__   = 'EGFABT'
__revision__ = "$Id: test_cryptutil.py,v 1.2 2003/02/17 09:35:22 artimage Exp $"

import unittest

from egtp.crypto import cryptutil

class SampleTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hmac(self):
        def longtobytes(n,block=1): #Slow!
            r = ""
            while n>0:
                r = chr(n&0xff) + r
                n = n >> 8
            if len(r)% block:
                r = chr(0)*(block-len(r)%block) + r
            return r
        test_vectors_sha = [
            #(key,data,result)
            #Taken from rfc2202
            ("\x0b"*20,"Hi There",0xb617318655057264e28bc0b6fb378c8ef146be00L),
            ("Jefe","what do ya want for nothing?",0xeffcdf6ae5eb2fa2d27416d5f184df9c259a7c79L),
            ("\xAA"*20,"\xDD"*50,0x125d7342b9ac11cd91a39af48aa17b4f63f175d3L),
            (0x0102030405060708090a0b0c0d0e0f10111213141516171819L,"\xcd"*50,
             0x4c9007f4026250c6bc8414f9bf50c86c2d7235daL),
            ("\x0c"*20,"Test With Truncation",0x4c1a03424b55e07fe7f27be1d58bb9324a9a5a04L),
            ("\xaa"*80,"Test Using Larger Than Block-Size Key - Hash Key First",
             0xaa4ae5e15272d00e95705637ce8a3b55ed402112L),
            ("\xaa"*80,
             "Test Using Larger Than Block-Size Key and Larger Than One Block-Size Data",
             0xe8e99d0f45237d786d6bbaa7965c7808bbff1a91L),
            ]
        for (key,data,result) in test_vectors_sha:
            if type(key)==type(1L): key=longtobytes(key)
            if type(data)==type(1L): data=longtobytes(data)
            if type(result)==type(1L): result=longtobytes(result,20)
            assert cryptutil.hmac(key,data) == result, "Failed on %s" % repr((key,data,result))

def suite():
    suite = unittest.makeSuite(SampleTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
