#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: cryptutil.py,v 1.3 2002/12/02 19:58:55 myers_carpenter Exp $"

# egtp modules
from egtp.mojostd import cryptutilError, OAEPError, oaep, oaep_decode, xor, hmac, hmacish, mgf1, get_rand_lt_n, get_rand_lt_n_with_prepended_0

from egtp.crypto import tripledescbc
from egtp import hashrandom



def hashexpand(inpstr, expbytes, HRClass=hashrandom.SHARandom):
    return HRClass(inpstr).get(expbytes)

def dummy_encrypt(cleartext, key):
    return cleartext

def dummy_decrypt(cleartext, key):
    return cleartext

def desx_encrypt(cleartext, key):
    """
    This is a very thin wrapper over `tripledescbc', providing a small simplification of
    combining key and iv into one `key', and providing a functionish rather than objectish
    interface.
    """
    # Could try to assert that `key' is long and probably random...  --Zooko 2000-09-22

    return tripledescbc.new(hashrandom.hashexpand(key + 'key', 24)).encrypt(hashrandom.hashexpand(key + 'iv', 8), cleartext)

def desx_decrypt(ciphertext, key):
    """
    This is a very thin wrapper over `tripledescbc', providing a small simplification of
    combining key and iv into one `key', and providing a functionish rather than objectish
    interface.
    """
    # Could try to assert that `key' is long and probably random...  --Zooko 2000-09-22

    return tripledescbc.new(hashrandom.hashexpand(key + 'key', 24)).decrypt(hashrandom.hashexpand(key + 'iv', 8), ciphertext)


