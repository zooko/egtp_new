# Copyright (c) 2003 Bryce "Zooko" Wilcox-O'Hearn
# mailto:zooko@zooko.com
# See the end of this file for the free software, open source license (BSD-style).

# Note: this was designed and implemented with one eye on Drue Lowenstern's
# "Khashmir" implementation and one eye on the original Kademlia paper.  (This
# explains all the typos -- no eyes left to review what we were writing.)

"""
Use a Kademlia routing system to communicate to other EGTP nodes.
"""

__version__ = "$Revision: 1.2 $"
# $Source: /home/zooko/playground/egtp_new/rescue-party/gw/../egtp_new/egtp_new/egtp/kademlia.py,v $

True = 1 == 1
False = 0 == 1

# pyutil modules
from pyutil.assertutil import _assert, precondition, postcondition
from pyutil.debugprint import debugprint, debugstream
from pyutil.humanreadable import hr

# egtp modules
import CommStrat
import idlib

class KademNode:
    pass
    # Art: fill this in.  ;-)
   

# Copyright (c) 2003 Bryce "Zooko" Wilcox-O'Hearn
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software to deal in this software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of this software, and to permit
# persons to whom this software is furnished to do so, subject to the following
# condition:
#
# THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THIS SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THIS SOFTWARE.
