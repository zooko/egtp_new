#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: BandwidthThrottler.py,v 1.5 2003/02/02 19:31:35 myers_carpenter Exp $"

# pyutil modules
from pyutil.config import DEBUG_MODE
from pyutil import timeutil, debugprint

true = 1
false = None

class BandwidthThrottler:
    """
    Very simple class to keep track of how much bandwidth you're using, and briefly turn off comms
    if it exceeds the recommended maximum.

    Currently we have one instance for incoming and one for outgoing traffic.
    """
    def __init__(self, Kbps, throttle=false, granularity=10, time=timeutil.timer.time):
        """
        @param Kbps: max throughput in kilobits/second
        @param throttle: `true' if and only if comms should be throttled when more than `Kbps'
            bandwidth has been used (averaged over the last `granularity' seconds)
        @param granularity: how many seconds long are the periods
        """
        self._maxbytes = long(((Kbps / 8.0) * 1024.0) * granularity)
        self._throttle = throttle
        self._granularity = granularity 
        self._used = 0
        self._lasttick = time()
        self._throttlecbs = []
        self._unthrottlecbs = []
        self._tick_doq_loop()

    def _tick_doq_loop(self):
        DoQ.doq._asyncorelooper.add_task(self.used, args=(0,))
        DoQ.doq.add_task(self._tick_doq_loop, delay=60)

    def register(self, throttle_callback, unthrottle_callback):
        self._throttlecbs.append(throttle_callback)
        self._unthrottlecbs.append(unthrottle_callback)

    def unregister(self, throttle_callback, unthrottle_callback):
        self._throttlecbs.remove(throttle_callback)
        self._unthrottlecbs.remove(unthrottle_callback)

    def used(self, bytes, time=timeutil.timer.time):
        """
        @param bytes: the number of bytes (not bits!) you just used
        """
        now = time()
        if now > (self._lasttick + self._granularity):
            if DEBUG_MODE:
                debugprint.debugprint("BandwidthThrottler measuring: %s bytes in %s seconds (%s Kbps)\n", args=(self._used, "%0.0f" % (now - self._lasttick), "%0.3f" % (((self._used * 8.0) / 1024.0) / self._granularity)), v=7, vs="TCPCommsHandler") ### for faster operation, comment this line out.  --Zooko 2000-12-11

            self._lasttick = now
            self._used = bytes
            for unthrottlecb in self._unthrottlecbs:
                unthrottlecb()
            return

        self._used = self._used + bytes

        if (self._throttle) and (self._used >= self._maxbytes):
            debugprint.debugprint("BandwidthThrottler maxed out: %s bytes in %s seconds (%s Kbps); throttling\n", args=(self._used, "%0.0f" % (now - self._lasttick), "%0.3f" % (((self._used * 8.0) / 1024.0) / self._granularity)), v=7, vs="TCPCommsHandler") ### for faster operation, comment this line out.  --Zooko 2000-12-11
            for throttlecb in self._throttlecbs:
                throttlecb()
