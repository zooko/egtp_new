#!/usr/bin/env python

import os, sys, string, re, urllib, md5

try:
    from distutils.core import setup, Extension, Command
    import distutils.command.build_ext
except:
    raise SystemExit, """\
Could not load the distutils modules. Have you installed them?
(on Debian you need to 'apt-get install python2.2-dev')
"""

class build_ext(distutils.command.build_ext.build_ext):
    user_options      = \
        distutils.command.build_ext.build_ext.user_options + \
        [('cryptopp-dir=', 'C', 
          "Directory to look for cryptopp library" ),
         ('cryptopp-version=', 'v', 
          "What version of the cryptopp library we are linking to" )]

    def __init__(self, dist):
        self.dist = dist
        
        distutils.command.build_ext.build_ext.__init__(self, dist)

    def initialize_options(self):
        self.cryptopp_dir = None
        self.cryptopp_version = None
        
        return distutils.command.build_ext.build_ext.initialize_options(self)
    
    def finalize_options(self):
        distutils.command.build_ext.build_ext.finalize_options(self)
        
        self.define = []
        self.library_dir = []
        
        ### the following code is to make it use `g++' instead of `gcc' to compile and link.
        ### It is a very ugly way to do it, but I can't figure out a nice way to do it.   --Zooko 2001-09-16
        ### I got this code from http://mail.python.org/pipermail/python-list/2001-March/032381.html
        from distutils import sysconfig
        save_init_posix = sysconfig._init_posix
        def my_init_posix():
            # print 'my_init_posix: changing gcc to g++'
            save_init_posix()
            g = sysconfig._config_vars
            g['CC'] = 'g++'
            g['LDSHARED'] = 'g++ -shared'
        sysconfig._init_posix = my_init_posix

        if os.environ.has_key('CRYPTOPP_DIR'):
            cryptoppdir = os.environ['CRYPTOPP_DIR']
            if not os.path.isdir(cryptoppdir) :
                raise SystemExit, "Your CRYPTOPP_DIR environment variable is incorrect.  is not dir: cryptoppdir: %s" % cryptoppdir
        elif os.path.isdir('/usr/include/crypto++'):
            cryptoppdir = '/usr/include/crypto++'
        elif os.path.isdir('/usr/local/include/crypto++'):
            cryptoppdir = '/usr/local/include/crypto++'
        else:
            raise SystemExit, """\
Your CRYPTOPP_DIR environment variable must be set, 
or for Debian unstable do 'apt-get install libcrypto++-dev'
"""

        if sys.platform == 'win32':
            # vc++ complained to me and told me to add /GX so I did
            self.define.extend((('PYTHON_MODULE', None), ('WIN32', None), ('GX', None),))
            # os.environ['CFLAGS'] = '/DPYTHON_MODULE /DWIN32 /GX'
            self.libraries.append('cryptlib-mojo')
        else:
            self.define.extend([('PYTHON_MODULE', None),])
            # self.extra_compile_args.extend(['-w',])
            # os.environ['CFLAGS'] = '-DPYTHON_MODULE -w'

            self.library_dirs.extend([self.cryptopp_dir])
            self.include_dirs.extend([self.cryptopp_dir])
            self.libraries.insert(0, 'cryptopp')

        # find out the crypto++ version from the include files
        ff = file(os.path.join(cryptoppdir, 'local.h'), 'r')
        tmp = ff.read()
        ff.close()
        tmp = re.findall(r'\#define\s+VERSION\s+\"([^"]+)\"', tmp)
        try:
            cryptoppversion = tmp[0]
        except IndexError:
            raise SystemExit, "Couldn't find Crypto++ version from the 'local.h' include file"

        if self.cryptopp_version == "3.2":
            self.define.extend([('CRYPTOPP_32', None),])
        elif self.cryptopp_version == "4.0":
            self.define.extend([('CRYPTOPP_40', None),])
        elif self.cryptopp_version == "4.1":
            self.define.extend([('CRYPTOPP_41', None),])
        elif self.cryptopp_version == "4.2":
            self.define.extend([('CRYPTOPP_42', None),])
        
        # On FreeBSD we -finally- found that -lgcc was the magic needed linker flag to
        # prevent the "undefined symbol: __pure_virtual" problem when attempting to
        # import the cryptopp.so module.
        if re.search('bsd', sys.platform, re.I):
            libgcc_dir = os.path.dirname( os.popen("gcc -print-libgcc-file-name").readline()[:-1] )
            self.library_dirs.append(libgcc_dir)
            self.libraries.append('gcc')
        
