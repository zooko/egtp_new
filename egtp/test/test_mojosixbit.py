#!/usr/bin/env python

__author__   = 'EGFABT'
__revision__ = "$Id: test_mojosixbit.py,v 1.1 2002/12/02 19:58:56 myers_carpenter Exp $"

import unittest

from egtp import mojosixbit

class MojosixbitTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testMojosixbit(self):
        assert mojosixbit._mojosixbit_to_str('abcd') == 'i\267\035'
        assert mojosixbit._mojosixbit_to_str('abcdef') == 'i\267\035y'
        assert mojosixbit._mojosixbit_to_str('abcdefg') == 'i\267\035y\370'
        assert mojosixbit._mojosixbit_to_str('abcdefgh') =='i\267\035y\370!'
        from struct import pack
        for x in range(0, 255) :
            sha_str = '\0'*19 + pack('B', x)
            sixbit_str = mojosixbit._str_to_mojosixbit(sha_str)
            assert len(sixbit_str) == 27
            assert mojosixbit._asciihash_re.match(sixbit_str)

    def testB2A(self):
        import random
        from array import array 
        b = array('B')
        for i in range(900):
            b.append(random.randint(0, 255))

        astr = mojosixbit.b2a(b)

        c = mojosixbit.a2b(astr)

        assert b.tostring() == c

    def testA2BRejectsNonEncoded(self):
        try:
            mojosixbit.a2b("*&")
        except mojosixbit.Error:
            return

        assert false

    def testA2BRejectsNonMojoSixBit(self):
        try:
            mojosixbit.a2b("hvfkN/q")
        except mojosixbit.Error:
            return

        assert false

    def testA2BRejectsTrailingGarbage(self):
        try:
            mojosixbit.a2b("c3BhbQ@@@")
        except mojosixbit.Error:
            return

        assert false
        
    def testA2BRejectsTrailingEqualSigns(self):
        try:
            mojosixbit.a2b("c3BhbQ==")
        except mojosixbit.Error:
            return

        assert false

    def testA2BRejectsTrailingNewlines(self):
        try:
            mojosixbit.a2b("c3BhbQ\n")
        except mojosixbit.Error:
            return

        assert false

    def testMojosixbitRE(self):
        b2a = mojosixbit.b2a
        for num in xrange(17):
            assert mojosixbit._mojosixbit_re.match(b2a(chr(num))), ('failed 2:', num, b2a(chr(num)))
            assert mojosixbit._mojosixbit_re.match(b2a(' '+chr(num))), ('failed 3:', num, b2a(' '+chr(num)))
            assert mojosixbit._mojosixbit_re.match(b2a('* '+chr(num))), ('failed 4:', num, b2a('* '+chr(num)))
            assert mojosixbit._mojosixbit_re.match(b2a(':-)'+chr(num))), ('failed 5:', num, b2a(':-)'+chr(num)))
            assert mojosixbit._mojosixbit_re.match(b2a('#8-}'+chr(num))), ('failed 6:', num, b2a('#8-}'+chr(num)))
            assert mojosixbit._mojosixbit_re.match(b2a(' ;-} '+chr(num))), ('failed 7:', num, b2a(' ;-} '+chr(num)))
            


def suite():
    suite = unittest.makeSuite(MojosixbitTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
