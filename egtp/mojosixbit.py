#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: mojosixbit.py,v 1.4 2002/12/02 19:58:53 myers_carpenter Exp $"

import re, string, types, binascii


true = 1
false = 0
from egtp import std



class Error(StandardError):
    pass


# re for matching mojosixbit encoded sha1's
_asciihash_re_str = '[-_0-9A-Za-z]{26}[AEIMQUYcgkosw048]'
_asciihash_re = re.compile('^'+_asciihash_re_str+'$')

# re for matching any valid canonical mojosixbit encoded string of bytes
_mojosixbit_re_str = '[-_0-9A-Za-z]*(|[-_0-9A-Za-z]{2}[AEIMQUYcgkosw048]|[-_0-9A-Za-z]{3}[AQgw])'
_mojosixbit_re = re.compile('^'+_mojosixbit_re_str+'$')

# internally used translation tables for filename safe sixbit strings
__to_mojosixbit = string.maketrans('+/', '-_')
__from_mojosixbit = string.maketrans('-_=+/', '+/!!!')   # =+/ are converted to ! so that they are rejected by the underlying RFC style base64 decoder

def _str_to_mojosixbit(str) :
    """
    Convert a string into our sixbit representation -without- any trailing '=' sign or newline padding.  

    You probably want `b2a()', which works on arguments of any length.
    """
    result = binascii.b2a_base64(str)

    # remove any newlines and '=' sign padding and translate
    # '+' -> '-' and '/' -> '_' for a filename safe representation
    result = string.translate(result, __to_mojosixbit, '\r\n=')

    return result

def _mojosixbit_to_str(sixbit) :
    """
    Convert a string back to binary from a sixbit representation.

    You probably want `a2b()'.
    """
    # add the appropriate '=' sign padding (len must be multiple of 4)
    if hasattr(types, 'UnicodeType') and type(sixbit) is types.UnicodeType:
        sixbit = str(sixbit)

    # translate '-' -> '+' and '_' -> '/' for decoding
    sixbit = string.translate(sixbit, __from_mojosixbit)

    topad = len(sixbit) % 4
    if topad == 3 :
        padding = '='
    elif topad == 2 :
        padding = '=='
    elif topad == 1 :
        padding = '==='
    else :
        padding = ''
    return binascii.a2b_base64(sixbit + padding)

def b2a(data):
    """
    Convert a string into our sixbit representation _without_ any trailing '=' sign or newline 
    padding.  
    """
    LEN_OF_BLOCK = 57

    # NOTE this is O((len(data)/57)^2) for large strings but we will never convert large strings to ascii so it doesn't matter
    
    i = 0
    asciiStr = ""
    while (i < len(data)):
        asciiStr = asciiStr + _str_to_mojosixbit(buffer(data[i:i+LEN_OF_BLOCK]))
        i = i + LEN_OF_BLOCK

    return asciiStr

try:
    unicode
    _strtypes = (types.StringType, types.UnicodeType)
except:
    _strtypes = (types.StringType,)

def a2b(astr, _strtypes=_strtypes):
    """
    @precondition: `astr' is a string.: type(astr) in _strtypes: "astr: %s" % `astr`

    @rasies mojosixbit.Error: if `astr' is `None', is an empty string "", does not fit the Mojo
        sixbit format, or has trailing garbage, or if b2a(a2b(astr)) != astr
    """
    assert type(astr) in _strtypes, "`astr' is a string." + " -- " + "astr: %s" % `astr`

    if len(astr) == 0:
        raise Error, "empty string is not a valid ascii-encoded value"

    if not _mojosixbit_re.match(astr):
        raise Error, ("string is not a valid ascii-encoded value", astr,)

    try:
        return _mojosixbit_to_str(astr)
    except binascii.Error, le:
        raise Error, (astr, le,)

def b2a_long_string_idempotent(thing):
    """
    If `thing' is not a valid mojosixbit-encoding, then return `b2a(thing)' on it, else return `thing'.
    Beware that strings that are too short (say, shorter than 20 bytes), might accidentally look like 
    a valid mojosixbit-encoding when they aren't.

    @precondition: `thing' must be long enough that there is no significant chance of an accident.: len(thing) >= 20: "len(thing): %s, thing: %s" % (std.hr(len(thing)), std.hr(thing),)
    """
    assert len(thing) >= 20, "precondition: `thing' must be long enough that there is no significant chance of an accident." + " -- " + "len(thing): %s, thing: %s" % (std.hr(len(thing)), std.hr(thing),)

    if _asciihash_re.match(thing):
        return thing
    else:
        return b2a(thing)

def a2b_long_string_idempotent(thing):
    """
    If `thing' is a valid mojosixbit-encoding, then return `a2b(thing)' on it, else return `thing'.
    Beware that strings that are too short (say, shorter than 20 bytes), might accidentally look like 
    a valid mojosixbit-encoding when they aren't.

    @precondition: `thing' must be long enough that there is no significant chance of an accident.: len(thing) >= 20: "len(thing): %s, thing: %s" % (std.hr(len(thing)), std.hr(thing),)
    """
    assert len(thing) >= 20, "precondition: `thing' must be long enough that there is no significant chance of an accident." + " -- " + "len(thing): %s, thing: %s" % (std.hr(len(thing)), std.hr(thing),)

    while 1:
        try:
            thing = a2b(thing)
        except Error:
            break

    return thing

