#!/usr/bin/env python

__author__   = 'EGFABT'
__revision__ = "$Id: test_idlib.py,v 1.1 2002/12/02 19:58:56 myers_carpenter Exp $"

import unittest

from egtp import idlib

class IdlibTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def testToMojosixbitIsIdempotent(self):
        i = idlib.new_random_uniq()
        assert idlib.to_mojosixbit(i) == idlib.to_mojosixbit(idlib.to_mojosixbit(i))



def suite():
    suite = unittest.makeSuite(IdlibTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
