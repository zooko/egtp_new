#!/usr/bin/env python

__author__   = 'EGFABT'
__revision__ = "$Id: test_keyutils.py,v 1.1 2002/11/28 00:49:56 myers_carpenter Exp $"

import unittest

from egtp.crypto import randsource, modval

from egtp import keyutil

class KeyUtilTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_publicKeyIsWellFormed(self):
        assert keyutil.publicKeyIsWellFormed(_sample_RSA_public_key_for_verifying_token_signatures_string)

    def test_publicKeyIsWellFormed_mustRejectRandomJunk(self):
        assert not keyutil.publicKeyIsWellFormed("fooey")
        
    def test_publicKeyIsWellFormed_mustRejectPrivateKey(self):
        assert not keyutil.publicKeyIsWellFormed(_sample_RSA_private_key_for_signing_tokens_message)

    def test_publicRSAKeyIsWellFormed(self):
        assert keyutil.publicRSAKeyIsWellFormed(_sample_RSA_public_key_for_verifying_token_signatures_string)
        
    def test_publicRSAKeyIsWellFormed_mustRejectRSAPrivateKey(self):
        assert not keyutil.publicRSAKeyIsWellFormed(_sample_RSA_private_key_for_signing_tokens_message)
        
    def test_publicRSAKeyIsWellFormed_mustRejectRandomJunk(self):
        assert not keyutil.publicRSAKeyIsWellFormed("whatever")

    def test_publicRSAKeyIsWellFormed_mustReject3DESSecretKey(self):
        assert not keyutil.publicRSAKeyIsWellFormed(_sample_3DES_secret_key_message)

    def test_publicKeyForVerifyingTokenSignaturesIsWellFormed(self):
        assert keyutil.publicKeyForVerifyingTokenSignaturesIsWellFormed(_sample_RSA_public_key_for_verifying_token_signatures_string)

    def test_publicKeyForVerifyingTokenSignaturesIsWellFormed_mustRejectPrivateKey(self):
        assert not keyutil.publicKeyForVerifyingTokenSignaturesIsWellFormed(_sample_RSA_private_key_for_signing_tokens_message)

    def test_publicKeyForVerifyingTokenSignaturesIsWellFormed_mustRejectBadUsage(self):
        print 'XXX write test_publicKeyForVerifyingTokenSignaturesIsWellFormed_mustRejectBadUsage'

    def test_publicKeyForVerifyingTokenSignaturesIsWellFormed_mustRejectIllFormed(self):
        print 'XXX unwritten test!'

    def test_publicKeyForVerifyingTokenSignaturesIsWellFormed_mustRejectIllFormed_2(self):
        print 'XXX unwritten test!'

    def test_publicKeyForVerifyingTokenSignaturesIsWellFormed_mustRejectIllFormed_3(self):
        print 'XXX unwritten test!'

    def test_publicRSAKeyForVerifyingTokenSignaturesIsWellFormed(self):
        assert keyutil.publicRSAKeyForVerifyingTokenSignaturesIsWellFormed(_sample_RSA_public_key_for_verifying_token_signatures_string)

    def test_publicRSAKeyForVerifyingTokenSignaturesIsWellFormed_mustRejectPrivateKey(self):
        assert not keyutil.publicRSAKeyForVerifyingTokenSignaturesIsWellFormed(_sample_RSA_private_key_for_signing_tokens_message)

    def test_keyIsWellFormed(self):
        assert keyutil.keyIsWellFormed(_sample_RSA_public_key_for_verifying_token_signatures_string)

    def disabled_test_keyIsWellFormed_2(self):
        assert keyutil.keyIsWellFormed(_sample_RSA_private_key_for_signing_tokens_message)

    def disabled_test_keyIsWellFormed_3(self):
        assert keyutil.keyIsWellFormed(_sample_3DES_secret_key_message)

    def test_keyIsWellFormed_mustRejectIllFormed(self):
        assert not keyutil.keyIsWellFormed("")

    def test_keyIsWellFormed_mustRejectIllFormed_2(self):
        print 'XXX unwritten test!'

    def test_keyIsWellFormed_mustRejectIllFormed_3(self):
        print 'XXX unwritten test!'

    def test_keyIsWellFormed_mustRejectIllFormed_4(self):
        print 'XXX unwritten test!'

    def test_keyIsWellFormed_mustRejectIllFormed_5(self):
        print 'XXX unwritten test!'

    def test_keyIsWellFormed_mustRejectIllFormed_5(self):
        print 'XXX unwritten test!'
     
    def test_makePublicRSAKeyForVerifyingTokenSignatures(self):
        kMV = modval.new(sampleModulus, sampleExponent)

        kSEXP = keyutil.makePublicRSAKeyForVerifyingTokenSignatures(kMV)

        assert keyutil.publicRSAKeyForVerifyingTokenSignaturesIsWellFormed(kSEXP)

    def test_makeRSAPublicKeyMVFromSexpString(self):
        kMV = keyutil.makeRSAPublicKeyMVFromSexpString(_sample_RSA_public_key_for_verifying_token_signatures_string)

        assert kMV.get_exponent() == sampleExponent 
        assert kMV.get_modulus() == sampleModulus 

    def test_publicRSAKeyIsSane(self):
        kMV = modval.new_random(10, 3)

        sxpStr = keyutil.makePublicRSAKeyForVerifyingTokenSignatures(kMV)

        assert keyutil.publicRSAKeyIsSane(sxpStr)

