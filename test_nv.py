import glob
import nv
import os
import pexpect
import py
import pytest


# -----------------------------------------------------------------------------
def test_flake8():
    """
    Style the code
    """
    pytest.debug_func()
    files = glob.glob('*.py')
    result = pexpect.run("flake8 {}".format(' '.join(files)))
    assert result == ''


# -----------------------------------------------------------------------------
def test_help():
    pytest.debug_func()
    actual = pexpect.run("./nv.py help")
    exp = ["activate - copy enable.snippet into the startup script(s)",
           "deactivate - remove enable.snippet from the startup script(s)",
           "disable - make a snip non-executable so it cannot run",
           "enable - make a snip executable so it can run",
           "help - show a list of available functions",
           "list - list the snips that can be turned on or off",
           "setup - make a link from dir or file to this program"]
    for p in exp:
        assert p in actual


# -----------------------------------------------------------------------------
def test_porl():
    pytest.debug_func()
    home = os.getenv("HOME")
    dname = os.path.join(home, ".nv", "proc.d")
    exp = (dname,
           os.path.join(home, ".bashrc"),
           os.path.join(dname, "enable.snippet"))
    actual = nv.porl('p')
    assert exp == actual, "Expected '%s', got '%s'" % (exp, actual)

    dname = os.path.join(home, ".nv", "login.d")
    exp = (dname,
           glob.glob(os.path.join(home, ".*profile"))[0],
           os.path.join(dname, "enable.snippet"))
    actual = nv.porl('l')
    assert exp == actual, "Expected '%s', got '%s'" % (exp, actual)

    with pytest.raises(SystemExit) as err:
        nv.porl('q')
    assert "directory must be 'p' or 'l'" in str(err)


# -----------------------------------------------------------------------------
def test_setup_link_noarg(tmpdir):
    """
    ./nv.py setup
    --> err: 'must specify link location'
    """
    pytest.debug_func()
    exp = "Link directory or file is required"
    with pytest.raises(SystemExit) as err:
        nv.nv_setup([])
    assert exp in str(err)


# -----------------------------------------------------------------------------
def test_setup_link_noarg_f():
    """
    ./nv.py setup -f
    --> err: 'must specify link location'
    """
    pytest.debug_func()
    exp = "Link directory or file is required"
    with pytest.raises(SystemExit) as err:
        nv.nv_setup(['-f'])
    assert exp in str(err)


# -----------------------------------------------------------------------------
def test_setup_link_nx(tmpdir, fx_nvpath):
    """
    non-existent file
    ./nv.py setup nx
    --> ln -s this nx
    """
    pytest.debug_func()
    testfile = tmpdir.join('nosuch')
    if testfile.exists():
        testfile.remove()
    nv.setup_link(testfile.strpath, fx_nvpath.strpath, False)
    assert testfile.islink()
    assert fx_nvpath == testfile.readlink()


