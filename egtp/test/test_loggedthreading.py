#!/usr/bin/env python

__author__   = 'zooko'
__revision__ = "$Id: test_loggedthreading.py,v 1.1 2003/03/09 18:54:57 zooko Exp $"

import unittest

from egtp.loggedthreading import *

class LoggedThreadingTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_this(self):
        print "FIXME: this does not test that the logging is working correctly"
        def funct():
            print 42
            raise "sixtynine dude!"
        l = LoggedThread(target=funct)
        l.start()
        import time
        time.sleep(1)


def suite():
    suite = unittest.makeSuite(LoggedThreadingTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
