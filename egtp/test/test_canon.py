#!/usr/bin/env python
"""\
test_canon.py
"""

__author__   = 'EGFABT'
__revision__ = "$Id: test_canon.py,v 1.1 2002/12/14 04:50:22 myers_carpenter Exp $"

import unittest

from egtp import canon

class SampleTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_strip_leading_zeroes(self):
        str = '\000'
        res = canon.strip_leading_zeroes(str)
        assert res == ""
        pass

    def test_strip_leading_zeroes(self):
        str = '\000\000'
        res = canon.strip_leading_zeroes(str)
        assert res == ""
        pass
        
    def test_strip_leading_zeroes(self):
        str = '\000\000A'
        res = canon.strip_leading_zeroes(str)
        assert res == 'A'
        pass
        
    def test_strip_leading_zeroes(self):
        str = 'B\000\000A'
        res = canon.strip_leading_zeroes(str)
        assert res == str
        pass

    def test__canon(self):
        str = '\000'
        res = canon._canon(str, 2)
        assert res == '\000\000'

    def test_canon(self):
        str = '123'
        res = canon._canon(str, 128)
        assert res != '123'
        assert res == "\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000123"

    def test_canon_rejectsTooLarge(self):
        str = '123'
        try:
            canon._canon(str, 2)
        except AssertionError:
            return

        assert false

    def test_canon_tooManyLeadingZeroes(self):
        str = '\00023'

        assert canon._canon(str, 2) == '23'

    def test_canon_same(self):
        str = '23'

        assert canon._canon(str, 2) == '23'

    def test_canon_empty(self):
        str = ''

        assert canon._canon(str, 2) == '\000\000'



def suite():
    suite = unittest.makeSuite(SampleTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
