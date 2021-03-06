"""
Common code for encoding and decoding EGTP object IDs
in their two common representations (binary and ascii/mojosixbit).

Everything in this file is optimized for speed, it gets called a
-lot- throughout the program, including many hot spots.
"""

#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__version__ = "$Revision: 1.17 $"
# $Source: /home/zooko/playground/egtp_new/rescue-party/gw/../egtp_new/egtp_new/egtp/idlib.py,v $

# Python Standard Library modules
import re, sha, struct, types

from pyutil.debugprint import debugprint
# egtp modules
from egtp import EGTPConstants, std, mojosixbit, std
from egtp.crypto import randsource

# pyutil libs
from pyutil.debugprint import debugprint

True = 1 == 1
False = 0 == 1

_asciihash_re = mojosixbit._asciihash_re

try:
    unicode
    _strtypes = (types.StringType, types.UnicodeType)
except:
    _strtypes = (types.StringType,)

Size_of_NativeId_Int_Space = 2**24
Largest_Distance_NativeId_Int_Space = 2**23

def sign(id1, id2):
    """
    @return: `1' if the distance in the increasing direction around the circle from `id1' to `id2' is shorter than the distance in the decreasing direction, else returns `-1';  If (in *native int* form) id1 == id2, or id1 == (id2+Largest_Distance_NativeId_Int_Space), then return 0.
    """
    id1 = id_to_native_int(id1)
    id2 = id_to_native_int(id2)
    if id1 == id2:
        return 0
    dist = distance(id1, id2)
    if dist == Largest_Distance_NativeId_Int_Space:
        return 0

    if id1 + dist == id2:
        return 1
    else:
        return -1

def distance(id1, id2):
    """
    @param id1: an id, can be in native-int form (for extra speed -- it converts them to native int anyway so it doesn't change the answer)
    @param id2: an id, can be in native-int form (for extra speed -- it converts them to native int anyway so it doesn't change the answer)

    @return: the distance between the two ids on the Great Circle
    """
    id1 = id_to_native_int(id1)
    id2 = id_to_native_int(id2)

    dif1 = abs(id1 - id2)
    dif2 = Size_of_NativeId_Int_Space - dif1
 
    return min(dif1, dif2)

def id_to_native_int(id, IntType=types.IntType, LongType=types.LongType, FloatType=types.FloatType):
    """
    This uses only the first 24 bits of `id', in order to be fast.
    (If we used 32 bits, it would be slower due to using Python longs
    instead of a native int.)

    @param: id can be one of the following four options: a native-int
        representation of an id, a float representation of a native-int,
        a full 160-bit id in either straight binary or mojosixbit-
        encoded form, or the prefix of an id, as long as it contains at
        least 24 bits of information and is in straight binary form,
        *not* in mojosixbit encoded form

    @precondition: `id' must be an id or a native-int of an id, a float of an id, or else it must be the right length for a binary id prefix.: is_sloppy_id(id) or ((type(id) in (IntType, LongType, FloatType,)) and ((id >= 0) and (id < (2 ** 24)))) or ((len(id) >= 3) and (len(id) <= EGTPConstants.SIZE_OF_UNIQS)): "id: %s :: %s" % (std.hr(id), std.hr(type(id)),)
    """
    assert is_sloppy_id(id) or ((type(id) in (IntType, LongType, FloatType,)) and ((id >= 0) and (id < (2 ** 24)))) or ((len(id) >= 3) and (len(id) <= EGTPConstants.SIZE_OF_UNIQS)), "precondition: `id' must be an id or a native-int of an id, a float of an id, or else it must be the right length for a binary id prefix." + " -- " + "id: %s :: %s" % (std.hr(id), std.hr(type(id)),)

    if type(id) == types.StringType and is_mojosixbitencoded_id(id):
        debugprint("warning: mojosixbitencoded id encountered.  Should be converted to flat binary.  id: %s\n", args=(id,))
    typ = type(id)
    if typ is IntType or typ is LongType or typ is FloatType:
        return int(id)

    try:
        # debugprint.debugprint("id: %s, %s, %s, %s\n" % (id, str(id), repr(id), std.hr(id),))
        nid = mojosixbit.a2b(id)
        if len(nid) < 3:
            # Hm.  More than likely this was actually a binary, but short, string that happened to look like a mojosixbit encoded string.  Let's just put it back without complaining.
            nid = id
    except mojosixbit.Error:
        # Good -- it was not an ascii-encoded thing.
        nid = id
        pass

    return struct.unpack(">i", chr(0) + nid[:3])[0]

