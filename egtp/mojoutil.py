#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: mojoutil.py,v 1.10 2002/12/02 21:20:46 myers_carpenter Exp $"

# standard modules
import binascii, copy, math, operator, os, profile, pstats, re
import sha, string, struct, sys, threading, traceback, time, types
import whrandom, random

# pyutil modules
from pyutil.debugprint import debugprint, debugstream
from pyutil import fileutil

# EGTP modules
from egtp import humanreadable

try:
    import trace
except ImportError, le:
    debugprint("ignoring failure to import trace. le: %s\n", args=(le,), v=6, vs="debug")
    pass

try:
    import coverage
except ImportError, le:
    debugprint("ignoring failure to import coverage. le: %s\n", args=(le,), v=6, vs="debug")
    pass

# Backwards-compatible names.
from pyutil.fileutil import *
from pyutil.dictutil import *
from egtp.crypto.cryptutil import *
from egtp.mojosixbit import *
from egtp.canon import *
from egtp.mojostd import iso_utc_time, iso_utc_time_to_localseconds, test_iso8601_utc_time, test_iso_utc_time_to_localseconds


def bool(thingie):
    if thingie:
        return 1
    else:
        return None

def get_file_size(f):
    ptr = f.tell()
    f.seek(0, 2)
    try:
        return f.tell()
    finally:
        f.seek(ptr)

def is_machine_little_endian():
    # XXX See sys.byteorder in Python >= 2.0.  --Zooko 2002-01-03
    # This assumes that the `struct' module correctly packs ints in native format.
    if struct.pack("=i", 1)[0] == "\001":
        return true
    else:
        return false

def _skim_with_builtin_naive(set, num):
    """
    very slow
    """
    items = set.items()
    items.sort(lambda a, b: cmp(b[1], a[1]))
    items = items[num:]
    for key, val in items:
        del set[key]
    return

def _skim_with_builtin(set, num):
    """
    nice and fast, but still does a full sort so it is O(N log N)

    @precondition: `num' must be non-negative.: num >= 0: "num: %s" % `num`
    """
    assert num >= 0, "precondition: `num' must be non-negative." + " -- " + "num: %s" % `num`

    if len(set) <= num:
        return

    if num == 0:
        set.clear()
        return

    if len(set) == 0:
        return

    vals = set.values()
    vals.sort()

    i = len(vals) - num
    # Now the smallest value that can remain in `set' is in vals[i].
    smallestval = vals[i]

    # Now see how many other elements, with the same value, should be thrown out.
    j = i
    while (i > 0) and (vals[i-1] == smallestval):
        i = i - 1

    numdups = j - i # the number of elements with the same value that must be thrown out.
    numthrown = 0

    # print "i: %s, numdups: %s, vals: %s, smallestval: %s" % (`i`, `numdups`, `vals`, `smallestval`)
    # Now make one pass through `set' throwing out all elements less than val, plus `numdups' of the same val.
    items = set.items()

    for key, val in items:
        if val < smallestval:
            del set[key]
        elif val == smallestval:
            if numthrown < numdups:
                del set[key]
                numthrown = numthrown + 1

    assert len(set) == num, "len(set): %s, num: %s, set: %s" % (`len(set)`, `num`, `set`)

def _skim_with_partial_bisort(set, num):
    """
    Throw out all but the top `num' items.
    This does a partial binary insertion sort.
    This mutates `set'.
    All values must be > (-sys.maxint-1).
    This is up to 2.5 times as fast as `_sort_with_builtin()' in benchmarks.  It's fastest when `num' is small.

    @param set: a map from keys to values
    @return: No return value, but `set' has been "skimmed" so that only the `num' items with the highest values remain.
    @precondition: `num' must be non-negative.: num >= 0: "num: %s" % humanreadable.hr(num)
    """
    assert num >= 0, "precondition: `num' must be non-negative." + " -- " + "num: %s" % humanreadable.hr(num)

    if len(set) <= num:
        return

    if num == 0:
        set.clear()
        return

    if len(set) == 0:
        return

    # print "set: %s" % `set`
    winkeys = []
    winvals = []
    min = -sys.maxint - 1
    for k, v in set.items():
        assert v > (-sys.maxint - 1)
        if v > min:
            # b["onepass"] = 0
            # startt("onepass")
            # print "k: %s, v: %s" % (`k`, `v`)
            rite = len(winvals)
            left = 0
            while left < rite:
                mid = (left + rite) / 2
                if v > winvals[mid]:
                    rite = mid
                else:
                    left = mid + 1
            winvals.insert(left, v)
            winkeys.insert(left, k)
            if len(winvals) > num:
                del winvals[-1]
                del winkeys[-1]
                min = winvals[-1]
            # stopt("onepass")

    # b["recon"] = 0
    # startt("recon")
    set.clear()
    map(operator.setitem, [set]*len(winvals), winkeys, winvals)
    # stopt("recon")

    assert len(set) == num, "len(set): %s, num: %s, set: %s, winners: %s" % (`len(set)`, `num`, `set`, `winners`)

