#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: keyutil.py,v 1.2 2002/12/02 19:58:53 myers_carpenter Exp $"


# python standard modules
import re

# egtp modules
from egtp.DataTypes import ANY, MOD_VAL, NON_NEGATIVE_INTEGER, UNIQUE_ID, ASCII_ARMORED_DATA
from egtp import OurMessages, MojoMessage, idlib, mencode, mojosixbit, mojoutil
from egtp.crypto import modval, randsource

true = 1
false = 0


def pubkey_to_id(key):
    """
    @precondition: `key' is a public key in SEXP form.: publicKeyIsWellFormed(key): "key: %s" % hr(key)
    """
    assert publicKeyIsWellFormed(key), "`key' is a public key in SEXP form." + " -- " + "key: %s" % hr(key)

    if publicKeyForVerifyingTokenSignaturesIsWellFormed(key):
        return idlib.make_id(key, thingtype='token verifying public key')
    elif publicKeyForCommunicationSecurityIsWellFormed(key):
        return idlib.make_id(key, thingtype='comms public key')
    else:
        return idlib.make_id(key, thingtype='public key')

#  This file is licensed under the
def getModulusFromPublicKey(key) :
    dict = mencode.mdecode(key)
    return mojosixbit.a2b(dict['key values']['public modulus'])

def makePublicRSAKeyForVerifyingTokenSignatures(keyMV):
    """
    @param keyMV: the key in a modval instance

    @return: the Mojo encoding of the key
    """
    return mencode.mencode({ 'key header': { 'type': "public", 'cryptosystem': "RSA", 'usage': "only for verifying token signatures", 'value of signed token': { 'currency': "Mojo Test Points", 'amount': "16" } }, 'key values': { 'public modulus': mojosixbit.b2a(keyMV.get_modulus()), 'public exponent': repr(keyMV.get_exponent()) }})


def makePublicRSAKeyForCommunicating(keyMV):
    return mencode.mencode({ 'key header': { 'type': "public", 'cryptosystem': "RSA", 'usage': "only for communication security" }, 'key values': { 'public modulus': mojosixbit.b2a(keyMV.get_modulus()), 'public exponent': repr(keyMV.get_exponent()) }})

   
def makeRSAPublicKeyMVFromSexpString(keySexpStr):
    """
    @param keySexpStr: RSA public key in MojoMessage format

    @return: modval instance containing the modulus and exponent of `keySexpStr'

    @precondition: `keySexpStr' is well-formed RSA public key.: publicRSAKeyIsWellFormed(keySexpStr): "keySexpStr: %s" % hr(keySexpStr)
    @precondition: `keySexpStr' is sane.: publicRSAKeyIsSane(keySexpStr): "keySexpStr: %s" % hr(keySexpStr)
    """
    assert publicRSAKeyIsWellFormed(keySexpStr), "`keySexpStr' is well-formed RSA public key." + " -- " + "keySexpStr: %s" % hr(keySexpStr)
    assert publicRSAKeyIsSane(keySexpStr), "`keySexpStr' is sane." + " -- " + "keySexpStr: %s" % hr(keySexpStr)

    ed = mencode.mdecode(keySexpStr)

    return modval.new(mojosixbit.a2b(ed['key values']['public modulus']), long(ed['key values']['public exponent']))


def publicRSAKeyIsSane(keySexpStr):
    """
    @param keySexpStr: public key (in an s-expression string with accompanying meta-data)

    @return: `true' if and only if `keySexpStr' is a correctly formed MojoMessage of an RSA public key for verifying token signatures which also satisfies a few mathematical sanity checks

    @precondition: `keySexpStr' is well-formed.: publicRSAKeyIsWellFormed(keySexpStr): "keySexpStr: %s" % hr(keySexpStr)
    """
    assert publicRSAKeyIsWellFormed(keySexpStr), "`keySexpStr' is well-formed." + " -- " + "keySexpStr: %s" % hr(keySexpStr)

    ed = mencode.mdecode(keySexpStr)

    keyMV = modval.new(mojosixbit.a2b(ed['key values']['public modulus']), long(ed['key values']['public exponent']))
       
    return modval.verify_key(keyMV.get_modulus()) == None


def keyIsWellFormed(keySexpStr):
    """
    @param keySexpStr: key in an s-expression string with accompanying meta-data

    @return: `true' if and only if `keySexpStr' is in the correct format for keys in the Mojo system
    """
    try:
        ed = mencode.mdecode(keySexpStr)

        MojoMessage.checkTemplate(ed, K_TEMPL)
    except (MojoMessage.BadFormatError, MojoMessage.WrongMessageTypeError, KeyError, mojosixbit.Error, mencode.MencodeError), x:
        return false

    return true

K_TEMPL={'key header': {'cryptosystem': ANY, 'type': ANY, 'usage': ANY}, 'key values': {}}