class test(Command):
    """
    Based off of http://mail.python.org/pipermail/distutils-sig/2002-January/002714.html
    """
    description  = "test the distribution prior to install"
    
    user_options = [
        ('test-dir=', None,
         "directory that contains the test definitions"),]
                 
    def initialize_options(self):
        self.test_dir = 'tests'    
        
    def finalize_options(self):
        build = self.get_finalized_command('build')
        self.build_purelib = build.build_purelib
        self.build_platlib = build.build_platlib
                                                                                           
    def run(self):
        import unittest
        self.run_command('build')

        old_path = sys.path[:]
        sys.path.insert(0, self.build_purelib)
        sys.path.insert(0, self.build_platlib)
        sys.path.insert(0, os.path.join(os.getcwd(), self.test_dir))
        
        runner = unittest.TextTestRunner()
        for ff in os.listdir(self.test_dir):
            if ff[-3:] != ".py":
                continue
            print "Running tests found in '%s'..." % ff
            TEST = __import__(ff[:-3], globals(), locals(), [''])
            runner.run(TEST.suite())
        
        sys.path = old_path[:]
                
class download(Command):
    description  = "download any files needed to build"
    
    user_options = []

    def initialize_options(self):
        pass
                
    def finalize_options(self):
        pass
                                                                                                   
    def run(self):
        self.download_bsddb3()
        self.download_pyutil()
        self.download_cryptopp()

    def download_bsddb3(self):
        try:
            import bsddb3
        except ImportError:
            raise SystemExit, """\
The module bsddb3 (http://pybsddb.sourceforge.net/) must be installed.  
(on Debian unstable you can do 'apt-get install python2.2-bsddb3')
"""
    def download_pyutil(self):
        # pyutil
        fetch_anon_cvs(':pserver:anonymous@cvs.pyutil.sourceforge.net:/cvsroot/pyutil', 'pyutil')

    def download_cryptopp(self):        
        def get_cryptopp():
            CRYPTOPP_URL = 'http://www.eskimo.com/~weidai/crypto42.zip'
            print "Downloading cryptopp from %s ... " % CRYPTOPP_URL
            out = file('crypto42.zip', 'w')
            out.write(urllib.urlopen(CRYPTOPP_URL).read())
            out.close()
        
        if os.path.isdir('/usr/include/crypto++') or os.path.isdir('/usr/local/include/crypto++'):
            print "Crypto++ is installed system wide, no need to download"
            return
        
        if not os.path.isfile('crypto42.zip'):
            get_cryptopp()

        m = md5.new()
        m.update(file('crypto42.zip', 'r').read())
        if m.hexdigest().upper() != 'C1700E6E15F3189801E7EA47EEE83078':
            print "File 'crypto42.zip' is incomplete or corrupt"
            get_cryptopp()

        if os.path.isfile('crypto42.zip') and not os.path.isdir('cryptopp-4.2'):
            print "Building crypto++..."
            os.system('unzip -d crypto++-4.2 -a crypto42.zip')
            os.chdir('crypto++-4.2')
            os.system('cat ../src/evilcryptopp/patches/* |patch -p0')
            os.system('make')
            os.chdir('..')
        

def fetch_anon_cvs(cvsroot, module):
    """
    Fetchs or updates a module from CVS.  Write the module into the current directory.
    """
    write_cvs_pass = 1
    if os.path.isfile(os.path.expandvars('${HOME}/.cvspass')):
        ff = file(os.path.expandvars('${HOME}/.cvspass'), 'r')
        tmp = ff.read()
        ff.close()
        tmp = re.findall(re.escape(cvsroot), tmp)
        if tmp:
            write_cvs_pass = 0
    if write_cvs_pass:
        ff = file(os.path.expandvars('${HOME}/.cvspass'), 'a')
        ff.write("%s A" % cvsroot)
    if os.path.isdir(module):
        print "Updating %r..." % module
        os.chdir(module)
        os.system('cvs -z3 -d%s up -Pd' % cvsroot)
        os.chdir('..')
    else:
        print "Checking out %r..." % module
        os.system('cvs -z3 -d%s co -P %s' % (cvsroot, module))

setup (
    name            = 'egtp',
    version         = '0.0.2',
    description     = 'EGTP is a system for sending messages between nodes in a peer to peer network.',
    author          = 'Mnet Project',
    author_email    = 'mnet-devel@lists.sourceforge.net',
    licence         = 'LGPL',
    cmdclass        = {
        'build_ext':    build_ext,
        'test':         test,
        'download':     download,
    },
    ext_modules     = [
        Extension (
            'egtp.mencode._c_mencode_help', 
            sources = [
                os.path.join('egtp', 'mencode', '_c_mencode_help.c'),
            ] 
        ),
        Extension (
            'egtp.crypto.evilcryptopp',
            sources = [ 
                os.path.join('egtp', 'crypto', 'modval.cpp'), 
                os.path.join('egtp', 'crypto', 'wrappedrsa.cpp'), 
                os.path.join('egtp', 'crypto', 'randsource_methods.cpp'),
                os.path.join('egtp', 'crypto', 'evilcryptopp.cpp'),
                os.path.join('egtp', 'crypto', 'tripledescbc.cpp'),
                os.path.join('egtp', 'crypto', 'randsource.cpp'),
            ],
            # include_dirs = include_dirs,
            # define_macros = define_macros,
            # extra_compile_args = extra_compile_args,
            # extra_link_args = extra_link_args,
            # extra_objects = extra_objects,
            # library_dirs = library_dirs,  
            # libraries = libraries,
        ),
    ],
)
