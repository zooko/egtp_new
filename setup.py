#!/usr/bin/env python

import os, sys, string, re, urllib, md5, glob, pprint
#import egtp.version

try:
    from distutils.core import setup, Extension, Command
    import distutils.command.build_ext
except:
    raise SystemExit, """\
Could not load the distutils modules. Have you installed them?
(on Debian you need to 'apt-get install python-dev')
"""

class download(Command):
    description  = "download any files needed to build"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not os.path.isdir('build'):
            os.mkdir('build')

        self.base_dir = os.getcwd()
        if not os.path.isdir('build'):
            os.mkdir('build')
        self.download_bsddb3()
        self.download_pyutil()
        #self.download_libzutil()
        #self.download_libzstr()
        self.download_libbase32()
        self.download_cryptopp()

    def download_bsddb3(self):
        try:
            import bsddb3
        except ImportError:
            raise SystemExit, """\
The module bsddb3 (http://pybsddb.sourceforge.net/) must be installed.  
(on Debian unstable you can do 'apt-get install python-bsddb3'
 for RedHat see http://rpmfind.net/linux/RPM/sourceforge/pybsddb/bsddb3-3.3.0-1.i386.html)
"""

    def download_pyutil(self):
        try:
            import pyutil
            # TODO verison testing
        except ImportError:
            print "Downloading 'pyutil' ... "
            my_build_dir = os.path.join('build', 'pyutil')
            fetch_anon_cvs(':pserver:anonymous@cvs.pyutil.sourceforge.net:/cvsroot/pyutil', 'pyutil_new', my_build_dir)
            os.chdir(my_build_dir)
            distutils.core.run_setup('setup.py', ['install', '--install-lib', self.base_dir] )
            os.chdir(self.base_dir)

    def download_libzutil(self):
        if not os.path.isdir(os.path.join('build', 'libzutil')):
            print "Downloading 'libzutil' ... "
            my_build_dir = os.path.join('build', 'libzutil')
            fetch_anon_cvs(':pserver:anonymous@cvs.libzutil.sourceforge.net:/cvsroot/libzutil', 'libzutil', my_build_dir)
            os.chdir(my_build_dir)
            os.system('make')

    def download_libzstr(self):
        if not os.path.isdir(os.path.join('build', 'libzstr')):
            print "Downloading 'libzstr' ... "
            my_build_dir = os.path.join('build', 'libzstr')
            fetch_anon_cvs(':pserver:anonymous@cvs.libzstr.sourceforge.net:/cvsroot/libzstr', 'libzstr', my_build_dir)
            os.chdir(my_build_dir)
            os.system('make')

    def download_libbase32(self):
        try:
            import base32
            # TODO version testing
        except ImportError:
            print "Downloading 'libbase32' ... "
            my_build_dir = os.path.join('build', 'libbase32')
            fetch_anon_cvs(':pserver:anonymous@cvs.libbase32.sourceforge.net:/cvsroot/libbase32', 'libbase32', my_build_dir)
            os.chdir(my_build_dir)
            distutils.core.run_setup('setup.py', ['install', '--install-lib', self.base_dir] )
            os.chdir(self.base_dir)

    def download_cryptopp(self):
        def get_cryptopp():
            CRYPTOPP_URL = 'http://www.eskimo.com/~weidai/crypto50.zip'
            print "Downloading cryptopp from %s ... " % CRYPTOPP_URL
            out = file(os.path.join('build', 'crypto50.zip'), 'wb')
            out.write(urllib.urlopen(CRYPTOPP_URL).read())
            out.close()

        if not os.path.isfile(os.path.join(os.getcwd(), 'build', 'crypto50.zip')):
            get_cryptopp()

        m = md5.new()
        m.update(file(os.path.join('build', 'crypto50.zip'), 'rb').read())
        if m.hexdigest().lower() != 'fe8d4ef49b69874763f6dab30cbb6292':
            raise SystemExit, "File %r is incomplete or corrupt" % os.path.join('build', 'crypto42.zip')

        if not os.path.isfile(os.path.join('build', 'crypto50.zip')):
            raise SystemExit, "couldn't get zip file"

        if not os.path.isdir(os.path.join('build', 'crypto50')):
            print "Extracting crypto++..."
            cmd = 'unzip -d %s -a %s' % (os.path.join('build', 'crypto50'), os.path.join('build', 'crypto50.zip'))
            print cmd
            os.system(cmd)
            # same effect as 'touch'
            file(os.path.join('build', 'crypto50', 'unpatched'),'w').close()

        if os.path.isfile(os.path.join('build', 'crypto50', 'unpatched')):
            print "Patching crypto50..."
            os.chdir(os.path.join(self.base_dir, 'build', 'crypto50'))
            patchlist = os.listdir(os.path.join(self.base_dir, 'egtp', 'crypto', 'patches'))
            patchlist = filter(lambda x: x[0].islower(), patchlist)
            for ii in patchlist:
                os.system('patch -p0 < %s' % os.path.join(self.base_dir, 'egtp', 'crypto', 'patches', ii))
            os.chdir(self.base_dir)
            os.unlink(os.path.join('build', 'crypto50', 'unpatched'))

        if not os.path.isfile(os.path.join('build', 'crypto50', 'libcryptopp.a')):
            print "Building crypto++..."
            os.chdir(os.path.join(self.base_dir, 'build', 'crypto50'))
            os.system('make libcryptopp.a')
            os.chdir(self.base_dir)

