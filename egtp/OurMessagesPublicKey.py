#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: OurMessagesPublicKey.py,v 1.3 2002/12/02 19:58:50 myers_carpenter Exp $"

from egtp.DataTypes import UNIQUE_ID, ANY, ASCII_ARMORED_DATA, NON_NEGATIVE_INTEGER, MOD_VAL, INTEGER, ListMarker, OptionMarker


# Public key for communications template.
PKFC_TEMPL={ 'key header': { 'type': "public", 'cryptosystem': ANY, 'usage': "only for communication security" }, 'key values': {}}

# Public RSA key for communications template.
PRKFC_TEMPL={ 'key header': { 'type': "public", 'cryptosystem': "RSA", 'usage': "only for communication security" }, 'key values': {'public modulus': MOD_VAL, 'public exponent': NON_NEGATIVE_INTEGER}}


