#!/usr/bin/env python
#
#  Copyright (c) 2001 Autonomous Zone Industries
#  Copyright (c) 2002 Bryce "Zooko" Wilcox-O'Hearn
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.
#
__cvsid = '$Id: version.py,v 1.2 2002/11/22 04:56:19 zooko Exp $'

# standard modules
import string

# pyutil modules
from pyutil import VersionNumber

# major, minor, micro (== bugfix release), nano (== not-publically-visible patchlevel), flag (== not-publically-visible UNSTABLE or STABLE flag)
versiontup = (0, 0, 3, 6,)
versionflag = 'UNSTABLE'
versionobj = VersionNumber.VersionNumber(string.join(map(str, versiontup), '.') + '-' + versionflag)
versionstr_full = versionobj.full_string()
versionstr = versionobj.terse_string()
