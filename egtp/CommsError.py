#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: CommsError.py,v 1.2 2002/12/02 19:58:45 myers_carpenter Exp $"

import exceptions

class Error(exceptions.StandardError): pass

class CannotSendError(Error): pass

class CannotListenError(Error): pass # for TCPCommsHandler, this means "couldn't bind to a port".