sampleModulus = '\xa4\xea\x83Lt\xb2\xe9B-?'
sampleExponent = 3

# sample RSA public key message (note: this is _NOT_ in canonical form -- I added extraneous carriage returns and indentation to aid readability.  Delete all carriage returns and whitespace indentation to get canonical form, as shown below):
#(
#     (10:key header
#         (
#             (12:cryptosystem3:RSA)
#             (4:type6:public)
#             (5:usage35:only for verifying token signatures)
#             (21:value of signed token
#                 (
#                     (6:amount2:16)
#                     (8:currency16:Mojo Test Points)))))
#     (10:key values
#         (
#             (15:public exponent1:3)
#             (14:public modulus14:pOqDTHSy6UItPw))))

# sample RSA public key message in canonical form

_sample_RSA_public_key_for_verifying_token_signatures_string='(4:dict(6:string10:key header)(4:dict(6:string12:cryptosystem)(6:string3:RSA)(6:string4:type)(6:string6:public)(6:string5:usage)(6:string35:only for verifying token signatures)(6:string21:value of signed token)(4:dict(6:string6:amount)(6:string2:16)(6:string8:currency)(6:string16:Mojo Test Points)))(6:string10:key values)(4:dict(6:string15:public exponent)(6:string1:3)(6:string14:public modulus)(6:string14:pOqDTHSy6UItPw)))'

# {
#     'key header': {
#         'type': 'public',
#         'cryptosystem': 'RSA',
#         'usage': 'only for verifying token signatures',
#         'value of signed token': {
#         'currency': 'Mojo Test Points',
#         'amount': '16',
#     },
#     'key values': {
#         'public modulus': 'pOqDTHSy6UItPw',
#         'public exponent': '3',
#     },
# },

_sample_RSA_public_key_for_verifying_token_signatures_edict = { 'header': { 'protocol': 'Mojo v0.94', 'message type': 'key' }, 'key': { 'key header': { 'type': 'public', 'cryptosystem': 'RSA', 'usage': 'only for verifying token signatures', 'value of signed token': { 'currency': 'Mojo Test Points', 'amount': '16' } }, 'key values': { 'public modulus':'pOqDTHSy6UItPw', 'public exponent': '3' } } }


# sample private RSA key message (note: this is _NOT_ in canonical form -- I added extraneous carriage returns and indentation to aid readability.  Delete all carriage returns and whitespace indentation to get canonical form, as shown below):
#    (
#        (6:header
#            (
#                (8:protocol10:Mojo v0.94)
#                (12:message type3:key)))
#        (3:key
#            (
#                (10:key header
#                    (
#                        (4:type7:private)
#                        (12:cryptosystem3:RSA)
#                        (5:usage23:only for signing tokens)
#                        (21:value of signed token
#                            (
#                                (8:currency16:Mojo Test Points)
#                                (6:amount2:16)))))
#                (10:key values
#                    (
#                        (16:private exponent128:PRIVATE_EXPONENT_BITS...........................................................................................................)
#                        (15:private factors
#                            (
#                                (1:p64:PRIVATE_FACTOR_P_BITS...........................................)
#                                (1:q64:PRIVATE_FACTOR_Q_BITS...........................................))))))))

