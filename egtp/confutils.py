#!/usr/bin/env python
#
#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.
#
# A module containing user-configuration utilities.
# (And it's pronounced confu-tils, where "confu" sounds like the beginning of "confusion".) 
#
# BirthDate: 2000-06-08
# CVS:
__cvsid = '$Id: confutils.py,v 1.2 2002/07/27 00:31:22 myers_carpenter Exp $'


# standard modules
import os.path
import sys
import types

# pyutil modules
from pyutil.config import DEBUG_MODE
from pyutil.debugprint import debugprint
from pyutil import humanreadable

true = 1
false = 0

# our modules
from egtp.mojostd import CRYPTOPP_VERSION_STR, confdefaults,  platform_map, platform, gen_per_kb_price_dict, DictFileException, lines_to_dict, dict_to_lines, ConfManager, confman


if int(confman.get('MAX_VERBOSITY', 0)) >= 6:
    # Only enable automatic mdecoding of strings in debugprints if we have a high verbosity level; these are extremely
    # CPU, memory cache, and memory bus intensive.
    debugprint("WARNING: high verbosity level, performance will be impacted!\n")
    humanreadable.brepr.enable_mdecode = true
    # NOTE: if config.DEBUG evaluates to true then mdecoding will be enabled regardless
    # of verbosity level.

def do_tests():
    import RunTests
    RunTests.runTests(["confutils"])
    return
    
# XXX won't this cause duplicate tests as they get run from mojostd?
mojo_test_flag = 1

def run(argv):
    if len(argv) > 1:
        if argv[1] == "test":
            do_tests()
        elif argv[1] == "dump":
            sys.stdout.writelines(dict_to_lines(confman.dict))
        else:
            print 'Unknown option "%s".' % argv[1]
    else:
        print 'Config file "%s" updated.' % os.path.expandvars(confman.dict["PATH"]["BROKER_CONF"])

if __name__ == '__main__':
    run(sys.argv)


## These functions are used to ensure that retrieved prices from confutils
## are always integers.  yeah, it's ugly
def _integerizePriceMap(tmap):
    for key in tmap.keys():
        tmap[key] = int(round(float(tmap[key])))
    return tmap

def integerizePrice(price):
    if(type(price) == types.DictType):
        return _integerizePriceMap(price)
    return int(round(float(price)))