# -----------------------------------------------------------------------------
def test_setup_link_nx_f(tmpdir, fx_nvpath):
    """
    ./nv.py setup -f nx
    --> ln -s this nx
    """
    pytest.debug_func()
    testfile = tmpdir.join('nosuch')
    assert not testfile.exists()
    nv.setup_link(testfile.strpath, fx_nvpath.strpath, True)
    assert testfile.islink()
    assert fx_nvpath.strpath == testfile.readlink()



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
    def test_help(self):
        actual = pexpect.run("./nv.py help")
        exp = [
            "activate - copy enable.snippet into the startup script(s)",
            "deactivate - remove enable.snippet from the startup script(s)",
            "disable - make a snip non-executable so it cannot run",
            'enable - make a snip executable so it can run',
            'help - show a list of available functions',
            'list - list the snips that can be turned on or off',
            'setup - make a link from dir or file to this program', 
            ]
        for p in exp:
            self.assertTrue(p in actual,
                            "Expected '%s' in '%s'" % (p, actual))


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
        stem = funcname()
        tdir = os.path.join(self.testdir, stem + "_dir")
        os.makedirs(tdir)
        tlink = os.path.join(tdir, "nv")
        if os.path.islink(tlink):
            os.unlink(tlink)

        result = nv.setup_link(tdir, self.nvpath, False)

        self.assertEqual(self.nvpath, os.readlink(tlink),
                         "Expected '%s' -> '%s'; got '%s' -> '%s'" %
                         (tlink, self.nvpath, tlink, os.readlink(tlink)))

    # -------------------------------------------------------------------------
    def test_setup_link_xdir_f(self):
        """
        existing directory with --force
        ./nv.py setup -f xdir
        --> ln -s this xdir/nv
        """
        stem = funcname()
        tdir = os.path.join(self.testdir, stem + "_dir")
        os.makedirs(tdir)
        tlink = os.path.join(tdir, "nv")
        if os.path.islink(tlink):
            os.unlink(tlink)

        result = nv.setup_link(tdir, self.nvpath, True)

        self.assertEqual(self.nvpath, os.readlink(tlink),
                         "Expected '%s' -> '%s'; got '%s' -> '%s'" %
                         (tlink, self.nvpath, tlink, os.readlink(tlink)))

    # -------------------------------------------------------------------------
    def test_setup_link_xfile(self):
        """
        existing file
        ./nv.py setup xfile
        --> err: 'rename xfile or use another link name'
        """
        stem = funcname()
        testfile = os.path.join(self.testdir, stem + "_link")
        open(testfile, 'w').close()

        result = nv.setup_link(testfile, self.nvpath, False)

        exp = "%s is a file; rename it or use --force" % testfile
        self.assertTrue(exp in result,
                        "Expect '%s' in '%s'" % (exp, result))
        self.assertFalse(os.path.islink(testfile),
                        "Expected '%s' to not be a link" % testfile)
        self.assertFalse(os.path.exists(testfile + ".original"),
                        "Did not expect '%s' to be renamed to '%s'" %
                        (testfile, testfile + ".original"))

    # -------------------------------------------------------------------------
    def test_setup_link_xfile_f(self):
        """
        existing file with --force
        ./nv.py setup -f xfile
        --> mv xfile xfile.original; ln -s this xfile
        """
        stem = funcname()
        testfile = os.path.join(self.testdir, stem + "_link")
        open(testfile, 'w').close()

        result = nv.setup_link(testfile, self.nvpath, True)

        self.assertTrue(os.path.islink(testfile),
                        "Expected '%s' to be a link" % testfile)
        self.assertTrue(os.path.exists(testfile + ".original"),
                        "Expected '%s' to be renamed to '%s'" %
                        (testfile, testfile + ".original"))
        self.assertEqual(self.nvpath, os.readlink(testfile),
                         "Expected '%s' -> '%s'; got '%s' -> '%s'" %
                         (testfile, self.nvpath,
                          testfile, os.readlink(testfile)))

    # -------------------------------------------------------------------------
    def test_setup_link_xlink_nxfile(self):
        """
        existing link pointing at non existent file
        ./nv.py setup xlinkfile -> nx file
        --> err: 'xlinkfile exists; rename or use --force'
        """
        stem = funcname()
        testfile = os.path.join(self.testdir, stem + "_file")
        testlink = os.path.join(self.testdir, stem + "_link")
        if os.path.exists(testfile):
            os.unlink(testfile)
        os.symlink(testfile, testlink)

        result = nv.setup_link(testlink, self.nvpath, False)

        exp = ('%s -> %s; remove %s or use --force' %
               (testlink, testfile, testlink))
        self.assertTrue(exp in result,
                        "Expected '%s' in '%s'" % (exp, result))
        self.assertTrue(os.path.islink(testlink),
                        "Expected '%s' to be a link" % testlink)
        self.assertEqual(testfile, os.readlink(testlink),
                         "Expected '%s' -> '%s', got '%s' -> '%s'" %
                         (testlink, testfile,
                          testlink, os.readlink(testlink)))

    # -------------------------------------------------------------------------
    def test_setup_link_xlink_nxfile_f(self):
        """
        existing link pointing at non existent file with --force
        ./nv.py setup -f xlinkfile
        --> rename xlinkfile; ln -s this xlinkfile
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
        self.assertTrue(os.path.islink(testlink + ".original"),
                        "Expected '%s' to be a link" %
                        testlink + ".original")
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
        stem = funcname()
        testlink = os.path.join(self.testdir, stem + "_l")
        fdir = os.path.join(self.testdir, stem + "_d")
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        lnv = os.path.join(fdir, "nv")
        if os.path.exists(lnv):
            os.unlink(lnv)
        os.symlink(fdir, testlink)

        result = nv.setup_link(testlink, self.nvpath, False)

        exp = ""
        self.assertEqual(exp, result,
                        "Expected '%s' to be empty" % (result))
        lnvorig = lnv + ".original"
        self.assertFalse(os.path.exists(lnvorig),
                         "%s should not exist" % lnvorig)
        self.assertTrue(os.path.islink(lnv),
                         "%s should not be a link" % lnv)
        self.assertEqual(self.nvpath, os.readlink(lnv),
                         "Expected '%s' to point at '%s'" %
                         (lnv, self.nvpath))

    # -------------------------------------------------------------------------
    def test_setup_link_xlinkdir_nonv_f(self):
        """
        existing link to an existing directory with no nv file with -f
        ./nv.py setup xlinkdir
        --> ln -s this xlinkdir/nv
        """
        stem = funcname()
        testlink = os.path.join(self.testdir, stem + "_l")
        fdir = os.path.join(self.testdir, stem + "_d")
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        lnv = os.path.join(fdir, "nv")
        if os.path.exists(lnv):
            os.unlink(lnv)
        os.symlink(fdir, testlink)

        result = nv.setup_link(testlink, self.nvpath, True)


        exp = ""
        self.assertEqual(exp, result,
                        "Expected '%s' to be empty" % (result))
        lnvorig = lnv + ".original"
        self.assertFalse(os.path.exists(lnvorig),
                         "%s should not exist" % lnvorig)
        self.assertTrue(os.path.islink(lnv),
                         "%s should not be a link" % lnv)
        self.assertEqual(self.nvpath, os.readlink(lnv),
                         "Expected '%s' to point at '%s'" %
                         (lnv, self.nvpath))

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
def test_setup_link_xlinkfile_f(tmpdir, fx_nvpath):
    """
    existing link pointing at existing file with --force
    ./nv.py setup -f xlinkfile
    --> unlink xlinkfile; ln -s this xlinkfile
    """
    stem = "fump"
    testfile = tmpdir.join(stem + "_file")
    testlink = tmpdir.join(stem + "_link")
    testfile.ensure()
    testlink.mksymlinkto(testfile.strpath)
    result = nv.setup_link(testlink.strpath, fx_nvpath.strpath, True)
    assert result == ""
    assert testlink.islink()
    assert fx_nvpath.strpath == testlink.readlink()


@pytest.fixture
def fx_nvpath():
    """
    Set up nvpath for tests that use it
    """
    nvpath = py.path.local('nv.py')
    return nvpath
