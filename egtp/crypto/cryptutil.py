#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: cryptutil.py,v 1.5 2002/12/14 04:50:21 myers_carpenter Exp $"

import sha

from pyutil.xor.xor import xor

from egtp.crypto import tripledescbc, randsource
from egtp import hashrandom, EGTPConstants

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


class cryptutilError(StandardError):
    pass
    
class OAEPError(cryptutilError):
    pass


def hmac(key, message):
    SIZE_OF_SHA1_INPUT = 64
    ipad = '\x36' * SIZE_OF_SHA1_INPUT
    opad = '\x5C' * SIZE_OF_SHA1_INPUT

    if len(key)>SIZE_OF_SHA1_INPUT:
        key = sha.sha(key).digest()

    key = key + '\000'*(SIZE_OF_SHA1_INPUT - len(key))

    a = xor(key, ipad)
    h1 = sha.sha(a + message).digest()
    b = xor(key, opad)
    h2 = sha.sha(b + h1).digest()

    return h2

def hmacish(key, message):
    hasher = sha.sha()
    hasher.update(key)
    hasher.update(message)
    hasher2 = sha.sha()
    hasher2.update(message)
    hasher2.update(hasher.digest())
    return hasher2.digest()

def mgf1(seed, intendedlength):
    """
    Mask Generation Function 1 MGF1 from PKCS #1 v2.
    """
    # I _think_ that MGF1 is the same as our hashrandom.SHARandom()...
    # XXX !!! We should verify this hypothesis...  --Zooko 2000-07-29
    s = hashrandom.SHARandom(seed)
    return s.get(intendedlength)

def oaep(m, emLen, p=""):
    """
    OAEP from PKCS #1 v2.  Not bitwise correct -- different encodings, length granularity, etc.

    Remember that modvals prefer an input of size SIZE_OF_MODULAR_VALUES, where oaep() returns a
    padded thingie of size SIZE_OF_MODULAR_VALUES - 1.  The thing to do is prepend a 0 byte
    before passing to modval.

    @param m: the message to be encoded
    @param emLen: the intended length of the padded form (should be EGTPConstants.SIZE_OF_MODULAR_VALUES)
    @param p: encoding parameters; we use empty string

    @precondition: The length of `p' must be less than or equal to the input limitation for SHA-1.: len(p) <= ((2^61)-1): "p: %s" % humanreadable.hr(p)
    @precondition: `emLen' must be big enough.: emLen >= (2 * EGTPConstants.SIZE_OF_UNIQS) + 1: "emLen: %s, EGTPConstants.SIZE_OF_UNIQS: %s" % (humanreadable.hr(emLen), humanreadable.hr(EGTPConstants.SIZE_OF_UNIQS))
    @precondition: The length of `m' must be small enough to fit.: len(m) <= (emLen - (2 * EGTPConstants.SIZE_OF_UNIQS) - 1): "emLen: %s, EGTPConstants.SIZE_OF_UNIQS: %s" % (humanreadable.hr(emLen), humanreadable.hr(EGTPConstants.SIZE_OF_UNIQS))
    """
    assert len(p) <= ((2^61)-1), "The length of `p' must be less than or equal to the input limitation for SHA-1." + " -- " + "p: %s" % humanreadable.hr(p)
    assert emLen >= (2 * EGTPConstants.SIZE_OF_UNIQS) + 1, "`emLen' must be big enough." + " -- " + "emLen: %s, EGTPConstants.SIZE_OF_UNIQS: %s" % (humanreadable.hr(emLen), humanreadable.hr(EGTPConstants.SIZE_OF_UNIQS))
    assert len(m) <= (emLen - (2 * EGTPConstants.SIZE_OF_UNIQS) - 1), "The length of `m' must be small enough to fit." + " -- " + "emLen: %s, EGTPConstants.SIZE_OF_UNIQS: %s" % (humanreadable.hr(emLen), humanreadable.hr(EGTPConstants.SIZE_OF_UNIQS))

    hLen = EGTPConstants.SIZE_OF_UNIQS

    # mojolog.write("mojoutil.oaep(): -- -- -- -- -- -- m: %s\n" % humanreadable.hr(m))
    # mojolog.write("mojoutil.oaep(): -- -- -- -- -- -- emLen: %s\n" % humanreadable.hr(emLen))
    ps = '\000' * (emLen - len(m) - (2 * hLen) - 1)
    # mojolog.write("mojoutil.oaep(): -- -- -- -- -- -- ps: %s\n" % humanreadable.hr(ps))
    pHash = sha.new(p).digest()
    db = pHash + ps + '\001' + m
    # mojolog.write("mojoutil.oaep(): -- -- -- -- -- -- db: %s\n" % humanreadable.hr(db))
    seed = randsource.get(hLen)
    dbMask = mgf1(seed, emLen - hLen)
    maskedDB = xor(db, dbMask)
    seedMask = mgf1(maskedDB, hLen)
    maskedSeed = xor(seed, seedMask)
    em = maskedSeed + maskedDB

    assert len(em) == emLen

    # mojolog.write("mojoutil.oaep(): -- -- -- -- -- -- em: %s\n" % humanreadable.hr(em))
    return em

