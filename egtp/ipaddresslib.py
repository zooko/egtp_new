#
#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.
#
# A library for determining the IP addresses of the local machine.
#
__cvsid = '$Id: ipaddresslib.py,v 1.7 2002/11/03 22:24:56 zooko Exp $'

# standard modules
import sys
import os
import re
import string
import exceptions
import socket


if sys.platform == 'win32':
    # this is part of the win32all python package, get it from:
    # http://www.activestate.com/Products/ActivePython/win32all.html
    import win32pipe

# pyutil modules
from pyutil.debugprint import debugprint


class Error(StandardError): pass
class NonRoutableIPError(Error): pass

# Supported platforms:
# The format of this dict is a key identifying a general platform, and a
# tuple value representing specific platform strings which get mapped into
# general identifier.  If you need a more specific identification,
# use sys.platform.

platform_map = {
    "linux-i386": "linux", # redhat
    "linux-ppc": "linux",  # redhat
    "linux2": "linux",     # debian
    "win32": "win32",
    "irix6-n32": "irix",
    "irix6-n64": "irix",
    "irix6": "irix",
    "openbsd2": "bsd",
    "freebsd4": "bsd",
    "netbsd1": "bsd",
    "sunos5": "sunos",
    }

# Platform information:
platform = sys.platform
try:
    platform = platform_map[platform]
except KeyError:
    # To be cautious, if platform is not in platforms, warn the developer.
    # (By release time this should gracefully explain to the user that the
    # platform is not supported, but of course that will never happen.  -Nate
    debugprint.write("WARNING: %s is not a supported platform.\n" % platform)
    debugprint.write("Supported platforms include:\n" + str(platform_map))

# These work in Redhat 6.x and Debian 2.2 potato
__linux_ifconfig_path = '/sbin/ifconfig'
__linux_route_path = '/sbin/route'

# NetBSD 1.4 (submitted by Rhialto)
__netbsd_ifconfig_path = '/sbin/ifconfig -a'
__netbsd_netstat_path = '/usr/bin/netstat'

# Darwin/MacOSX
__darwin_ifconfig_path = '/sbin/ifconfig -a'
__darwin_netstat_path = '/usr/sbin/netstat'

# Solaris 2.x
__sunos_ifconfig_path = '/usr/sbin/ifconfig -a'
__sunos_netstat_path = '/usr/bin/netstat'

# Irix 6.5
__irix_ifconfig_path = '/usr/etc/ifconfig -a'
__irix_netstat_path = '/usr/etc/netstat'

# Wow, I'm really amazed at home much mileage we've gotten out of calling
# the external route.exe program on windows...  It appears to work on all
# versions so far.  Still, the real system calls would much be preferred...
__win32_route_path = 'route.exe'


#
# NOTE: these re's DO get used outside of this file
#
valid_ipaddr_re = re.compile(r"^\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?$")
localhost_re = re.compile(r"^(localhost$|localhost\.|127\.)")
# match RFC1597 addresses and all class D multicast addresses
bad_address_re = re.compile(r"^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|22[4-9]\.|23\d\.).*")

IP_ADDRESS_DETECTOR_HOST = '198.11.16.136'

def get_primary_ip_address(nonroutableok) :
    """
    @param nonroutableok: `true' if and only if it is okay to bind to a non-routable IP address
        like 127.0.0.1 or 192.168.1.2
    """
    address = find_address_via_socket()
    
    if not address:
        address = find_address_via_config()
    return address
            

def find_address_via_socket():
    """
    Playing around with the socket module I stumbled across this method!
    This will detect the IP address of your network interface that would
    be used to connect to the configured host.  A good idea would be to
    always use the root metatracker as the host.
    """
    address = None
    
    detectorhost = IP_ADDRESS_DETECTOR_HOST
    # this won't actually send any packets, it just creates a DGRAM socket so we can call getsockname() on it
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect( (detectorhost, 53) )
        address, ignoredport = s.getsockname()
    except socket.error, se:
        debugprint("Error trying to use %s to detect our IP address: %s (this is normal on win95/98/ME)\n", args=(detectorhost, se), v=2, vs='ipaddresslib')
        address = None
    del s

    return address    