def _skim_with_partial_qsort(set, num):
    """
    This destroys `set'.

    Throw out all but the top `num' items.

    This does a partial quick-sort which is O(2N) compared to doing a full sort and then keeping the top N, which is O(N log N).

    This is faster than `_skim_with_builtin()', but it is complicated and potentially brittle in the presence of different statistical distributions, weird values of `num', etc.

    @precondition: `num' must be non-negative.: num >= 0: "num: %s" % humanreadable.hr(num)
    """
    assert num >= 0, "precondition: `num' must be non-negative." + " -- " + "num: %s" % humanreadable.hr(num)

    if len(set) <= num:
        return

    if num == 0:
        set.clear()
        return

    if len(set) == 0:
        return

    torv = 0 # "throw out radixval";  Must be set to `false' initially, then it toggles when each radixval is hit.  This is to prevent the infinite loop in which you have N elements with all the same value, and you are trying to get K elements; K < N.
    other = None
    while len(set) > num:
        origlenset=len(set)
        ix = 1.0 - float(num) / len(set)
        if (len(set) <= 1024) or ((len(set) <= 65536) and (abs(ix-0.5) < 0.3)):
            _skim_with_builtin(set, num)
            assert len(set) == num, "len(set): %s, num: %s" % (`len(set)`, `num`)
            return

        other = {} # (Throw away previous `other'.)

        items = set.items()

        rs = []
        for i in range(15):
            rs.append(whrandom.choice(items)[1])

        i = int(ix * len(rs))
        if i > 7:
            i = i - 1
        elif i < 7:
            i = i + 1

        assert i < len(rs), "i: %s, rs: %s" % (humanreadable.hr(i), humanreadable.hr(rs))
        assert i >= 0, "i: %s" % humanreadable.hr(i)
        rs.sort()
        radix = rs[i]

        for key, val in items:
            if val < radix:
                other[key] = val
                del set[key]
            elif val == radix:
                if torv:
                    other[key] = val
                    del set[key]
                torv = not torv

    assert len(set) <= num
    assert other is None or (len(other) + len(set) >= num), "len(other): %s, len(set): %s, num: %s" % (`len(other)`, `len(set)`, `num`)

    if (len(set) < num) and (other):
        # If we have too few, skim the top from `other' and move them into `set'.
        _skim_with_partial_qsort(other, num - len(set))
        assert len(other) == (num - len(set)), "len(other): %s, num: %s, len(set): %s" % (`len(other)`, `num`, `len(set)`)
        set.update(other)

    assert len(set) == num, "len(set): %s, num: %s" % (`len(set)`, `num`)
    return

skim = _skim_with_partial_bisort

def int_log_base_2(x):
    """
    Rounds down.

    @precondition: `x' must be greater than or equal to 1.0.: x >= 1.0: "x: %s" % humanreadable.hr(x)
    """
    assert x >= 1.0, "precondition: `x' must be greater than or equal to 1.0." + " -- " + "x: %s" % humanreadable.hr(x)

    # Is it faster to use math.log and convert the result to base 2, or is it faster to do this?  Probably the former, but oh well...  --Zooko 2001-02-18
    y = 1
    res = -1
    while y <= x:
        res = res + 1
        y = y * 2

    return res

def int_log_base_10(x):
    """
    Rounds down.

    @precondition: `x' must be greater than or equal to 1.0.: x >= 1.0: "x: %s" % humanreadable.hr(x)
    """
    assert x >= 1.0, "precondition: `x' must be greater than or equal to 1.0." + " -- " + "x: %s" % humanreadable.hr(x)

    # Is it faster to use len(str()), or is it faster to do this?  Probably the former, but oh well...  --Zooko 2001-02-18
    y = 1
    res = -1
    while y <= x:
        res = res + 1
        y = y * 10

    return res