class build_ext(distutils.command.build_ext.build_ext):
    user_options      = \
        distutils.command.build_ext.build_ext.user_options + \
        [('cryptopp-dir=', 'C',
          "Directory to look for cryptopp library" ),]

    def __init__(self, dist):
        self.dist = dist

        distutils.command.build_ext.build_ext.__init__(self, dist)

    def initialize_options(self):
        self.cryptopp_dir = None

        return distutils.command.build_ext.build_ext.initialize_options(self)

    def finalize_options(self):
        distutils.command.build_ext.build_ext.finalize_options(self)

        self.define = []
        self.library_dir = []
        self.extra_link_args = []

        if self.cryptopp_dir:
            pass
        elif os.environ.has_key('CRYPTOPP_DIR'):
            self.cryptopp_dir = os.environ['CRYPTOPP_DIR']
            if not os.path.isdir(self.cryptopp_dir) :
                raise SystemExit, "Your CRYPTOPP_DIR environment variable is incorrect.  is not dir: self.cryptopp_dir: %s" % self.cryptopp_dir
        elif os.path.isdir(os.path.join('build', 'crypto50')) and os.path.isfile(os.path.join('build', 'crypto50', 'libcryptopp.a')):
            self.cryptopp_dir = os.path.join('build', 'crypto50')
        else:
            raise SystemExit, """\
You don't have a copy of crypto++ version 5.0.  Try runing 'python setup.py download'...
"""

        if sys.platform == 'win32':
            # vc++ complained to me and told me to add /GX so I did
            self.define.extend((('PYTHON_MODULE', None), ('WIN32', None), ('GX', None),))
            # os.environ['CFLAGS'] = '/DPYTHON_MODULE /DWIN32 /GX'
            self.library_dirs.extend([self.cryptopp_dir])
            self.include_dirs.extend([self.cryptopp_dir])
            self.libraries.append('cryptopp')

        elif string.find(sys.platform, 'darwin') != -1:
            self.extra_link_args.extend(['-framework', 'Python'])
            #self.extra_link_args.append('-lstdc++')
            self.extra_link_args.append('-bundle')
            self.extra_link_args.extend(['-bundle_loader', sys.executable])
            self.library_dirs.append(self.cryptopp_dir)
            self.include_dirs.append(self.cryptopp_dir)
            self.libraries.insert(0, 'cryptopp')

        else:
            self.define.extend([('PYTHON_MODULE', None),])
            # self.extra_compile_args.extend(['-w',])
            # os.environ['CFLAGS'] = '-DPYTHON_MODULE -w'

            self.library_dirs.extend([self.cryptopp_dir])
            self.include_dirs.extend([self.cryptopp_dir])
            self.libraries.insert(0, 'cryptopp')

        self.define.extend([('CRYPTOPP_50', None),])

        # On FreeBSD we -finally- found that -lgcc was the magic needed linker flag to
        # prevent the "undefined symbol: __pure_virtual" problem when attempting to
        # import the cryptopp.so module.
        if re.search('bsd', sys.platform, re.I):
            libgcc_dir = os.path.dirname( os.popen("gcc -print-libgcc-file-name").readline()[:-1] )
            self.library_dirs.append(libgcc_dir)
            self.libraries.append('gcc')

    def build_extension(self, ext):
        fullname = self.get_ext_fullname(ext.name)

        # Skip win_entropy if platform is not windows.
        if (sys.platform != 'win32') and (fullname == 'egtp.crypto.win_entropy'):
                print "Skipping " + fullname + " since its only for win32."
                return

        # Deal with cryptopp and its need for C++
        if fullname == 'egtp.crypto.evilcryptopp':
            ext.extra_link_args.extend(self.extra_link_args)
            save_compiler = self.compiler
            self.compiler.compiler = ['g++']
            self.compiler.linker_exe = ['g++']
            self.compiler.compiler_so = ['g++']
            if string.find(sys.platform, 'darwin') != -1:
                self.compiler.linker_so = ['g++']
            else:
                self.compiler.linker_so = ['g++', '-shared']
            

        tmp = distutils.command.build_ext.build_ext.build_extension(self, ext)
        if fullname == 'egtp.crypto.evilcryptopp':
            self.compiler = save_compiler
        return tmp

