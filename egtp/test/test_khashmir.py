#!/usr/bin/env python
"""\
Unit test for khashmir lookup manager. 
"""

__author__   = 'Artimage <artimage@ishiboo.com>'
__revision__ = "$Id: test_khashmir.py,v 1.1 2003/02/09 19:52:48 artimage Exp $"

import time
import unittest
from random import randrange

#from twisted.internet.defer import Deferred                                   
#from twisted.internet import protocol                                     
#from twisted.python import threadable                                 
#from twisted.internet.app import Application                       
#from twisted.web import server  
#threadable.init() 

import threading

from pyutil.debugprint import debugprint

from dht import khashmir
from dht import hash
from dht import node
	
   
def test_build_net(quiet=0, peers=24, host='127.0.0.1',  pause=0, startport=2001, dbprefix='/tmp/test'):
    from whrandom import randrange
    import threading
    import thread
    import sys
    port = startport
    l = []
    if not quiet:
        print "Building %s peer table." % peers
    
    for i in xrange(peers):
        a = khashmir.Khashmir(host, port + i, db = dbprefix +`i`)
        l.append(a)
    
    
    thread.start_new_thread(l[0].app.run, ())
    time.sleep(1)
    for peer in l[1:]:
        peer.app.run()
    #time.sleep(3)
    
    def spewer(frame, s, ignored):
        from twisted.python import reflect
        if frame.f_locals.has_key('self'):
            se = frame.f_locals['self']
            print 'method %s of %s at %s' % (
                frame.f_code.co_name, reflect.qual(se.__class__), id(se)
                )
    #sys.settrace(spewer)

    print "adding contacts...."
    def makecb(flag):
        def cb(f=flag):
            f.set()
        return cb

    for peer in l:
        p = l[randrange(0, len(l))]
        if p != peer:
            n = p.node
            flag = threading.Event()
            peer.addContact(host, n.port, makecb(flag))
            flag.wait()
        p = l[randrange(0, len(l))]
        if p != peer:
            n = p.node
            flag = threading.Event()
            peer.addContact(host, n.port, makecb(flag))
            flag.wait()
        p = l[randrange(0, len(l))]
        if p != peer:
            n = p.node
            flag = threading.Event()
            peer.addContact(host, n.port, makecb(flag))
            flag.wait()
    
    print "finding close nodes...."
    
    for peer in l:
        flag = threading.Event()
        def cb(nodes, f=flag):
            f.set()
        peer.findCloseNodes(cb)
        flag.wait()
    #    for peer in l:
    #	peer.refreshTable()
    return l
    
def test_find_value(l, quiet=0):
    ff = threading.Event()	
    fa = threading.Event()
    fb = threading.Event()
    fc = threading.Event()
	
    n = len(l)
    a = l[randrange(0,n)]
    b = l[randrange(0,n)]
    c = l[randrange(0,n)]
    d = l[randrange(0,n)]
	
    key = hash.newID()
    value = hash.newID()
    if not quiet: print "inserting value..."
    def acb(p, f=ff):
        f.set()
    a.storeValueForKey(key, value, acb)
    ff.wait()

    if not quiet:
        print "finding..."
	
    class cb:
        def __init__(self, flag, value=value, port=None):
            self.flag = flag
            self.val = value
            self.found = 0
            self.port = port
	def callback(self, values):
	    try:
		# BUGBUG like the last test case, I believe these
		# should be asserts.
		if(len(values) == 0):
			if not self.found:
				print "find                NOT FOUND"
			else:
				print "find                FOUND"
                        assert self.found
		else:
			if self.val in values:
				self.found = 1
	    finally:
		self.flag.set()
	
    b.valueForKey(key, cb(fa, port=b.port).callback, searchlocal=0)
    fa.wait()
    c.valueForKey(key, cb(fb, port=c.port).callback, searchlocal=0)
    fb.wait()
    d.valueForKey(key, cb(fc, port=d.port).callback, searchlocal=0)    
    fc.wait()

def test_find_nodes(l, quiet=0):
    flag = threading.Event()
    
    n = len(l)

    a = l[randrange(0,n)]
    b = l[randrange(0,n)]
    
    def callback(nodes, flag=flag, id = b.node.id):
            # BUGBUG look at this test code.
            # This is the original khashmir code. It seems to me
            # that we should use asserts instead of the if. I have
            # given examples here, but since I can't test I will 
            # leave them commented out.     
            # assert len(nodes) > 0
            # assert nodes[0].id == id
            # Maybe that won't work since we are in a callback and 
            # we need to set the flag. But I think this should be fine.
            assert(len(nodes) >0) and (nodes[0].id == id)

            if (len(nodes) >0) and (nodes[0].id == id):
                    print "test_find_nodes  PASSED"
            else:
                    print "test_find_nodes  FAILED"
            flag.set()
    a.findNode(b.node.id, callback)
    flag.wait()



class KhashmirLookupManTestCase(unittest.TestCase):
    """
    This code blatently stolen from node.py in khashmir. If this turns out to be 
    a problem we can remove it. But I figured it would be nice to try this here. 
    Really we should probably call Khashmir's unit tests from ours... maybe not.
    """
    def set_up(self):
	pass

    def tear_down(self):
        pass

    def test_updated_last_seen(self):
        '''
        '''
        self.node = khashmir.Node().init(hash.newID(), 'localhost', 2002)
        t = self.node.lastSeen
        self.node.updateLastSeen()
        assert t < self.node.lastSeen


        

def suite():
    suite = unittest.makeSuite(KhashmirLookupManTestCase, 'test')
    return suite

if __name__ == "__main__":
    import sys
    n = 8
    if len(sys.argv) > 1: n = int(sys.argv[1])
    l = test_build_net(peers=n)
#    print "__main__: length of l ", len(l)
#    for node in l:
#        print "__main__: node ", node
#        print "__main__: buckets of a node ", node.table.buckets

    time.sleep(3)
    print "finding nodes..."
    for i in range(10):
		test_find_nodes(l)
    print "inserting and fetching values..."
    for i in range(10):
		test_find_value(l)

    

