#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: MojoErrors.py,v 1.3 2003/01/08 13:14:09 myers_carpenter Exp $"

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


