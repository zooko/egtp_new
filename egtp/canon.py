#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: canon.py,v 1.3 2002/12/02 19:58:51 myers_carpenter Exp $"

from egtp.mojostd import _canon, strip_leading_zeroes, is_canonical, is_canonical_modval, is_canonical_uniq
from egtp import std

std.is_canonical_modval = is_canonical_modval
std.is_canonical_uniq = is_canonical_uniq