class test(Command):
    """
    Based off of http://mail.python.org/pipermail/distutils-sig/2002-January/002714.html
    """
    description  = "test the distribution prior to install"

    user_options = [
        ('test-dir=', None,
         "directory that contains the test definitions"),]

    def initialize_options(self):
        self.test_dir = os.path.join('egtp', 'test')

    def finalize_options(self):
        build = self.get_finalized_command('build')
        self.build_purelib = build.build_purelib
        self.build_platlib = build.build_platlib

    def run(self):
        import unittest
        self.run_command('build')

        old_path = sys.path[:]
        sys.path.insert(0, os.path.abspath(self.build_purelib))
        sys.path.insert(0, os.path.abspath(self.build_platlib))

        runner = unittest.TextTestRunner()
        testFiles = glob.glob(os.path.join(self.test_dir, 'test_*.py'))
        testSuites = []
        for ff in testFiles:
            ff = ff.replace(os.sep, '.')
            MOD = __import__(ff[:-3], globals(), locals(), [''])
            if not hasattr(MOD, 'suite'):
                print "Skipping %r as it has no 'suite' function" % ff
            else:
                testSuites.append(MOD.suite())
            
        runner.run(unittest.TestSuite(tuple(testSuites)))

        sys.path = old_path[:]

def fetch_anon_cvs(cvsroot, module, directory_name):
    """
    Fetchs or updates a module from CVS.  Write the module into the current directory.
    """
    print "Downloading module '%s' from CVS ROOT '%s' into directory '%s' ..." % (module, cvsroot, directory_name)

    cwd = os.getcwd()

    write_cvs_pass = 1
    if os.path.isfile(os.path.expandvars('${HOME}/.cvspass')):
        ff = open(os.path.expandvars('${HOME}/.cvspass'), 'r')
        tmp = ff.read()
        ff.close()
        tmp = re.findall(re.escape(cvsroot), tmp)
        if tmp:
            write_cvs_pass = 0
    if write_cvs_pass:
        ff = open(os.path.expandvars('${HOME}/.cvspass'), 'a')
        ff.write("%s A\n" % cvsroot)
    if os.path.isdir(directory_name):
        print "Updating %r..." % module
        os.chdir(directory_name)
        os.system('cvs -z3 -d%s update -Pd' % cvsroot)
    else:
        print "Checking out %r..." % module
        subdir, final_dir = os.path.split(os.path.abspath(directory_name))
        os.chdir(subdir)
        cmd = 'cvs -z3 -d%s checkout -d%s -P %s' % (cvsroot, final_dir, module)
        os.system(cmd)
    os.chdir(cwd)

setup_args = {
    'name': "egtp",
#    'version': egtp.version.versionstr_full,
    'description': "EGTP is a system for sending messages between nodes in a peer to peer network.",
    'author': "Mnet Project",
    'author_email': "mnet-devel@lists.sourceforge.net",
    'licence': "GNU LGPL",
    'packages': [
        "egtp", 
        "egtp.crypto", 
        "egtp.mencode", 
        "egtp.test"
    ],
    'cmdclass': {
        'build_ext': build_ext,
        'test': test,
        'download': download,
    },
    'ext_modules': [
        Extension (
            'egtp.mencode._c_mencode_help',
            sources = [
                os.path.join('egtp', 'mencode', '_c_mencode_help.c'),
            ]
        ),
        Extension (
            'egtp.crypto.win_entropy',
            sources = [
                os.path.join('egtp', 'crypto', 'win_entropy.c'),
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
        ),
    ],
}

if hasattr(distutils.dist.DistributionMetadata, 'get_keywords'):
    setup_args['keywords'] = "internet tcp p2p crypto"

if hasattr(distutils.dist.DistributionMetadata, 'get_platforms'):
    setup_args['platforms'] = "win32 posix"

if __name__ == '__main__':
    apply(setup, (), setup_args)
    