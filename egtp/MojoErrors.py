#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: MojoErrors.py,v 1.2 2002/12/02 19:58:48 myers_carpenter Exp $"

import exceptions

# throws by anything which doesn't like what was passed to it
class DataError(exceptions.StandardError):
    pass

# thrown by MojoMessage
class MojoMessageError(DataError):
    pass

# thrown by DataTypes
class BadFormatError(DataError):
    pass

# throws by things which do block reassembly
class ReassemblyError(IOError):
    pass