class Timer:
    """
    A simple class to be used for timing of operations.
    """
    def __init__(self, start=None):
        self._result = None
        if start: self.start()
    def start(self):
        """starts the timer"""
        self._result = None
        self._start_time = time.time()
    def stop(self):
        """returns the time delta between now and when start was called"""
        self._stop_time = time.time()
        self._result = max(0.0000001, self._stop_time - self._start_time)
        return self._result
    def get(self):
        """returns the elapsed time between the most recent start and stop calls or the time elapsed if stop has not been called"""
        if self._result is not None:
            return self._result
        else:
            return max(0.0000001, time.time() - self._start_time)


class Counter:
    """
    A simple thread-safe counter.

    We could use operator overloading to create a class
    which acts like a number but is threadsafe, but this
    class requires explicit yet simple use, which seems
    preferable.
    """
    def __init__(self, value=0):
        self.v = value
        self.l = threading.Lock()
    def get(self):
        self.l.acquire()
        v = self.v
        self.l.release()
        return v
    def set(self, value):
        self.l.acquire()
        self.v = value
        self.l.release()
    def inc(self, amount=1):
        self.l.acquire()
        try:
            self.v = self.v + amount
        finally:
            self.l.release()
        return self.v
    def dec(self, amount=1):
        return self.inc(0 - amount)

class SimpleCounter:
    """
    A simple non-thread-safe counter.

    We could use operator overloading to create a class
    which acts like a number but is threadsafe, but this
    class requires explicit yet simple use, which seems
    preferable.
    """
    def __init__(self, value=0):
        self.v = value
    def get(self):
        v = self.v
        return v
    def set(self, value):
        self.v = value
    def inc(self, amount=1):
        self.v = self.v + amount
        return self.v
    def dec(self, amount=1):
        return self.inc(0 - amount)


class StackTree:
    """
    A dict with a stack representing the current path.
    This is handy for using the xml.sax style of parser
    to create a python dict.
    """
    def __init__(self):
        self.dict = {}
        self._path = []
    def get_current(self):
        current = self.dict
        for key in self._path:
            current = current[key]
        return current
    def push(self, name, value=None):
        if value == None:
            value = {}
        self.get_current()[name] = value
        self._path.append(name)
    def pop(self):
        return self._path.pop()

def common_substring_length(a, b, bitunits=true):
    """
    Returns the length of the common leading substring of a and b.
    If bitunits is true, this length is in bits, else it is
    in bytes.
    """
    count = 0
    maxlen = max(len(a), len(b))

    while count < maxlen and a[count] == b[count]:
        count = count + 1

    if bitunits:
        i = count
        count = count * 8
        if i < maxlen:
            # Does this craziness work?!  I think so.  -Neju 2001-02-18
            count = count + (7 - int_log_base_2(ord(a[i]) ^ ord(b[i])))

    return count

def zip(*args):
    """
    This is a naive implementation that does AFAICT the same thing that 
    the python 2.0 builtin `zip()' does.
    """
    res = []
    lenres = None

    for arg in args:
        if (lenres is None) or (len(arg) < lenres):
            lenres = len(arg)

    for i in range(lenres):
        newtup = []
        for arg in args:
            newtup.append(arg[i])
        res.append(tuple(newtup))

    return res

irange = lambda seq: zip(range(len(seq)), seq)

def doit(func):
    return func()

def coverageit(func):
    global tracedone
    tracedone.clear()
    debugprint("xxxxxxxxxxxxxxxxxxxx %s\n", args=(func,), v=0, vs="debug")
    coverage.the_coverage.start()
    # run the new command using the given trace
    try:
        result = apply(func)
        debugprint("yyyyyyyyyyyyyyyyyyyy %s\n", args=(func,), v=0, vs="debug")
    finally:
        coverage.the_coverage.stop()
        tmpfname = fileutil.mktemp(prefix=humanreadable.hr(func))

        debugprint("zzzzzzzzzzzzzzzzzzzz %s\n", args=(func,), v=0, vs="debug")

        # make a report, telling it where you want output
        res = coverage.the_coverage.analysis('/home/zooko/playground/evil-SF-unstable/common/MojoTransaction.py')
        print res
        tracedone.set()
    return result


