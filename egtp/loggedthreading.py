#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: loggedthreading.py,v 1.6 2003/02/23 16:18:30 myers_carpenter Exp $"

# standard modules
from threading import *
import traceback

# pyutil modules
from pyutil.debugprint import debugprint, debugstream

# remove stuff from our namespace to allow a polite 'from X import *'
_print_exc = traceback.print_exc
del traceback
_debugprint = debugprint
_debugstream = debugstream
del debugprint, debugstream


class LoggedThread(Thread):
    """
    A descendent of threading.Thread() that overrides the run() method
    to log all thread terminating exceptions using debugprint rather
    than normal stderr as the threading module does.
    NOTE: this won't be useful if you override the run() method.
    """
    def run(self):
        try:
            Thread.run(self)
        except:
            _debugprint('Exception in thread \'%s\':\n' % (self.getName(),), vs='ERROR')
            _print_exc(file=_debugstream)

