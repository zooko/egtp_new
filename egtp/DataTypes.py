#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

"""
Test data coming from the network to make sure if fits the data type is supposed to.
"""

__revision__ = "$Id: DataTypes.py,v 1.11 2003/02/23 16:18:29 myers_carpenter Exp $"

import types, pprint

from egtp.MojoErrors import BadFormatError
from egtp import EGTPConstants, idlib, mojosixbit, std

from pyutil import humanreadable

true = 1
false = 0

def NONEMPTY(thing, verbose):
    pass

def ANY(thing, verbose):
    if thing is None:
        raise BadFormatError, "any can't be none"

def STRING(thing, verbose, StringType=types.StringType):
    if type(thing) is not StringType:
        raise BadFormatError, "not a string"

def BOOLEAN(thing, verbose):
    if thing != 'true' and thing != 'false':
        raise BadFormatError, "not 'true' or 'false'"

def INTEGER(thing, verbose, StringType=types.StringType, IntType=types.IntType, LongType=types.LongType):
    if type(thing) not in (StringType, IntType, LongType,):
        raise BadFormatError, "not an integer (not a string, int or long)"

    if type(thing) is StringType:
        try:
            num = long(thing)
        except ValueError:
            raise BadFormatError, "not an integer"

        canonicalstr = `num`
        # remove any annoying python 1.5.2 Ls (1.6 doesn't do this)
        if canonicalstr[-1] == 'L':
            canonicalstr = canonicalstr[:-1]

        if canonicalstr != thing:
            raise BadFormatError, "not an integer (not canonical)"

        if long(canonicalstr) != num:
            raise BadFormatError, "not an integer (not canonical)"

def NON_NEGATIVE_INTEGER(thing, verbose, StringType=types.StringType, IntType=types.IntType, LongType=types.LongType):
    if type(thing) not in (StringType, IntType, LongType,):
        raise BadFormatError, "not an integer (not a string, int or long)"

    if type(thing) is not StringType:
        if thing < 0:
            raise BadFormatError, "not a non-negative integer (not non-negative)"
    else:
        try:
            num = long(thing)
        except ValueError:
            raise BadFormatError, "not an integer"

        canonicalstr = `num`
        # remove any annoying python 1.5.2 Ls (1.6 doesn't do this)
        if canonicalstr[-1] == 'L':
            canonicalstr = canonicalstr[:-1]

        if canonicalstr != thing:
            raise BadFormatError, "not an integer (not canonical)"

        if long(canonicalstr) != num:
            raise BadFormatError, "not an integer (not canonical)"

        if num < 0:
            raise BadFormatError, "not a non-negative integer (not non-negative)"

def ASCII_ARMORED_DATA(thing, verbose, StringType=types.StringType):
    if type(thing) is not types.StringType:
        raise BadFormatError, "not proper ascii-armored data - not a string"
    try:
        if not len(mojosixbit.a2b(thing)) > 0:
            raise BadFormatError, 'zero-length strings are rejected by ascii armored data match'
    except mojosixbit.Error, reason:
        raise BadFormatError, str(reason)
    ### !!!!! XXXXXX need to make this canonical!  --Zooko 2000-08-20

def UNIQUE_ID(thing, verbose, StringType=types.StringType):
    if type(thing) is not StringType or not idlib.is_sloppy_id(thing):
        raise BadFormatError, "not an unique id"
    if idlib.is_mojosixbitencoded_id(thing):
        # XXX someday soon this will reject mojosixbit encoded UNIQUE_IDs...  --Zooko 2003-02-08
        debugprint("warning: found mojosixbitencoded id in protocol.  These should be converted to flat binary encoding.  id: %s\n", args=(thing,), v=5, vs="protocol")

def ASCII_ID(thing, verbose, StringType=types.StringType):
    if type(thing) is not StringType or not idlib.is_mojosixbitencoded_id(thing):
        raise BadFormatError, "not an ascii id"