def int_to_id_prefix(i):
    """
    This generates only the first 24 bits of an id, from the most significant 24 bits of `i'.

    @param i: an int or an id

    @precondition: `i' must be an integer or an id.: is_sloppy_id(i) or (type(i) in ( types.IntType, types.LongType, )): "i: %s :: %s" % (std.hr(i), std.hr(type(i)))
    """
    assert is_sloppy_id(i) or (type(i) in ( types.IntType, types.LongType, )), "precondition: `i' must be an integer or an id." + " -- " + "i: %s :: %s" % (std.hr(i), std.hr(type(i)))

    if is_sloppy_id(i):
        return i

    C = 2**24

    while (i > C):
        i = i >> 8

    if type(id) in [ types.LongType, types.IntType ]:
        return struct.pack(">i", int(i))[1:]

def is_canonical_uniq(thing, _strtypes=_strtypes):
    """slightly slower than is_binary_id, but more accurate due to the type check"""
    if type(thing) not in _strtypes:
        return False
    return len(thing) == EGTPConstants.SIZE_OF_UNIQS

def identifies(id, thing, thingtype=None):
    """
    @precondition: `id' must be an id.: is_sloppy_id(id): "id: %s" % repr(id)
    """
    assert is_sloppy_id(id), "precondition: `id' must be an id." + " -- " + "id: %s" % repr(id)

    return equal(id, make_id(thing, thingtype))

def make_ascii_id(data):
    """Returns a nice simple 27 char ascii encoded id (sha1) of data"""
    return mojosixbit.b2a(string_to_id(data))

def string_to_id(sexpStr):
    """
    @param sexpStr: the string containing the expression in canonical form

    @return: the unique id of the sexp str

    @postcondition: Result is of correct form.: is_binary_id(result)

    @precondition: `sexpStr' must be a string.: type(sexpStr) == types.StringType: "sexpStr: %s" % repr(sexpStr)

    @memoizable

    @deprecated: in favor of new name: `make_id()'
    """
    return make_id(sexpStr)

def make_id(thing, thingtype=None):
    """
    Use this function to create a unique persistent cryptographically assured id of a string.

    @param thing: the thing that you want an id of
    @param thingtype: optional type of the thing (ignored)

    @precondition: `thing' must be a string.: type(thing) == types.StringType: "thing: %s :: %s" % (std.hr(thing), std.hr(type(thing)))

    """
    assert type(thing) == types.StringType, "precondition: `thing' must be a string." + " -- " + "thing: %s :: %s" % (str(thing), str(type(thing)))

    return sha.new(thing).digest()

def canonicalize(id, thingtype=None):
    """
    Use this function to canonicalize an id of one of the "bare" forms
    (a EGTPConstants.SIZE_OF_UNIQS-byte binary string or the mojosixbit
    encoding thereof) into the canonical form.  Useful for calling on
    ids received from other brokers over the wire.

    @param id: an id, which may be a bare binary or bare mojosixbit encoded id,
        or a full canonical id
    @param thingtype: optional type of the thing that is identified (ignored)

    @return: the full canonical id

    @precondition: `id' must be an id.: is_sloppy_id(id): "id: %s" % repr(id)
    """
    assert is_sloppy_id(id), "precondition: `id' must be an id." + " -- " + "id: %s" % repr(id)

    # NOTE: this method is also known as idlib.to_binary
    # implemented for speed not maintainability:
    if len(id) == EGTPConstants.SIZE_OF_UNIQS:
        return id
    else:
        return mojosixbit.a2b(id)