# sample private RSA key message in canonical form:
_sample_RSA_private_key_for_signing_tokens_message='(4:dict(6:string6:header)(4:dict(6:string12:message type)(6:string3:key)(6:string8:protocol)(6:string10:Mojo v0.94))(6:string3:key)(4:dict(6:string10:key header)(4:dict(6:string12:cryptosystem)(6:string3:RSA)(6:string4:type)(6:string7:private)(6:string5:usage)(6:string23:only for signing tokens)(6:string21:value of signed token)(4:dict(6:string6:amount)(6:string2:16)(6:string8:currency)(6:string16:Mojo Test Points)))(6:string10:key values)(4:dict(6:string16:private exponent)(6:string128:PRIVATE_EXPONENT_BITS...........................................................................................................)(6:string15:private factors)(4:dict(6:string1:p)(6:string64:PRIVATE_FACTOR_P_BITS...........................................)(6:string1:q)(6:string64:PRIVATE_FACTOR_Q_BITS...........................................)))))'

# sample withdrawal message (note: this is _NOT_ in canonical form -- I added extraneous carriage returns and indentation to aid readability.  Delete all carriage returns and whitespace indentation to get canonical form, as shown below):
#    (
#        (6:header
#            (
#                (8:protocol10:Mojo v0.94)
#                (12:message type16:token withdrawal)))
#        (21:token ids for signing
#            (
#                (23:token id for signing #120:TOKEN_ID_4_S_BITS_1.)
#                (23:token id for signing #220:TOKEN_ID_4_S_BITS_2.)
#                (23:token id for signing #320:TOKEN_ID_4_S_BITS_3.))))

# sample withdrawal message in canonical form:
_sample_withdrawal_message='(4:dict(6:string6:header)(4:dict(6:string12:message type)(6:string16:token withdrawal)(6:string8:protocol)(6:string10:Mojo v0.94))(6:string21:token ids for signing)(4:dict(6:string23:token id for signing #1)(6:string20:TOKEN_ID_4_S_BITS_1.)(6:string23:token id for signing #2)(6:string20:TOKEN_ID_4_S_BITS_2.)(6:string23:token id for signing #3)(6:string20:TOKEN_ID_4_S_BITS_3.)))'

_sample_withdrawal_reply_message_edict={'header': {'protocol': 'Mojo v0.94', 'message type': 'token withdrawal reply'}, 'signed token ids for signing': {'signed token id for signing #1': 'S_T_ID_4_S_BITS_1_..', 'signed token id for signing #2': 'S_T_ID_4_S_BITS_2_..', 'signed token id for signing #3': 'S_T_ID_4_S_BITS_3_..'}}


# sample 3DES secret key message (note: this is _NOT_ in canonical form -- I added extraneous carriage returns and indentation to aid readability.  Delete all carriage returns and whitespace indentation to get canonical form, as shown below):
#    (
#        (6:header
#            (
#                (8:protocol10:Mojo v0.94)
#                (12:message type3:key)))
#        (3:key
#            (
#                (10:key header
#                    (
#                        (4:type13:shared secret)
#                        (12:cryptosystem43:Triple DES, Encrypt-Decrypt-Encrypt, 3 Keys)
#                        (5:usage28:only for encrypting sessions)))
#                (10:key values
#                    (
#                        (17:shared secret key192:SHARED_SECRET_KEY_BITS..........................................................................................................................................................................))))))

# sample 3DES secret key message in canonical form
_sample_3DES_secret_key_message='(4:dict(6:string6:header)(4:dict(6:string12:message type)(6:string3:key)(6:string8:protocol)(6:string10:Mojo v0.94))(6:string3:key)(4:dict(6:string10:key header)(4:dict(6:string12:cryptosystem)(6:string43:Triple DES, Encrypt-Decrypt-Encrypt, 3 Keys)(6:string4:type)(6:string13:shared secret)(6:string5:usage)(6:string28:only for encrypting sessions))(6:string10:key values)(4:dict(6:string17:shared secret key)(6:string192:SHARED_SECRET_KEY_BITS..........................................................................................................................................................................))))'

def suite():
    suite = unittest.makeSuite(KeyUtilTestCase, 'test')

    # suite2 = module2.TheTestSuite()
    # return unittest.TestSuite((suite1, suite2))

    return suite

if __name__ == "__main__":
    unittest.main()
