#!/usr/bin/env python

__author__   = 'EGFABT'
__revision__ = "$Id: test_datatypes.py,v 1.1 2003/02/27 22:12:18 myers_carpenter Exp $"

import unittest

from egtp.DataTypes import *

class DataTypesTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_not_on_rejection(self):
        check_template('a', NotMarker('b'))

    def test_not_on_acceptance(self):
        try:
            check_template('a', NotMarker('a'))
        except BadFormatError:
            pass
        else:
            self.fail()
            
    def test_uses_function(self):
        spam = []
        check_template(3, lambda thing, verbose, spam = spam: spam.append(thing))
        assert len(spam) == 1 and spam[0] == 3

    def test_none_passes_none(self):
        check_template(None, None)

    def test_none_rejects_string(self):
        try:
            check_template('spam', None)
        except BadFormatError:
            pass
        else:
            self.fail()

    def test_check_positive_accepts_positive(self):
        check_template(2, 1)

    def test_check_positive_rejects_zero(self):
        try:
            check_template(0, 1)
        except BadFormatError:
            pass
        else:
            self.fail()
                    
    def test_check_positive_rejects_negative(self):
        try:
            check_template(-2, 1)
        except BadFormatError:
            pass
        else:
            self.fail()
            
    def test_check_int_passes(self):
        check_template(3, -1)
        check_template(-2, -1)
        check_template(0, -1)

    def test_check_int_fails_string(self):
        try:
            check_template('spam', -1)
        except BadFormatError:
            pass
        else:
            self.fail()
            
    def test_check_nonnegative_accepts_positive(self):
        check_template(2, 0)
        
    def test_check_nonnegative_accepts_zero(self):
        check_template(0, 0)

    def test_check_nonnegative_rejects_negative(self):
        try:
            check_template(-2, 0)
        except BadFormatError:
            pass
        else:
            self.fail()
            
    # checks both items of a list passing
    def test_check_list_pass(self):
        template = ListMarker({"a": ANY})
        thing = [{"a": "a"},{"a": "a"}]
        check_template(thing, template)

    # checks the second item of a list failing
    def test_check_list_fail(self):
        template = ListMarker({"a": ANY})
        thing = [{"a": "a"},{"b": "a"}]
        try:
            check_template(thing, template)
        except BadFormatError:
            pass
        else:
            self.fail()
            
    def test_check_option_accepts_nonexistent(self):
        template = {'spam': OptionMarker('eggs')}
        thing = {}
        check_template(thing, template)
        
    def test_check_option_rejects_exists_with_none(self):
        template = {'spam': OptionMarker('eggs')}
        thing = {'spam': None}
        try:
            check_template(thing, template)
        except BadFormatError:
            pass
        else:
            self.fail()
                    
    def test_check_option_accepts_valid(self):
        template = {'spam': OptionMarker('eggs')}
        thing = {'spam': 'eggs'}
        check_template(thing, template)
        
    def test_check_option_rejects_invalid(self):
        template = {'spam': OptionMarker('eggs')}
        thing = {'spam': 'bacon'}
        try:
            check_template(thing, template)
        except BadFormatError:
            pass
        else:
            self.fail()
            
    # checks formatting against a non-list
    def test_check_bad_list(self):
        template = ListMarker({"a": ANY})
        thing = 'spam'
        try:
            check_template(thing, template)
        except BadFormatError:
            pass
        else:
            self.fail()
            
    # use list of matches none of which match (although combined pieces do)
    def test_check_multiple_fail(self):
        template = (
            {"a": ANY, "b": ANY},
            {"c": ANY, "d": ANY}
            )
        thing = {"a": "spam", "c": "eggs"}
        try:
            check_template(thing, template)
        except BadFormatError:
            pass
        else:
            self.fail()
                
    # use list of templates the first of which matches
    def test_check_multiple_pass_first(self):
        template = (
            {"a": ANY, "b": ANY},
            {"c": ANY, "d": ANY}
            )
        thing = {"a": "spam", "b": "eggs"}
        check_template(thing, template)
        
    # use list of two templates the second of which matches
    def test_check_multiple_pass_second(self):
        template = (
            {"a": ANY, "b": ANY},
            {"c": ANY, "d": ANY}
            )
        thing = {"c": "spam", "d": "eggs"}
        check_template(thing, template)
        
    # doesn't match first depth but does second
    def test_check_multiple_in_second_depth_pass(self):
        template = {"a": ({"c": ANY}, {"d": ANY})}
        thing = {"a": {"d": "spam"}}
        check_template(thing, template)
                    
    # matches first depth but not second
    def test_check_multiple_in_second_depth_fail(self):
        template = {"a": ({"c": ANY}, {"d": ANY})}
        thing = {"a": {"a": "spam"}}
        try:
            check_template(thing, template)
        except BadFormatError:
            pass
        else:
            self.fail()
def suite():
    suite = unittest.makeSuite(DataTypesTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
