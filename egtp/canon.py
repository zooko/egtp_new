#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: canon.py,v 1.4 2002/12/14 04:50:21 myers_carpenter Exp $"

import types, operator

from pyutil import humanreadable

from egtp import std

def _canon(numstr, size):
    """
    @param numstr: the string representation of an integer which will be canonicalized
    @param size: the size in 8-bit bytes (octets) that numbers of this kind should have;  This
        number should almost always be EGTPConstants.SIZE_OF_UNIQS or
        EGTPConstants.SIZE_OF_MODULAR_VALUES

    @return: the canonical version of `numstr' for numbers of its type

    @precondition: `numstr' must be a string.: type(numstr) == types.StringType: "numstr: %s :: %s" % (humanreadable.hr(numstr), `type(numstr)`)
    @precondition: `numstr', not counting leading zeroes, is not too large.: len(strip_leading_zeroes(numstr)) <= size: "numstr: %s" % humanreadable.hr(numstr)
    """
    assert type(numstr) == types.StringType, "precondition: `numstr' must be a string." + " -- " + "numstr: %s :: %s" % (humanreadable.hr(numstr), `type(numstr)`)
    assert len(strip_leading_zeroes(numstr)) <= size, "precondition: `numstr', not counting leading zeroes, is not too large." + " -- " + "numstr: %s" % humanreadable.hr(numstr)

    if len(numstr) >= size:
        return numstr[len(numstr) - size:]

    return operator.repeat('\000', size - len(numstr)) + numstr

def strip_leading_zeroes(numstr):
    """
    @param numstr: the string to be stripped

    @return: `numstr' minus any leading zero bytes

    @precondition: `numstr' must be a string.: type(numstr) == types.StringType: "numstr: %s :: %s" % (humanreadable.hr(numstr), `type(numstr)`)
    """
    assert type(numstr) == types.StringType, "precondition: `numstr' must be a string." + " -- " + "numstr: %s :: %s" % (humanreadable.hr(numstr), `type(numstr)`)

    if len(numstr) == 0:
        return numstr

    # When we are done `i' will point to the first non-zero byte.
    i = 0

    while (i < len(numstr)) and (numstr[i] == '\000'):
        i = i + 1
        
    return numstr[i:]

def is_canonical(astr, length, StringType=types.StringType):
    if type(astr) is not types.StringType:
        return 0 # false
    return len(astr) == length

def is_canonical_modval(astr):
    """
    Return `true' if and only if `astr' is in canonical format for modular values encoded into
    string form.

    @memoizable
    """
    return is_canonical(astr, EGTPConstants.SIZE_OF_MODULAR_VALUES)

def is_canonical_uniq(astr):
    """
    Return `true' if and only if `astr' is in canonical format for "uniq" strings.

    @memoizable
    """
    return is_canonical(astr, EGTPConstants.SIZE_OF_UNIQS)

# STDHACK

std.is_canonical_modval = is_canonical_modval
std.is_canonical_uniq = is_canonical_uniq