def traceorcountit(func, dotrace, docount, countfuncs):
    global tracedone
    tracedone.clear()
    debugprint("xxxxxxxxxxxxxxxxxxxx %s, countfuncs: %s\n", args=(func, countfuncs,), v=0, vs="debug")
    t = trace.Trace(trace=dotrace, count=docount, countfuncs=countfuncs, infile="/tmp/trace", outfile="/tmp/trace", ignoredirs=(sys.prefix, sys.exec_prefix,))
    # run the new command using the given trace
    try:
        result = t.runfunc(func)
        debugprint("yyyyyyyyyyyyyyyyyyyy %s\n", args=(func,), v=0, vs="debug")
    finally:
        tmpfname = fileutil.mktemp(prefix=humanreadable.hr(func))

        debugprint("zzzzzzzzzzzzzzzzzzzz %s\n", args=(func,), v=0, vs="debug")

        # make a report, telling it where you want output
        t.results().write_results(show_missing=1)
        tracedone.set()
    return result

def traceit(func):
    return traceorcountit(func, dotrace=true, docount=false, countfuncs=false)

def countit(func):
    return traceorcountit(func, dotrace=false, docount=true, countfuncs=false)

def traceandcountit(func):
    return traceorcountit(func, dotrace=true, docount=true, countfuncs=false)

def countfuncsit(func):
    return traceorcountit(func, dotrace=false, docount=false, countfuncs=true)

def _dont_enable_if_you_want_speed_profit(func):
    result = None
    p = profile.Profile()
    try:
        debugprint("xxxxxxxxxxxxxxxxxxxx %s\n", args=(func,), v=0, vs="debug")
        result = p.runcall(func)
        debugprint("yyyyyyyyyyyyyyyyyyyy %s\n", args=(func,), v=0, vs="debug")
    finally:
        tmpfname = fileutil.mktemp(prefix=humanreadable.hr(func))

        debugprint("zzzzzzzzzzzzzzzzzzzz %s\n", args=(tmpfname,), v=0, vs="debug")

        p.dump_stats(tmpfname)
        p = None
        del p

        stats = pstats.Stats(tmpfname)
        stats.strip_dirs().sort_stats('time').print_stats()
    return result

def is_int(thing):
    return type(thing) in (types.IntType, types.LongType)

def is_number(thing):
    return type(thing) in (types.IntType, types.LongType, types.FloatType,)

def is_number_or_None(thing):
    return (thing is None) or (type(thing) in (types.IntType, types.LongType, types.FloatType,))

#if confman.is_true_bool(('PROFILING',)):
#    profit = _dont_enable_if_you_want_speed_profit
#else:
#    profit = doit
# profit = coverageit

global tracedone
tracedone = threading.Event()
tracedone.set() # if we actually do some tracing, we'll clear() it first then set() it afterwards.  That way you can wait() on this Event whether or not we do tracing.

# xor function:
xor = lambda a, b : (a and not b) or (not a and b)
xor.__doc__ = "The xor function is a logical exclusive-or."

def get_path_size(path):
    """
    If path is a non-directory, this returns the file's size.
    If path is a directory, this returns the sum of a recursive call on each path in that directory.
    If there's any OSError, return None
    """
    # XXX Keep an eye out for a standard library way of doing this.  os.path.walk seemed too restrictive.
    try:
        if os.path.isdir(path):
            return os.path.getsize(path) + reduce(lambda x, y: long(x)+y, filter(None, map(get_path_size, map(lambda p, base=path, os=os: os.path.join(base, p), os.listdir(path)))), 0)
        else:
            return os.path.getsize(path)
    except OSError:
        return None
        
def callback_wrapper(func, args=(), kwargs={}, defaultreturnval=None):
    """
    Use this with all callbacks to aid debugging.  When there is a TypeError it shows which function was being called
    (as opposed to just having a reference named something like "cb").

    @param defaultreturnval: if `func' is None, then this will be returned;  You probably want `None'.
    """
##    if debugstream.max_verbosity >= 22:   # because traceback.extract_stack() is slow
##        debugprint("DEBUG: about to call wrapped method: %s(%s, %s) from %s\n", args=(func, args, kwargs, traceback.extract_stack()), v=22, vs="debug")
##        # really, really, egregiously verbose.  Use this if you basically want a log containing a substantial fraction of all function calls made during the course of the program.  --Zooko 2000-10-08 ### for faster operation, comment this line out.  --Zooko 2000-12-11 ### for faster operation, comment this line out.  --Zooko 2000-12-11

    if (not func):
        return defaultreturnval

#     try:
    try:
        return apply(func, args, kwargs)
    except TypeError, description:
        debugprint('got a TypeError, func was %s, args was %s, kwargs was %s\n' % (`func`, `args`, `kwargs`))
        raise