def MOD_VAL(thing, verbose, StringType=types.StringType):
    if type(thing) is not StringType:
        raise BadFormatError, "not proper modval - not a string"
    try:
        if len(mojosixbit.a2b(thing)) != EGTPConstants.SIZE_OF_MODULAR_VALUES:
            raise BadFormatError, "not a proper modval"
    except mojosixbit.Error:
        raise BadFormatError, "not a proper modval - not even proper ascii-encoded data"

def BINARY_SHA1(thing, verbose, StringType=types.StringType):
    """
    @deprecated: in favor of UNIQUE_ID
    """
    if type(thing) is not StringType:
        raise BadFormatError, "not proper binary sha1 - not a string"
    if not idlib.is_canonical_uniq(thing):
        raise BadFormatError, "not a sha1 value - it does not have a length of 20" 

class OptionMarker :
    def __init__(self, template) :
        self.template = template
    def __repr__(self):
        return "OptionMarker: <%s>" % humanreadable.hr(self.template)

def AndMarker(templs):
    """
    Require the thing to match all templates.
    """
    def func(thing, verbose, templs = templs):
        for templ in templs:
            if verbose:
                inner_check_verbose(thing, templ)
            else:
                inner_check_noverbose(thing, templ)
    return func

def NotMarker(template):
    def func(thing, verbose, template = template):
        try:
            if verbose:
                inner_check_verbose(thing, template)
            else:
                inner_check_noverbose(thing, template)
        except BadFormatError:
            return
        raise BadFormatError, "got match when should not have"
    return func

NOT_PRESENT = OptionMarker(NotMarker(NONEMPTY))

def ListMarker(template, ListType=types.ListType, TupleType=types.TupleType):
    def func(thing, verbose, template = template, ListType=ListType, TupleType=TupleType):
        if type(thing) not in (ListType, TupleType,):
            raise BadFormatError, 'not a list'
        if verbose:
            try:
                i = 0
                while i < len(thing):
                    if verbose:
                        inner_check_verbose(thing[i], template)
                    else:
                        inner_check_noverbose(thing[i], template)
                    i = i + 1
            except BadFormatError, reason:
                raise BadFormatError, 'mismatch at index ' + humanreadable.hr(i) + ': ' + str(reason)
        else:
            for i in thing :
                if verbose:
                    inner_check_verbose(i, template)
                else:
                    inner_check_noverbose(i, template)
    return func

def is_template_matching(thing, templ):
    try:
        check_template(thing, templ)
    except BadFormatError:
        return false
    return true
       
def check_template(thing, templ):
    """
    throws BadFormatError if the thing does not match the template
    """
    try:
        inner_check_noverbose(thing, templ)
        return
    except BadFormatError, reason:
        pass
    try:
        inner_check_verbose(thing, templ)
    except BadFormatError, reason:
        raise BadFormatError, 'failed template check because: (%s) template was: (%s) target was: (%s)' % (str(reason), pprint.pformat(humanreadable.hr(templ)),  pprint.pformat(humanreadable.hr(thing)))

