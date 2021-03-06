#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: UnreliableHandicapper.py,v 1.9 2003/02/09 17:52:13 zooko Exp $"

# pyutil modules
from pyutil.humanreadable import hr

# egtp modules
from egtp import idlib

# The most reliable broker is still handicapped this much.
TUNING_FACTOR=float(2**8)

# Extra boost for publication: we want to publish to more reliable servers!!
PUB_TUNING_FACTOR=float(8)

# The least reliable broker is handicapped as much as the furthest-away broker.
MIN_RELIABILITY=TUNING_FACTOR / idlib.Largest_Distance_NativeId_Int_Space

class UnreliableHandicapper:
    def __init__(self, counterparties, our_id):
        self.counterparties = counterparties
        self.our_id = our_id

    def __call__(self, counterparty_id, metainfo, message_type, message_body, TUNING_FACTOR=TUNING_FACTOR):
        """
        for all msgtypes
        """
        if idlib.equal(counterparty_id, self.our_id):
            return 0.0  # no handicap for us, we have high self esteem
        else:
            cpty = self.counterparties.get_counterparty_object(counterparty_id)
            reliability = cpty.get_custom_stat("reliability", 1.0)
            if reliability < MIN_RELIABILITY:
                reliability = MIN_RELIABILITY
                cpty.set_reliability(reliability)

        if message_type in ('pub block', 'put blob'): # "put block" is the way it will be spelled in the future, "put blob" is the way it was spelled in the past
            return (TUNING_FACTOR * PUB_TUNING_FACTOR) / reliability
        else:
            return TUNING_FACTOR / reliability
