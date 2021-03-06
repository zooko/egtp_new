#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: __init__.py,v 1.4 2002/12/02 19:58:51 myers_carpenter Exp $"

""" 
Evil Geninus Transport Protocol

EGTP is a system for sending messages between nodes in a peer to peer
network.  This Tutorial will show you how to instantiate an EGTP node, send
messages to other nodes, and process messages sent to your node.  Currently
this functionality is available only via a Python API, but other languages
(including XML-RPC and C) will be supported as soon as someone wants it
enough.

This Tutorial will contain snippets of Python code.  You can see complete,
running code by looking in the EGTPunittest.py file, at the function named
`_help_test_EGTP_send_and_receive()'.  It might be helpful to compare the
code snippets in the Tutorial with the running code in that unit test while
reading the Tutorial.


 1.  Initializing EGTP

 First import the Python module:

 >>> import Node

 Now before using Node for anything, you have to call `Node.init()'.

 >>> Node.init()


 2.  Creating an EGTP Node

 >>> mynode = Node.Node(lookupman, discoveryman)

 Hey waitasecond -- what are these "lookupman" and "discoveryman" things? 
 Well,

 Each EGTP node has a unique ID which is cryptographically determined by the
 node's public key.  

"""
