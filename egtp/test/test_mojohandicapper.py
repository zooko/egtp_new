#!/usr/bin/env python

__author__   = 'EGFABT'
__revision__ = "$Id: test_mojohandicapper.py,v 1.1 2003/02/27 22:12:19 myers_carpenter Exp $"

import unittest

from egtp.MojoHandicapper import *

class MojoHandicapperTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_disqualified_not_returned(self):
        id_a = idlib.string_to_id('a')
        id_b = idlib.string_to_id('b')
        h = MojoHandicapper()
        def cfunc(counterparty_id, metainfo, message_type, message_body, id_a = id_a, id_b = id_b) :
            if counterparty_id == id_a :
                return DISQUALIFIED
            else :
                return 0
        h.add_handicapper(cfunc)
        result = h.sort_by_preference(counterparty_ids = [(id_a, None), (id_b, None)], message_type = 'a message', message_body = {})
        assert len(result) == 1
        assert result[0][0] == id_b

    def test_returns_nothing_for_nothing(self):
        assert len(MojoHandicapper(None).sort_by_preference([], 'm', {})) == 0

    def test_asserts_for_negative_value(self):
        id_a = idlib.string_to_id('a')
        h = MojoHandicapper()
        def cfunc(counterparty_id, metainfo, message_type, message_body) :
            return -2
        h.add_handicapper(cfunc)
        try :
            h.sort_by_preference(counterparty_ids = [(id_a, None)], message_type = 'a message', message_body = {})
            return 0
        except AssertionError :
            return 1
        
    def test_normal_operation(self):
        id_a = idlib.string_to_id('a')
        id_b = idlib.string_to_id('b')
        h = MojoHandicapper()
        def cfunc(counterparty_id, metainfo, message_type, message_body, id_a = id_a, id_b = id_b) :
            if counterparty_id == id_a :
                return 1
            else :
                return 0
        h.add_handicapper(cfunc)
        result = h.sort_by_preference(counterparty_ids = [(id_a, None), (id_b, None)], message_type = 'a message', message_body = {})
        assert len(result) == 2
        assert result[0][0] == id_b
        assert result[1][0] == id_a
        
    def test_normal_operation_opposite_order(self):
        id_a = idlib.string_to_id('a')
        id_b = idlib.string_to_id('b')
        h = MojoHandicapper()
        def cfunc(counterparty_id, metainfo, message_type, message_body, id_a = id_a, id_b = id_b) :
            if counterparty_id == id_a :
                return 1
            else :
                return 0
        h.add_handicapper(cfunc)
        result = h.sort_by_preference(counterparty_ids = [(id_b, None), (id_a, None)], message_type = 'a message', message_body = {})
        assert len(result) == 2
        assert result[0][0] == id_b
        assert result[1][0] == id_a
        
    def test_equal_handicap_returns_something(self):
        id_a = idlib.string_to_id('a')
        id_b = idlib.string_to_id('b')
        h = MojoHandicapper()
        def cfunc(counterparty_id, metainfo, message_type, message_body, id_a = id_a, id_b = id_b) :
            return 1
        h.add_handicapper(cfunc)
        result = h.sort_by_preference(counterparty_ids = [(id_a, None), (id_b, None)], message_type = 'a message', message_body = {})
        assert len(result) == 2
        assert result[0][0] != result[1]
        
    def test_uses_first_handicapper_stored(self):
        id_a = idlib.string_to_id('a')
        id_b = idlib.string_to_id('b')
        h = MojoHandicapper()
        def cfunc(counterparty_id, metainfo, message_type, message_body, id_a = id_a, id_b = id_b) :
            if counterparty_id == id_a :
                return 1
            else :
                return 0
        h.add_handicapper(cfunc)
        def cfunc2(counterparty_id, metainfo, message_type, message_body, id_a = id_a, id_b = id_b) :
            if counterparty_id == id_a :
                return 0
            else :
                return 2
        h.add_handicapper(cfunc2)
        result = h.sort_by_preference(counterparty_ids = [(id_b, None), (id_a, None)], message_type = 'a message', message_body = {})
        assert len(result) == 2
        assert result[0][0] == id_a
        assert result[1][0] == id_b
        
    def test_uses_second_handicapper_stored(self):
        id_a = idlib.string_to_id('a')
        id_b = idlib.string_to_id('b')
        h = MojoHandicapper()
        def cfunc(counterparty_id, metainfo, message_type, message_body, id_a = id_a, id_b = id_b) :
            if counterparty_id == id_a :
                return 0
            else :
                return 2
        h.add_handicapper(cfunc)
        def cfunc2(counterparty_id, metainfo, message_type, message_body, id_a = id_a, id_b = id_b) :
            if counterparty_id == id_a :
                return 1
            else :
                return 0
        h.add_handicapper(cfunc2)
        result = h.sort_by_preference(counterparty_ids = [(id_b, None), (id_a, None)], message_type = 'a message', message_body = {})
        assert len(result) == 2
        assert result[0][0] == id_a
        assert result[1][0] == id_b

def suite():
    suite = unittest.makeSuite(MojoHandicapperTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