def inner_check_verbose(thing, templ, FunctionType=types.FunctionType, MethodType=types.MethodType, DictType=types.DictType, StringType=types.StringType, LongType=types.LongType, IntType=types.IntType, ListType=types.ListType, TupleType=types.TupleType):
    # The following isn't really used right now, but I'm leaving the commented-out code for evidence.  --Zooko 2001-06-07
    # if isinstance(thing, mencode.PreEncodedThing):
    #     thing = thing.getvalue()

    templtype = type(templ)
    if templtype is FunctionType or templtype is MethodType:
        templ(thing, true)
    elif templtype is DictType:
        if not type(thing) is DictType:
            raise BadFormatError, 'target is not a dict'

        for key in templ.keys():
            if not thing.has_key(key):
                if not isinstance(templ[key], OptionMarker) :
                    raise BadFormatError, "lacks required key: (" + humanreadable.hr(key) + ")"
            else:
                try:
                    if isinstance(templ[key], OptionMarker) :
                        inner_check_verbose(thing[key], templ[key].template)
                    else :
                        inner_check_verbose(thing[key], templ[key])
                except BadFormatError, reason:
                    raise BadFormatError, 'mismatch in key (' + humanreadable.hr(key) + '): ' + str(reason)
    elif templtype is StringType:
        if type(thing) is not StringType:
            raise BadFormatError, "no match - target is not a string"
        if thing != templ:
            raise BadFormatError, "strings (" + thing + ') and (' + templ + ') do not match'
    elif templ == 0 or templ == -1 or templ == 1:
        if type(thing) is not LongType and type(thing) is not IntType:
            raise BadFormatError, 'expected int'
        if templ == 0:
            if thing < 0:
                raise BadFormatError, 'template called for non-negative value'
        elif templ == -1:
            return
        else:
            assert templ == 1
            if thing <= 0:
                raise BadFormatError, 'template called for strictly positive value'
    elif templtype is ListType or templtype is TupleType:
        failure_reason = 'did not match any of the ' + humanreadable.hr(len(templ)) + ' possible templates;'
        index = -1
        for i in templ:
            try:
                index = index + 1
                inner_check_verbose(thing, i)
                return
            except BadFormatError, reason:
                failure_reason = failure_reason + ' failed template' + humanreadable.hr(i) + ' at index ' + humanreadable.hr(index) + ' on thing ' + humanreadable.hr(thing) + ' because (' + str(reason) + ')'
        raise BadFormatError, failure_reason
    elif templ is None:
        if thing is not None:
            raise BadFormatError, 'expected None'
    else:
        assert false, "bad template - " + humanreadable.hr(templ)

def checkTemplate(thing, templ):
    """
    @rasies BadFormatError: if the thing does not match the template
    @deprecated: in favor of `check_template()' for naming consistency reasons
    """
    return check_template(thing, templ)

def inner_check_noverbose(thing, templ, FunctionType=types.FunctionType, MethodType=types.MethodType, DictType=types.DictType, StringType=types.StringType, LongType=types.LongType, IntType=types.IntType, ListType=types.ListType, TupleType=types.TupleType):
    # The following isn't really used right now, but I'm leaving the commented-out code for evidence.  --Zooko 2001-06-07
    # if isinstance(thing, mencode.PreEncodedThing):
    #     thing = thing.getvalue()

    templtype = type(templ)
    if templtype is FunctionType or templtype is MethodType:
        templ(thing, false)
    elif templtype is DictType:
        if not type(thing) is DictType:
            raise BadFormatError, 'target is not a dict'

        for key in templ.keys():
            if not thing.has_key(key):
                if not isinstance(templ[key], OptionMarker) :
                    raise BadFormatError, "lacks required key"
            else:
                if isinstance(templ[key], OptionMarker) :
                    inner_check_noverbose(thing[key], templ[key].template)
                else:
                    inner_check_noverbose(thing[key], templ[key])
    elif templtype is StringType:
        if type(thing) is not StringType:
            raise BadFormatError, "no match - target is not a string"
        if thing != templ:
            raise BadFormatError, "strings do not match"
    elif templ == 0 or templ == -1 or templ == 1:
        if type(thing) is not LongType and type(thing) is not IntType:
            raise BadFormatError, 'expected int'
        if templ == 0:
            if thing < 0:
                raise BadFormatError, 'template called for non-negative value'
        elif templ == -1:
            return
        else:
            assert templ == 1
            if thing <= 0:
                raise BadFormatError, 'template called for strictly positive value'
    elif templtype is ListType or templtype is TupleType:
        for i in templ:
            try:
                inner_check_noverbose(thing, i)
                return
            except BadFormatError:
                pass
        raise BadFormatError, "did not match any possible templates"
    elif templ is None:
        if thing is not None:
            raise BadFormatError, 'expected None'
    else:
        assert false, "bad template - " + humanreadable.hr(templ)

