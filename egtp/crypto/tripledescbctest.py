#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: tripledescbctest.py,v 1.4 2002/12/02 19:58:55 myers_carpenter Exp $"

from egtp.crypto import tripledescbc


x = tripledescbc.new("THIS IS A 24 BYTE KEYxyz")
iv = "IM 8B IV"
plaintext = "this is a plaintext message testing testing 1 2 3"
print "plaintext =",plaintext
ciphertext = x.encrypt(iv,plaintext)
print "ciphertext =",`ciphertext`
verify = x.decrypt(iv,ciphertext)
print "verification =",verify

print
plaintext = ""
print "plaintext (the null string) =",plaintext
ciphertext = x.encrypt(iv,plaintext)
print "ciphertext =",`ciphertext`
verify = x.decrypt(iv,ciphertext)
print "verification =",verify