##    finally:
##        if debugstream.max_verbosity >= 23:   # because traceback.extract_stack() is slow
##            debugprint("DEBUG: done calling wrapped method: %s(%s, %s) from %s\n", args=(func, args, kwargs, traceback.extract_stack()), v=23, vs="debug")
##            # really, really, egregiously verbose.  Use this if you basically want a log containing a substantial fraction of all function calls made during the course of the program.  --Zooko 2000-10-08 ### for faster operation, comment this line out.  --Zooko 2000-12-11

def _cb_warper(icb=None):
    """
    This crazy function is for waiting for a callback and then examining the results.  (Just for
    testing.  Using this in production code is a no-no just like using "initiate_and_wait()".)

    Anyway, `_cb_warper()' takes a function.  It returns a tuple of `res', `reskw', `doneflag',
    and `_wcb'.  You pass `_wcb' as your callback, then call `doneflag.wait()'.  When your
    `wait()' call returns, you can look at `res' and `reskw' to see all of the values passed to
    the callback function.  Also your `icb' function, if it exists, got called before the
    `wait()' returned.

    @precondition: `icb' is None or callable.: (not icb) or callable(icb): "icb: [%s]" % humanreadable.hr(icb)
    """
    assert (not icb) or callable(icb), "`icb' is None or callable." + " -- " + "icb: [%s]" % humanreadable.hr(icb)

    res=[]
    reskw={}
    doneflag = threading.Event()

    # this is a callable class, an instance of which will be used as the _wcb callback that we return
    class wrapped_callback:
        def __init__(self, icb, res, reskw, doneflag):
            self.icb = icb
            self.res = res
            self.reskw = reskw
            self.doneflag = doneflag
        def __call__(self, *args, **kwargs):
            resu = None
            if self.icb:
                resu = apply(self.icb, args, kwargs)
            self.res.extend(list(args))
            self.reskw.update(kwargs)
            self.doneflag.set()
            return resu

    return res, reskw, doneflag, wrapped_callback(icb, res, reskw, doneflag)

def cherrypick_best_from_list(lst, num):
    """
    Returns a list of length min(len(lst), num) items that have been
    picked randomly from the list with an exponential distribution,
    preferring to pick ones from the head of the list over the tail.

    SIDE EFFECT: Removes picked items from lst.
    """
    assert num >= 0
    cherry_list = []
    while lst and len(cherry_list) < num:
        idx = whrandom.randint(0, whrandom.randint(0, len(lst)-1))
        cherry_list.append(lst[idx])
        del lst[idx]
    return cherry_list

def rotatelist(lst):
    """
    Returns a new list that has been rotated a random amount
    """
    if len(lst) > 1:
        rotation = whrandom.randint(0, len(lst) - 1)
        return lst[rotation:] + lst[:rotation]
    else:
        return copy.copy(lst)


def shuffleList(list):
    """
    returns a new list with the items shuffled
    his isn't all that efficient (especially on space)
    """
    l = list[:] # make a copy so nothing unexpected happens to the caller
    shuffled = []
    length = len(l)
    for i in range(length):
        x = whrandom.randint(0, (length - 1) - i)
        shuffled.append(l[x])
        del l[x]
    return shuffled

def update_weighted_sample(history, newvalue, historyweight=None,default_value=None):
    """
    @param history: (mean, sigma, mean_squares,)
    @param newvalue: new statistic to add to history with weighted deviation
    @param historyweight: 0.0 = ignore history, 1.0 = ignore new sample
    @param default_value: what to use when history param is None

    @return: updated history (mean, sigma, mean_squares,)
    """
    stat = history
    if stat is None:
        if default_value is None:
            stat = (float(newvalue), 0, float(newvalue)*float(newvalue))
        else:
            stat = (float(default_value), 0, float(default_value)*float(default_value))
    mean = float((historyweight * stat[0]) + ((1.0 - historyweight)*newvalue))
    mean_squares = float((historyweight * stat[2]) + ((1.0 - historyweight)*newvalue*newvalue))
    sigma_squared = mean_squares - mean*mean
    if sigma_squared > 0.0:
        sigma = math.sqrt(sigma_squared)
    else:
        # sigma = 0.0
        # ? I'm thinking we want to be a lot more lenient when we don't have enough samples yet.  --Zooko 2001-07-10
        sigma = math.sqrt(abs(mean))
    return (mean,sigma,mean_squares)
    

