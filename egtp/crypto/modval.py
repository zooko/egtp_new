#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: modval.py,v 1.4 2002/12/02 19:58:55 myers_carpenter Exp $"

from egtp.crypto import evilcryptopp, randsource

__doc__ = evilcryptopp._modval_doc
verify_key_and_value = evilcryptopp._modval_verify_key_and_value
verify_key = evilcryptopp._modval_verify_key
new = evilcryptopp._modval_new
new_random = evilcryptopp._modval_new_random
new_serialized = evilcryptopp._modval_new_serialized
Error = evilcryptopp.ModValError
