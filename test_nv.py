import nv
import os
import pdb
import pexpect
import shutil
import sys
import unittest

# -----------------------------------------------------------------------------
# class StdoutExcursion(object):
#     """
#     This class allows us to run something that writes to stdout and capture the
#     output in a StringIO.
# 
#         with StdoutExcursion() as sio:
#             do something that writes to stdout
#             result = sio()
#         self.assertEqual(result, ...)
# 
#     This is useful in a different way than
#         result = pexpect.run(something that writes stdout)
#     since pexpect.run() expects a command line but in a StdoutExcursion, we can
#     call a python function.
#     """
#     def __init__(self):
#         self.stdout = sys.stdout
# 
#     def __enter__(self):
#         sys.stdout = StringIO.StringIO()
#         return sys.stdout.getvalue
# 
#     def __exit__(self, type, value, traceback):
#         sys.stdout.close()
#         sys.stdout = self.stdout


# -----------------------------------------------------------------------------
def funcname():
    return sys._getframe(1).f_code.co_name

# -----------------------------------------------------------------------------
class TestNV(unittest.TestCase):
    testdir = "/tmp/nv_test"
    nvpath = os.path.abspath("./nv.py")
    
    # -------------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        if os.path.exists(cls.testdir):
            shutil.rmtree(cls.testdir)
        os.mkdir(cls.testdir)

    # -------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        keep = os.getenv("KEEPFILES")
        if os.path.exists(cls.testdir) and not keep:
            shutil.rmtree(cls.testdir)

    # -------------------------------------------------------------------------
    def test_setup_link_noarg(self):
        """
        ./nv.py setup
        --> err: 'must specify link location'
        """
        actual = pexpect.run("./nv.py setup")
        exp = "Link directory or file is required"
        self.assertTrue(exp in actual,
                        "Expected '%s' in '%s'" % (exp, actual))

    # -------------------------------------------------------------------------
    def test_setup_link_noarg_f(self):
        """
        ./nv.py setup -f
        --> err: 'must specify link location'
        """
        actual = pexpect.run("./nv.py setup -f")
        exp = "Link directory or file is required"
        self.assertTrue(exp in actual,
                         "Expected '%s' in '%s'" % (exp, actual))

    # -------------------------------------------------------------------------
    def test_setup_link_nx(self):
        """
        non-existent file
        ./nv.py setup nx
        --> ln -s this nx
        """
        testfile = os.path.join(self.testdir, "nosuch")
        if os.path.exists(testfile):
            os.unlink(testfile)
        nvpath = os.path.abspath("./nv.py")
        nv.setup_link(testfile, nvpath, False)
        self.assertTrue(os.path.islink(testfile),
                        "%s should be a link" % testfile)
        self.assertEqual(nvpath, os.readlink(testfile),
                         "'%s' != '%s'" %
                         (nvpath, os.readlink(testfile)))
        os.unlink(testfile)

    # -------------------------------------------------------------------------
    def test_setup_link_nx_f(self):
        """
        ./nv.py setup -f nx
        --> ln -s this nx
        """
        testfile = os.path.join(self.testdir, "nosuch")
        if os.path.exists(testfile):
            os.unlink(testfile)
        nvpath = os.path.abspath("./nv.py")
        nv.setup_link(testfile, nvpath, True)
        self.assertTrue(os.path.islink(testfile),
                        "%s should be a link" % testfile)
        self.assertEqual(nvpath, os.readlink(testfile),
                         "'%s' != '%s'" %
                         (nvpath, os.readlink(testfile)))
        os.unlink(testfile)

    # -------------------------------------------------------------------------
    def test_setup_link_xdir(self):
        """
        existing directory
        ./nv.py setup xdir
        --> ln -s this xdir/nv
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xdir_f(self):
        """
        existing directory with --force
        ./nv.py setup -f xdir
        --> ln -s this xdir/nv
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xfile(self):
        """
        existing file
        ./nv.py setup xfile
        --> err: 'rename xfile or use another link name'
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xfile_f(self):
        """
        existing file with --force
        ./nv.py setup -f xfile
        --> mv xfile xfile.original; ln -s this xfile
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xlink_nxdir(self):
        """
        existing link to an non-existent directory
        ./nv.py setup xlinkdir
        --> ln -s this xlinkdir/nv
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xlink_nxdir_f(self):
        """
        existing link to an non-existent directory with -f
        ./nv.py setup xlinkdir
        --> ln -s this xlinkdir/nv
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xlinkdir_nonv(self):
        """
        existing link to an existing directory with no nv file
        ./nv.py setup xlinkdir
        --> ln -s this xlinkdir/nv
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xlinkdir_nonv_f(self):
        """
        existing link to an existing directory with no nv file with -f
        ./nv.py setup xlinkdir
        --> ln -s this xlinkdir/nv
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xlink_nxfile(self):
        """
        existing link pointing at non existent file
        ./nv.py setup xlinkfile -> nx file
        --> err: 'xlinkfile exists; rename or use --force'
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xlink_nxfile_f(self):
        """
        existing link pointing at non existent file with --force
        ./nv.py setup -f xlinkfile
        --> unlink xlinkfile; ln -s this xlinkfile
        """
        stem = funcname()
        testfile = os.path.join(self.testdir, stem + "_file")
        testlink = os.path.join(self.testdir, stem + "_link")
        if os.path.exists(testfile):
            os.unlink(testfile)
        os.symlink(testfile, testlink)
        
        result = nv.setup_link(testlink, self.nvpath, True)

        exp = ('%s -> %s; remove %s or use --force' %
               (testlink, testfile, testlink))
        self.assertTrue(os.path.islink(testlink),
                        "Expected '%s' to be a link" % testlink)
        self.assertEqual(self.nvpath, os.readlink(testlink),
                         "Expected '%s' -> '%s', got '%s' -> '%s'" %
                         (testlink, self.nvpath,
                          testlink, os.readlink(testlink)))

    # -------------------------------------------------------------------------
    def test_setup_link_xlinkdir_nonv(self):
        """
        existing link to an existing directory with no nv file
        ./nv.py setup xlinkdir
        --> ln -s this xlinkdir/nv
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xlinkdir_nonv_f(self):
        """
        existing link to an existing directory with no nv file with -f
        ./nv.py setup xlinkdir
        --> ln -s this xlinkdir/nv
        """
        self.fail('construction')

    # -------------------------------------------------------------------------
    def test_setup_link_xlinkdir_nv(self):
        """
        existing link to an existing directory with an nv file
        ./nv.py setup xlinkdir
        --> ln -s this xlinkdir/nv
        """
        stem = funcname()
        testlink = os.path.join(self.testdir, stem + "_l")
        fdir = os.path.join(self.testdir, stem + "_d")
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        lnv = os.path.join(fdir, "nv")
        open(lnv, 'w').close()
        os.symlink(fdir, testlink)

        result = nv.setup_link(testlink, self.nvpath, False)

        exp = ("%s is a file or directory; rename it or use --force" %
               os.path.join(testlink, "nv"))
        self.assertTrue(exp in result,
                        "Expected '%s' in '%s'" % (exp, result))
        lnvorig = lnv + ".original"
        self.assertFalse(os.path.exists(lnvorig),
                         "%s should not exist" % lnvorig)
        self.assertFalse(os.path.islink(lnv),
                         "%s should not be a link" % lnv)

    # -------------------------------------------------------------------------
    def test_setup_link_xlinkdir_nv_f(self):
        """
        existing link to an existing directory with an nv file with -f
        ./nv.py setup xlinkdir
        --> ln -s this xlinkdir/nv
        """
        stem = funcname()
        testlink = os.path.join(self.testdir, stem + "_l")
        fdir = os.path.join(self.testdir, stem + "_d")
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        lnv = os.path.join(fdir, "nv")
        open(lnv, 'w').close()
        os.symlink(fdir, testlink)

        result = nv.setup_link(testlink, self.nvpath, True)

        lnvorig = lnv + ".original"
        self.assertTrue(os.path.exists(lnvorig),
                        "%s should exist" % lnvorig)
        self.assertTrue(os.path.islink(lnv),
                        "%s should be a link" % lnv)
        self.assertEqual(self.nvpath, os.readlink(lnv),
                         "Expected '%s' -> '%s', got '%s' -> '%s'" %
                         (testlink, self.nvpath,
                          testlink, os.readlink(testlink)))

    # -------------------------------------------------------------------------
    def test_setup_link_xlinkfile(self):
        """
        existing link pointing at existing file
        ./nv.py setup xlinkfile
        --> err: 'xlinkfile exists; rename or use --force'
        """
        stem = funcname()
        testfile = os.path.join(self.testdir, stem + "_file")
        testlink = os.path.join(self.testdir, stem + "_link")
        open(testfile, 'w').close()
        os.symlink(testfile, testlink)
        
        result = nv.setup_link(testlink, self.nvpath, False)

        exp = ('%s -> %s; remove %s or use --force' %
               (testlink, testfile, testlink))
        self.assertTrue(exp in result,
                        "Expected '%s' in '%s'" % (exp, result))

    # -------------------------------------------------------------------------
    def test_setup_link_xlinkfile_f(self):
        """
        existing link pointing at existing file with --force
        ./nv.py setup -f xlinkfile
        --> unlink xlinkfile; ln -s this xlinkfile
        """
        stem = funcname()
        testfile = os.path.join(self.testdir, stem + "_file")
        testlink = os.path.join(self.testdir, stem + "_link")
        open(testfile, 'w').close()
        os.symlink(testfile, testlink)
        
        result = nv.setup_link(testlink, self.nvpath, True)

        exp = ('%s -> %s; remove %s or use --force' %
               (testlink, testfile, testlink))
        self.assertTrue(os.path.islink(testlink),
                        "Expected '%s' to be a link" % testlink)
        self.assertEqual(self.nvpath, os.readlink(testlink),
                         "Expected '%s' -> '%s', got '%s' -> '%s'" %
                         (testlink, self.nvpath,
                          testlink, os.readlink(testlink)))