def find_address_via_config():
    global platform
    
    if platform == 'linux':
        ifacedict = read_linux_ifconfig()
        default_iface = get_linux_default_iface()

        if not default_iface or not ifacedict.has_key(default_iface) :
            debugprint("ERROR ipaddresslib couldn't determine your IP address, assuming 127.0.0.1 for testing\n", vs='ipaddresslib')
            address = '127.0.0.1'
        else :
            address = ifacedict[default_iface]
    elif platform == 'win32' :
        addr = read_win32_default_ifaceaddr()
        if not addr :
            debugprint("ERROR ipaddresslib couldn't determine your IP address, assuming 127.0.0.1 for testing\n", vs='ipaddresslib')
            address = '127.0.0.1'
        else :
            address = addr
    elif platform == 'bsd':
        ifacedict = read_netbsd_ifconfig()
        default_iface = get_netbsd_default_iface()

        if not default_iface or not ifacedict.has_key(default_iface) :
            debugprint("ERROR ipaddresslib couldn't determine your IP address, assuming 127.0.0.1 for testing\n", vs='ipaddresslib')
            address = '127.0.0.1'
        else :
            address = ifacedict[default_iface]
    elif platform == 'darwin1':
        ifacedict = read_netbsd_ifconfig(ifconfig_path=__darwin_ifconfig_path)
        default_iface = get_netbsd_default_iface(netstat_path=__darwin_netstat_path)

        if not default_iface or not ifacedict.has_key(default_iface) :
            debugprint("ERROR ipaddresslib couldn't determine your IP address, assuming 127.0.0.1 for testing\n", vs='ipaddresslib')
            address = '127.0.0.1'
        else :
            address = ifacedict[default_iface]
    elif platform == 'irix' :
        ifacedict = read_irix_ifconfig()
        default_iface = get_irix_default_iface()

        if not default_iface or not ifacedict.has_key(default_iface) :
            debugprint("ERROR ipaddresslib couldn't determine your IP address, assuming 127.0.0.1 for testing\n", vs='ipaddresslib')
            address = '127.0.0.1'
        else :
            address = ifacedict[default_iface]
    elif platform == 'sunos':
        ifacedict = read_sunos_ifconfig()
        default_iface = get_sunos_default_iface()

        if not default_iface or not ifacedict.has_key(default_iface):
            debugprint("ERROR ipaddresslib couldn't determine your IP address, assuming 127.0.0.1 for testing\n", vs='ipaddresslib')
            address = '127.0.0.1'
        else:
            address = ifacedict[default_iface]
    else :
        debugprint('ERROR ipaddresslib unsupported os: '+sys.platform)
        if not forced_address :
            raise RuntimeError, "unsupported OS in ipaddresslib and IP_ADDRESS_OVERRIDE not configured"

    debugprint("I think your IP Address is " + address + "\n", v=3, vs='ipaddresslib')

    if (not nonroutableok) and (not is_routable(address)):
        raise NonRoutableIPError

    if not valid_ipaddr_re.match(str(address)) :
        raise RuntimeError, "ipaddresslib could not figure out a valid IP address for your host; invalid address: %s" % address

    return address

def is_routable(address):
    return (address) and not (localhost_re.match(address) or bad_address_re.match(address))


########################################################################

def read_linux_ifconfig():
    """Returns a dict mapping interface names to IP addresses"""
    # this is one function that may have been simpler in Perl...
    ifconfig_output = os.popen(__linux_ifconfig_path).read()
    ifconfig_output_ifaces = string.split(ifconfig_output, '\n\n')
    iface_re = re.compile('^(?P<name>\w+)\s.+\sinet addr:(?P<address>\d+\.\d+\.\d+\.\d+)\s.+$', flags=re.M|re.I|re.S)

    resultdict = {}
    for output in ifconfig_output_ifaces:
        m = iface_re.match(output)
        if m:
            d = m.groupdict()
            resultdict[d['name']] = d['address']
    
    return resultdict

def get_linux_default_iface():
    """Returns the interface name the default route uses on this machine"""
    route_output = os.popen(__linux_route_path + ' -n').read()
    def_route_re = re.compile('^0\.0\.0\.0\s.*\s(?P<name>\w+)$', flags=re.M|re.I)
    m = def_route_re.search(route_output)
    if m:
        return m.group('name')
    else:
        return None

########################################################################

def read_netbsd_ifconfig(ifconfig_path=__netbsd_ifconfig_path):
    """Returns a dict mapping interface names to IP addresses"""
    # this is one function that may have been simpler in Perl...
    ifconfig_output = os.popen(ifconfig_path).read()
    ifconfig_output_ifaces = string.split(ifconfig_output, '\n')
    name_re = re.compile('^(?P<name>\w+): flags=', flags=re.M|re.I|re.S)
    addr_re = re.compile('^\s+inet (?P<address>\d+\.\d+\.\d+\.\d+)\s.+$', flags=re.M|re.I|re.S)

    resultdict = {}
    for output in ifconfig_output_ifaces:
        m = name_re.match(output)
        if m:
            name = m.groupdict()['name']
        m = addr_re.match(output)
        if m:
            d = m.groupdict()
            resultdict[name] = d['address']
    
    return resultdict

