#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.

__revision__ = "$Id: tripledescbc.py,v 1.3 2002/12/02 19:58:55 myers_carpenter Exp $"

from egtp.crypto import evilcryptopp

__doc__ = evilcryptopp._tripledescbc_doc
new = evilcryptopp._tripledescbc_new
Error = evilcryptopp.TripleDESCBCError
