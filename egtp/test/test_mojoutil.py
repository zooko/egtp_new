#!/usr/bin/env python

__author__   = 'EGFABT'
__revision__ = "$Id: test_mojoutil.py,v 1.1 2002/12/02 19:58:56 myers_carpenter Exp $"

import unittest, whrandom

from egtp import mojoutil

true = 1
false = None

class MojoutilTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _help_test_skim(self, FUNC, SETSIZE, MAXVAL, NUMWANTED):
        whrandom.seed(0,0,0)
        d = {}
        for i in range(SETSIZE):
            d[i] = whrandom.randint(0, MAXVAL)

        db = {}
        db.update(d)

        FUNC(d, NUMWANTED)
        l = d.items()
        l.sort(lambda a, b: cmp(b[1], a[1]))

        l2 = db.items()
        l2.sort(lambda a, b: cmp(b[1], a[1]))
        l2 = l2[:NUMWANTED]

        for i in range(NUMWANTED):
            assert l[i][1] == l2[i][1], "i: %s, l: %s, l2: %s" % (`i`, `l`, `l2`)

    def _help_test_skim_2(self, FUNC):
        self._help_test_skim(FUNC, 1, 4, 0)
        self._help_test_skim(FUNC, 1, 4, 1)
        self._help_test_skim(FUNC, 2, 4, 0)
        self._help_test_skim(FUNC, 2, 4, 1)
        self._help_test_skim(FUNC, 2, 4, 2)
        self._help_test_skim(FUNC, 3, 4, 0)
        self._help_test_skim(FUNC, 3, 4, 1)
        self._help_test_skim(FUNC, 3, 4, 2)
        self._help_test_skim(FUNC, 3, 4, 3)
        self._help_test_skim(FUNC, 4, 4, 0)
        self._help_test_skim(FUNC, 4, 4, 1)
        self._help_test_skim(FUNC, 4, 4, 2)
        self._help_test_skim(FUNC, 4, 4, 3)
        self._help_test_skim(FUNC, 4, 4, 4)
        self._help_test_skim(FUNC, 10, 10, 3)
        self._help_test_skim(FUNC, 10, 1000, 3)
        self._help_test_skim(FUNC, 30, 4, 10)
        self._help_test_skim(FUNC, 100, 10, 30)
        self._help_test_skim(FUNC, 100, 1000, 30)
        self._help_test_skim(FUNC, 300, 4, 100)
        self._help_test_skim(FUNC, 3000, 1000, 100)
        self._help_test_skim(FUNC, 7000, 10000, 300)

    def test_skim(self):
        self._help_test_skim_2(FUNC=mojoutil.skim)

    def test_common_substring_length(self):
        common_substring_length = mojoutil.common_substring_length
        s = '\000\000\000'
        d = '\000\000\001'
        assert common_substring_length(s, d) == 23, "s: %s, d: %s, common_substring_length(s, d): %s" % (repr(s), repr(d), humanreadable.hr(common_substring_length(s, d)))

        s = '\000'
        d = '\001'
        assert common_substring_length(s, d) == 7, "s: %s, d: %s, common_substring_length(s, d): %s" % (repr(s), repr(d), humanreadable.hr(common_substring_length(s, d)))

        s = '\000'
        d = '\000'
        assert common_substring_length(s, d) == 8, "s: %s, d: %s, common_substring_length(s, d): %s" % (repr(s), repr(d), humanreadable.hr(common_substring_length(s, d)))

        s = '\000'
        d = '\000'
        assert common_substring_length(s, d, bitunits=false) == 1, "s: %s, d: %s, common_substring_length(s, d): %s" % (repr(s), repr(d), humanreadable.hr(common_substring_length(s, d)))

        s = '\111'
        d = '\111'
        assert common_substring_length(s, d) == 8, "s: %s, d: %s, common_substring_length(s, d): %s" % (repr(s), repr(d), humanreadable.hr(common_substring_length(s, d)))

        s = '\111' + chr(64)
        d = '\111' + chr(32)
        assert common_substring_length(s, d) == 9, "s: %s, d: %s, common_substring_length(s, d): %s" % (repr(s), repr(d), humanreadable.hr(common_substring_length(s, d)))

    """
    # not converted because I'm lazy -- icepick 2002-12-02
    # >>> please comment me out for distribution -- I am testing and benchmarking code
    BSIZES = []
    for i in range(19-4):
        BSIZES.append(2**(i+4))

    global _bench_dicts_serred 
    _bench_dicts_serred = None

    global _bench_dicts
    _bench_dicts = {}
    global _bench_dicts_bak
    _bench_dicts_bak = {}

    global FUNCS, FNAMES
    # FUNCS = [ skim, _skim_with_builtin, _skim_with_builtin_naive ]
    FUNCS = [ _skim_with_partial_bisort, skim, _skim_with_builtin, _skim_with_builtin_naive  ]
    # FUNCS = [ _skim_with_partial_bisort ]
    # FNAMES = [ "skim", "_skim_with_builtin", "_skim_with_builtin_naive" ]
    FNAMES = [ "_skim_with_partial_bisort", "skim", "_skim_with_builtin", "_skim_with_builtin_naive" ]
    # FNAMES = [ "_skim_with_partial_bisort" ]

    def _help_make_init_func(N):
        def init(N=N):
            _help_init_bench_dict(N)
        return init

    def _help_testemall():
        i = 0
        global FUNCS, FNAMES
        for FUNC in FUNCS:
            print "FUNC: %s" % FNAMES[i]
            _help_test_skim_2(FUNC=FUNC)
            i = i + 1

    def _help_benchemall():
        import benchfunc

        global FUNCS, FNAMES
        global BSIZES
        for BSIZE in BSIZES:
            print "BSIZE: %s" % BSIZE
            for BS2 in BSIZES:
                if BS2 < BSIZE / 128:
                    print "BS2: %s" % BS2
                    _help_init_bench_dict(BSIZE)
                    IF = _help_make_init_func(BSIZE)
                    i = 0
                    for FUNC in FUNCS:
                        BF = _help_make_bench_skim(FUNC, BS2)
                        REPS = ((12 - math.log(max(BSIZE, 16))) ** 2) + 1
                        # REPS = 1
                        print "FUNC: %s, REPS: %d" % (FNAMES[i], REPS)
                        benchfunc.rebenchit(BF, BSIZE, initfunc=IF, REPS=REPS)
                        i = i + 1

        global b
        print b

    def _help_init_first_bench_dict(N):
        global _bench_dicts
        global _bench_dicts_bak

        keys = _bench_dicts_bak.keys()
        keys.sort()
        _bench_dicts[N] = {}
        _bench_dicts_bak[N] = {}

        if len(keys) > 0:
            i = keys[-1]
            _bench_dicts_bak[N].update(_bench_dicts_bak[i])
        else:
            i = 0

        thisdict_bak = _bench_dicts_bak[N]
        rand = random.lognormvariate
        # rand = random.normalvariate
        while i < N:
            i = i + 1
            X = rand(0, 1)
            thisdict_bak[i] = X

    def _help_init_bench_dict(N):
        global _bench_dicts
        global _bench_dicts_bak

        if not _bench_dicts_bak.has_key(N):
            _help_init_first_bench_dict(N)
        _bench_dicts[N].update(_bench_dicts_bak[N])

    def _help_make_bench_skim(benchfunc, num):
        global _bench_dicts
        global _bench_dicts_bak

        def f(N, num=num, benchfunc=benchfunc):
            benchfunc(_bench_dicts[N], num=num)
        return f
    # <<< please comment me out for distribution -- I am testing and benchmarking code
    """

def suite():
    suite = unittest.makeSuite(MojoutilTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
