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
__cvsid = '$Id: confutils.py,v 1.5 2002/09/28 17:45:36 zooko Exp $'


# standard modules
import os.path
import sys
import types

# pyutil modules
from pyutil.config import DEBUG_MODE
from pyutil.debugprint import debugprint

true = 1
false = 0

from egtp.mojostd import confman, platform