def oaep_decode(em, p=""):
    """
    Remember that modvals output cleartext of size SIZE_OF_MODULAR_VALUES, where oaep() needs a
    padded thingie of size SIZE_OF_MODULAR_VALUES - 1.  The thing to do is pop off the prepended
    0 byte before passing to oaep_decode().  (Feel free to check whether it is zero and raise a
    bad-encoding error if it isn't.)

    @param em: the encoded message
    @param p: encoding parameters; we use empty string

    @precondition: The length of `p' must be less than or equal to the input limitation for SHA-1.: len(p) <= ((2^61)-1)
    """
    assert len(p) <= ((2^61)-1), "The length of `p' must be less than or equal to the input limitation for SHA-1."

    # mojolog.write("mojoutil.oaep_decode(): -- -- -- -- -- -- em: %s\n" % humanreadable.hr(em))

    if len(em) < (2 * EGTPConstants.SIZE_OF_UNIQS) + 1:
        raise OAEPError, "decoding error: `em' is not long enough."

    hLen = EGTPConstants.SIZE_OF_UNIQS
    maskedSeed = em[:hLen]
    # mojolog.write("mojoutil.oaep_decode(): -- -- -- -- -- -- maskedSeed: %s\n" % humanreadable.hr(maskedSeed))
    maskedDB = em[hLen:]
    # mojolog.write("mojoutil.oaep_decode(): -- -- -- -- -- -- maskedDB: %s\n" % humanreadable.hr(maskedDB))
    assert len(maskedDB) == (len(em) - hLen)
    seedMask = mgf1(maskedDB, hLen)
    # mojolog.write("mojoutil.oaep_decode(): -- -- -- -- -- -- seedMask: %s\n" % humanreadable.hr(seedMask))
    seed = xor(maskedSeed, seedMask)
    # mojolog.write("mojoutil.oaep_decode(): -- -- -- -- -- -- seed: %s\n" % humanreadable.hr(seed))
    dbMask = mgf1(seed, len(em) - hLen)
    # mojolog.write("mojoutil.oaep_decode(): -- -- -- -- -- -- dbMask: %s\n" % humanreadable.hr(dbMask))
    db = xor(maskedDB, dbMask)
    # mojolog.write("mojoutil.oaep_decode(): -- -- -- -- -- -- db: %s\n" % humanreadable.hr(db))
    pHash = sha.sha(p).digest()

    pHashPrime = db[:hLen]

    # Now looking for `ps'...
    i = hLen
    while db[i] == '\000':
        if i >= len(db):
            raise OAEPError, "decoding error: all 0's -- no m found"

        i = i + 1

    if db[i] != '\001':
        raise OAEPError, "decoding error: no 1 byte separator found before m -- db: %s, i: %s, db[i:]: %s\n" % (str(db), str(i), str(db[i:]))

    m = db[i+1:] # This is here instead of after the check because that's the way it is written in the PKCS doc.  --Zooko 2000-07-29

    if pHash != pHashPrime:
        raise OAEPError, "decoding error: pHash: %s != pHashPrime: %s" % tuple(map(humanreadable.hr, (pHash, pHashPrime,)))

    return m

def get_rand_lt_n(seed, n):
    """
    @param n: a modval

    This function can take an average of 2^(K+1) time, where K is the number of leading 0 bits
    in the most significant places in `n'.  In all of our current code, K == 0 (modvals are
    always chosen to have a 1-bit in the most significant place.)
    """
    old = n.get_value()

    r = hashrandom.SHARandom(seed)
    x = r.get(len(n.get_modulus()))

    while modval.verify_key_and_value(n.get_modulus(), x) != None:
        x = r.get(len(n.get_modulus()))

    return x

def get_rand_lt_n_with_prepended_0(seed, n):
    """
    @param n: a modval
    """
    r = hashrandom.SHARandom(seed)
    return '\000' + r.get(len(n.get_modulus()) - 1)