def get_netbsd_default_iface(netstat_path=__netbsd_netstat_path):
    """Returns the interface name the default route uses on this machine"""
    route_output = os.popen(netstat_path + ' -rn').read()
    def_route_re = re.compile('^default\s.*\s(?P<name>\w+)$', flags=re.M|re.I)
    m = def_route_re.search(route_output)
    if m:
        return m.group('name')
    else:
        return None

########################################################################
def read_sunos_ifconfig(ifconfig_path=__sunos_ifconfig_path):
    """Returns a dict mapping interface names to IP addresses"""
    # this is one function that may have been simpler in Perl...
    ifconfig_output = os.popen(ifconfig_path).read()
    ifconfig_output_ifaces = string.split(ifconfig_output, '\n')
    name_re = re.compile('^(?P<name>[\w:]+): flags=', flags=re.M|re.I|re.S)
    addr_re = re.compile('^\s+inet (?P<address>\d+\.\d+\.\d+\.\d+)\s.+$', flags=re.M|re.I|re.S)

    resultdict = {}
    for output in ifconfig_output_ifaces:
        m = name_re.match(output)
        if m:
            name = m.groupdict()['name']
        m = addr_re.match(output)
        if m:
            d = m.groupdict()
            resultdict[name] = d['address']

    return resultdict

def get_sunos_default_iface(netstat_path=__sunos_netstat_path):
    """Returns the interface name the default route uses on this machine"""
    route_output = os.popen(netstat_path + ' -rna').read()
    routes_split = string.split(route_output, '\n')
    def_route_re = re.compile('^0.0.0.0\s.*\s(?P<name>\w+)$', flags=re.M|re.I)
    for output in routes_split:
        m = def_route_re.search(output)
        if m:
            return m.group('name')
        else:
            return None

########################################################################
# Irix thankfully uses the BSD ifconfig and netstat tools...

def read_irix_ifconfig(ifconfig_path=__irix_ifconfig_path):
    """Returns a dict mapping interface names to IP addresses"""
    ifconfig_output = os.popen(ifconfig_path).read()
    ifconfig_output_ifaces = string.split(ifconfig_output, '\n')
    name_re = re.compile('^(?P<name>\w+): flags=', flags=re.M|re.I|re.S)
    addr_re = re.compile('^\s+inet (?P<address>\d+\.\d+\.\d+\.\d+)\s.+$', flags=re.M|re.I|re.S)

    resultdict = {}
    for oidx in filter( lambda n: (n+2)%2, range(len(ifconfig_output_ifaces)) ):
        output, nextoutput = ifconfig_output_ifaces[oidx-1:oidx+1]
        m = name_re.match(output)
        if m:
            name = m.groupdict()['name']
            m = addr_re.match(nextoutput)
            if m:
                d = m.groupdict()
                resultdict[name] = d['address']
    
    return resultdict

def get_irix_default_iface():
    return get_netbsd_default_iface(netstat_path=__irix_netstat_path)

########################################################################

def read_win32_default_ifaceaddr(warninglogged_boolean=[]):
    # we could use the but it causes problems with some Norton tool
    # We'll use it.  The other thing doesn't work for Art.  --Zooko 2002-11-03
    return _route_read_win32_default_ifaceaddr()
    # return _hostname_read_win32_default_ifaceaddr()

def _hostname_read_win32_default_ifaceaddr():
    """return the IP address found by looking up our hostname"""
    try:
        myhostname = socket.gethostname()
        myipaddress = socket.gethostbyname(myhostname)
    except socket.error, e:
        debugprint('WARNING: could not obtain IP address for your machine.\n', v=1, vs="ipaddresslib.win32")
        return "127.0.0.1"  # unknown IP address, return localhost
    return myipaddress

def _route_read_win32_default_ifaceaddr():
    """return the IP address of the interface used by the first default route"""
    # the win32pipe interface hopefully doesn't bluescreen norton antivirus
    try:
        route_output = win32pipe.popen(__win32_route_path + ' print 0.0.0.0').read()
    except:
        debugprint('WARNING: win32pipe.popen() failed reverting to os.popen() to call ROUTE to obtain IP address\n', vs='ipaddresslib.win32')
        route_output = os.popen(__win32_route_path + ' print 0.0.0.0').read()
    def_route_re = re.compile('^\s*0\.0\.0\.0\s.+\s(?P<address>\d+\.\d+\.\d+\.\d+)\s+(?P<metric>\d+)\s*$', flags=re.M|re.I|re.S)

    m = def_route_re.search(route_output)
    if m:
        return m.group('address')
    else:
        return None


