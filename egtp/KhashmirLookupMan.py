#!/usr/bin/env python
#
# Copyright (c) 2002 Luke "Artimage" Nelson
# mailto:artimage@ishiboo.com
# See the end of this file for the free software, open source license (BSD-style).

# standard Python modules
import exceptions
import types

# EGTP modules
from egtp import CommStrat, humanreadable, interfaces

# (old) MN modules
from egtp import idlib

# Khashmir
import khashmir

class KhashmirLookupMan(interfaces.ILookupManager):
    """
    Khashmir is an implementation of Kademlia, which is a kind of distributed hash table.

    Here we are doing lookups via Khashmir.
    """
    def __init__(self, url, verifier=None):
        """
        @param url: This is the url to a known Khashmir node.
        @param verifier: the object that verifies that what the lookup
               returned is indeed valid.
        """
        if verifier is None:
            verifier = NodeMappingVerifier.NodeMappingVerifier() 
        interfaces.ILookupManager.__init__(self, verifier)

        # Create a khashmir node.
        self.lm = khashmir.Khashmir('127.0.0.1', '8888')    # BUGBUG the next version of khashmir will not require args.
        thread.start_new_thread(self.lm.app.run, ())        # start it running in its own thread.

        # Connect to a known node.
        mo =  re.search("http://(.*):(\d*)", url, re.IGNORECASE)
        if not mo:
            raise "No Match" # BUGBUG Should I raise somthing else?
        
        host = mo.group(1)
        ip   = mo.group(2)
        
        self.lm.addContact(host, port) # Khashmir is now connected. BUGBUG we should test this connection.
        self.lm.findCloseNodes()       # Find nodes close to us to bootstrap our finger table.

    def lookup(self, key, lookuphand):
        """
        @precondition: key must be well-formed according to the verifier.: self.verifier.verify_key(key): "key: %s" % hr(key)
        """
        assert self.verifier.verify_key(key), "precondition: key must be well-formed according to the verifier." + " -- " + "key: %s" % hr(key)

        val = None
        def search_callback():
            pass #BUGBUG I can't remember what the callback looks like. I wrote it down somewhere.
            
        self.lm.valueForKey(key, search_callback)
        lookuphand.result(val)

    def publish(self, key, object):
        """
        @precondition: key must be well-formed according to the verifier.: self.verifier.verify_key(key): "key: %s" % hr(key)
        @precondition: key-object pair must be valid mapping according to the verifier.: self.verifier.verify_mapping(key, object): "key: %s, object: %s" % (hr(key), hr(object),)
        """
        assert self.verifier.verify_key(key), "precondition: key must be well-formed according to the verifier." + " -- " + "key: %s" % hr(key)
        assert self.verifier.verify_mapping(key, object), "precondition: key-object pair must be valid mapping according to the verifier." + " -- " + "key: %s, object: %s" % (hr(key), hr(object),)
        
        self.lm.storeValueForKey(key, object)


# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software to deal in this software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of this software, and to permit
# persons to whom this software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of this software.
#
# THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THIS SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THIS SOFTWARE.