def equal(id1, id2):
    """
    @return: true if and only if id1 and id2 identify the same thing;  if `id1' or `id2' or both are `None', then `equals()' returns false.

    @precondition: `id1' must be `None' or an id.: (id1 is None) or is_sloppy_id(id1): "id1: %s" % repr(id1)
    @precondition: `id2' must be `None' or an id.: (id2 is None) or is_sloppy_id(id2): "id2: %s" % repr(id2)
    """
    assert (id1 is None) or is_sloppy_id(id1), "precondition: `id1' must be `None' or an id." + " -- " + "id1: %s" % repr(id1)
    assert (id2 is None) or is_sloppy_id(id2), "precondition: `id2' must be `None' or an id." + " -- " + "id2: %s" % repr(id2)

    if (not id1) or (not id2):
        return None

    if len(id1) == len(id2):
        return id1 == id2

    if len(id1) == 27:
        assert len(id2) == EGTPConstants.SIZE_OF_UNIQS
        return to_binary(id1) == id2
    else:
        assert len(id2) == 27
        assert len(id1) == EGTPConstants.SIZE_OF_UNIQS
        return id1 == to_binary(id2)

# alternate name
equals = equal

def make_new_random_id(thingtype=None):
    return new_random_uniq()

def string_to_id(sexpStr):
    """
    @param sexpStr: the string containing the expression in canonical form

    @return: the unique id of the sexp str

    @postcondition: Result is of correct form.: is_binary_id(result)

    @precondition: `sexpStr' must be a string.: type(sexpStr) == types.StringType: "sexpStr: %s" % repr(sexpStr)

    @memoizable
    """
    assert type(sexpStr) == types.StringType, "precondition: `sexpStr' must be a string." + " -- " + "sexpStr: %s" % repr(sexpStr)

    return sha.new(sexpStr).digest()

def id_to_abbrev(str):
    """
    @precondition: `str' must be an id.: is_sloppy_id(str): "str: %s" % repr(str)
    """
    if (len(str) == 27) and (_asciihash_re.match(str)):
        return "<" + str[:4] + ">"
    elif len(str) == EGTPConstants.SIZE_OF_UNIQS:
        return "<" + mojosixbit.b2a(str[:3]) + ">"
    else:
        assert is_sloppy_id(str), "precondition: `str' must be an id." + " -- " + "str: %s" % repr(str)

# this gets called a -lot-, it must be fast!
def is_sloppy_id(astr, thingtype=None, _strtypes=_strtypes, _asciihash_re=_asciihash_re, SIZE_OF_UNIQS=EGTPConstants.SIZE_OF_UNIQS):
    return (type(astr) in _strtypes) and ((len(astr) == SIZE_OF_UNIQS) or ((len(astr) == 27) and (_asciihash_re.match(astr))))

# this gets called a -lot-, it must be fast!
def is_mojosixbitencoded_id(str, thingtype=None, _asciihash_re=_asciihash_re):
    try:
        return (len(str) == 27) and (_asciihash_re.match(str))
    except:
        return False

is_ascii_id = is_mojosixbitencoded_id

# this gets called a -lot-, it must be fast!
def is_binary_id(str, thingtype=None, SIZE_OF_UNIQS=EGTPConstants.SIZE_OF_UNIQS):
    """
    @deprecated in favor of "is_id()" for naming reasons
    """
    try:
        return len(str) == SIZE_OF_UNIQS
    except:
        return False

# this gets called a -lot-, it must be fast!
def is_id(str, thingtype=None, SIZE_OF_UNIQS=EGTPConstants.SIZE_OF_UNIQS):
    try:
        return len(str) == SIZE_OF_UNIQS
    except:
        return False

sloppy_id_to_bare_binary_id = canonicalize
to_binary = canonicalize

def to_mojosixbit(sid):
    """
    @precondition: `sid' must be an id.: is_sloppy_id(sid): "sid: %s" % repr(sid)
    """
    if _asciihash_re.match(sid):
        return sid

    assert len(sid) == EGTPConstants.SIZE_OF_UNIQS, "`sid' must be a mojosixbit or binary id." + " -- " + "sid: %s" % repr(sid)

    # then it must be binary, encode it
    return mojosixbit.b2a(sid)

to_ascii = to_mojosixbit

def newRandomUniq():
    """
    @return: a universally unique random number

    @postcondition: Result is of correct form.: is_canonical_uniq(result)

    @deprecated: in favor of `new_random_uniq()'
    """
    return randsource.get(EGTPConstants.SIZE_OF_UNIQS)

new_random_uniq = newRandomUniq

std.is_sloppy_id = is_sloppy_id
std.is_canonical_uniq = is_canonical_uniq
std.is_mojosixbitencoded_id = is_mojosixbitencoded_id