def publicKeyIsWellFormed(keySexpStr):
    """
    @param keySexpStr: key in an s-expression string with accompanying meta-data

    @return: `true' if and only if `keySexpStr' is in the correct format for keys in the Mojo system
    """
    if not keyIsWellFormed(keySexpStr):
        return false

    try:
        ed = mencode.mdecode(keySexpStr)

        MojoMessage.checkTemplate(ed, PK_TEMPL)
    except (MojoMessage.BadFormatError, MojoMessage.WrongMessageTypeError, KeyError, mojosixbit.Error, mencode.MencodeError):
        return false

    return true

PK_TEMPL={'key header': {'cryptosystem': ANY, 'type': "public", 'usage': ANY}, 'key values': {}}


def publicRSAKeyIsWellFormed(keySexpStr):
    """
    @param keySexpStr: public RSA key in an s-expression string with accompanying meta-data

    @return: tuple of (`true' if and only if `keySexpStr' is in the correct format for public RSA keys in the Mojo system, the key data in sexp format)
    """
    if not publicKeyIsWellFormed(keySexpStr):
        return false

    try:
        ed = mencode.mdecode(keySexpStr)

        MojoMessage.checkTemplate(ed, PK_TEMPL)
    except (MojoMessage.BadFormatError, MojoMessage.WrongMessageTypeError, KeyError, mojosixbit.Error):
        return false

    return true

PRK_TEMPL={'key header': {'cryptosystem': "RSA", 'type': "public", 'usage': ANY}, 'key values': {'public modulus': MOD_VAL, 'public exponent': NON_NEGATIVE_INTEGER}}


def publicKeyForVerifyingTokenSignaturesIsWellFormed(keySexpStr):
    """
    @param keySexpStr: public key for verifying token signatures in an s-expression string with accompanying meta-data

    @return: `true' if and only if `keySexpStr' is in the correct format for public keys which are used for token signing in the Mojo system
    """
    if not publicKeyIsWellFormed(keySexpStr):
        return false

    try:
        ed = mencode.mdecode(keySexpStr)

        MojoMessage.checkTemplate(ed, PKFVTS_TEMPL)
    except (MojoMessage.BadFormatError, MojoMessage.WrongMessageTypeError, KeyError, mojosixbit.Error, mencode.MencodeError):
        return false

    return true

PKFVTS_TEMPL={'key header': {'cryptosystem': ANY, 'type': "public", 'usage': "only for verifying token signatures", 'value of signed token': {'currency': ANY, 'amount': NON_NEGATIVE_INTEGER}}, 'key values': {}}


def publicKeyForCommunicationSecurityIsWellFormed(keySexpStr):
    """
    @param keySexpStr: public key for verifying token signatures in an s-expression string with accompanying meta-data

    @return: `true' if and only if `keySexpStr' is in the correct format for public keys which are used for communication security
    """
    if not publicKeyIsWellFormed(keySexpStr):
        return false

    try:
        ed = mencode.mdecode(keySexpStr)

        MojoMessage.checkTemplate(ed, OurMessages.PKFC_TEMPL)
    except (MojoMessage.BadFormatError, MojoMessage.WrongMessageTypeError, KeyError, mojosixbit.Error, mencode.MencodeError), x:
        return false

    return true


def publicRSAKeyForVerifyingTokenSignaturesIsWellFormed(key):
    """
    @param key: public RSA key for verifying token signatures in an s-expression string with accompanying meta-data

    @return: `true' if and only if `key' is in the correct format for public keys which are used for token signing in the Mojo system
    """
    if (publicRSAKeyIsWellFormed(key)) and (publicKeyForVerifyingTokenSignaturesIsWellFormed(key)):
        return true
    else:
        return false


def publicRSAKeyForCommunicationSecurityIsWellFormed(key):
    """
    @param key: public RSA key for communications security in an
        s-expression string with accompanying meta-data
    @return: `true' if and only if `key' is in the correct format for public
        keys which are used for communications security
    """
    if (publicRSAKeyIsWellFormed(key)) and (publicKeyForCommunicationSecurityIsWellFormed(key)):
        return true
    else:
        return false


def getDenomination(keySexpStr):
    """
    Get the currency and value of tokens verified by this public key.

    @param key: public RSA key for verifying token signatures in an
        s-expression string with accompanying meta-data
    @return: a tuple of (currency, amount), where `currency' is a string and
        `amount' is a long

    @precondition: `keySexpStr' is well-formed.: publicKeyForVerifyingTokenSignaturesIsWellFormed(key): "keySexpStr: %s" % hr(keySexpStr)
    """
    assert publicKeyForVerifyingTokenSignaturesIsWellFormed(key), "`keySexpStr' is well-formed." + " -- " + "keySexpStr: %s" % hr(keySexpStr)

    ed = mencode.mdecode(keySexpStr)

    return (ed['key header']['value of signed token']['currency'], long(ed['key header']['value of signed token']['amount']))

