#  Copyright (c) 2003 Myers Carpenter
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.

__revision__ = "$Id: aesctr.py,v 1.1 2003/03/22 20:51:00 myers_carpenter Exp $"

from egtp.crypto import evilcryptopp

__doc__ = evilcryptopp._aesctr_doc
new = evilcryptopp._aesctr_new
Error = evilcryptopp.AESCTRError
