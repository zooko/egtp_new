# Copyright (c) 2002 Bryce "Zooko" Wilcox-O'Hearn
# mailto:zooko@zooko.com
# See the end of this file for the free software, open source license (BSD-style).

__revision__ = "$Id: NodeMappingVerifier.py,v 1.5 2002/12/02 19:58:49 myers_carpenter Exp $"

# standard Python modules
import exceptions, types

# pyutil modules
from pyutil.debugprint import debugprint

# EGTP modules
from egtp import CommStrat, interfaces, idlib
from egtp.humanreadable import hr

class NodeMappingVerifier(interfaces.IVerifier):
    """
    Determines where a nodeId -> EGTP address mapping is legitimate.
    """
    def __init__(self):
        interfaces.IVerifier.__init__(self)

    def verify_mapping(self, key, object):
        """
        @return: true if and only if `object' is a valid result for `key'

        @precondition: key must be well-formed.: self.verify_key(key)
        """
        assert self.verify_key(key), "precondition: key must be well-formed."

        # debugprint("to: %s\n", args=(type(object),))
        # debugprint("hk: %s\n", args=(object.has_key("connection strategies"),))
        # debugprint("gethk: %s\n", args=(object.get("connection strategies", [{}])[0].has_key("pubkey"),))
        # debugprint("eq: %s\n", args=(idlib.equal(key, CommStrat.addr_to_id(object)),))
        return (((type(object) is types.DictType) and (object.has_key("connection strategies")) and (object.get("connection strategies", [{}])[0].has_key("pubkey"))) or ((type(object) is types.InstanceType) and (isinstance(object, CommStrat)) and (object._broker_id is not None))) and idlib.equal(key, CommStrat.addr_to_id(object))

    def verify_key(self, key):
        """
        @return: true if and only if `key' is well-formed
        """
        return idlib.is_id(key)
