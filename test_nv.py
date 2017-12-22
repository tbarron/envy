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


# -------------------------------------------------------------------------
def test_setup_link_xdir(tmpdir, fx_nvpath):
    """
    existing directory
    ./nv.py setup xdir
    --> ln -s this xdir/nv
    """
    pytest.debug_func()
    tdir = tmpdir.join('_dir')
    tdir.ensure(dir=True)
    tlink = tdir.join('nv')
    result = nv.setup_link(tdir.strpath, fx_nvpath.strpath, False)
    assert result == ''
    assert fx_nvpath.strpath == tlink.readlink()


# -----------------------------------------------------------------------------
def test_setup_link_xdir_f(tmpdir, fx_nvpath):
    """
    existing directory with --force
    ./nv.py setup -f xdir
    --> ln -s this xdir/nv
    """
    pytest.debug_func()
    tdir = tmpdir.join('_dir')
    tdir.ensure(dir=True)
    tlink = tdir.join('nv')
    assert not tlink.exists()
    result = nv.setup_link(tdir.strpath, fx_nvpath.strpath, True)
    assert result == ''
    assert fx_nvpath.strpath == tlink.readlink()


# -----------------------------------------------------------------------------
def test_setup_link_xfile(tmpdir, fx_nvpath):
    """
    existing file
    ./nv.py setup xfile
    --> err: 'rename xfile or use another link name'
    """
    pytest.debug_func()
    testfile = tmpdir.join('_link')
    testfile.ensure()
    result = nv.setup_link(testfile.strpath, fx_nvpath.strpath, False)
    exp = "%s is a file; rename it or use --force" % testfile
    assert exp in result
    assert not testfile.islink()
    origfile = py.path.local(testfile.strpath + '.original')
    assert not origfile.exists()


# -------------------------------------------------------------------------
def test_setup_link_xfile_f(tmpdir, fx_nvpath):
    """
    existing file with --force
    ./nv.py setup -f xfile
    --> mv xfile xfile.original; ln -s this xfile
    """
    pytest.debug_func()
    testfile = tmpdir.join('_link')
    testfile.ensure()
    result = nv.setup_link(testfile.strpath, fx_nvpath.strpath, True)
    assert result == ''
    assert testfile.islink()
    origfile = py.path.local(testfile.strpath + '.original')
    assert origfile.exists()
    assert fx_nvpath.strpath == testfile.readlink()


# -------------------------------------------------------------------------
def test_setup_link_xlink_nxfile(tmpdir, fx_nvpath):
    """
    existing link pointing at non existent file
    ./nv.py setup xlinkfile -> nx file
    --> err: 'xlinkfile exists; rename or use --force'
    """
    pytest.debug_func()
    testfile = tmpdir.join('_file')
    testlink = tmpdir.join('_link')
    assert not testfile.exists()
    testlink.mksymlinkto(testfile.strpath)
    result = nv.setup_link(testlink.strpath, fx_nvpath.strpath, False)
    exp = ('%s -> %s; remove %s or use --force' %
           (testlink.strpath, testfile.strpath, testlink.strpath))
    assert exp in result
    assert testlink.islink()
    assert testfile.strpath == testlink.readlink()


# -------------------------------------------------------------------------
def test_setup_link_xlink_nxfile_f(tmpdir, fx_nvpath):
    """
    existing link pointing at non existent file with --force
    ./nv.py setup -f xlinkfile
    --> rename xlinkfile; ln -s this xlinkfile
    """
    pytest.debug_func()
    testfile = tmpdir.join('_file')
    testlink = tmpdir.join('_link')
    assert not testfile.exists()
    testlink.mksymlinkto(testfile.strpath)
    result = nv.setup_link(testlink.strpath, fx_nvpath.strpath, True)
    assert result == ''
    assert testlink.islink()
    origlink = py.path.local(testlink.strpath + '.original')
    assert origlink.islink()
    assert fx_nvpath.strpath == testlink.readlink()


# -------------------------------------------------------------------------
def test_setup_link_xlinkdir_nonv(tmpdir, fx_nvpath):
    """
    existing link to an existing directory with no nv file
    ./nv.py setup xlinkdir
    --> ln -s this xlinkdir/nv
    """
    pytest.debug_func()
    testlink = tmpdir.join('_l')
    fdir = tmpdir.join('_d')
    fdir.ensure(dir=True)
    lnv = fdir.join('nv')
    assert not lnv.exists()
    testlink.mksymlinkto(fdir.strpath)
    result = nv.setup_link(testlink.strpath, fx_nvpath.strpath, False)
    assert result == ''
    lnvorig = py.path.local(lnv.strpath + '.original')
    assert not lnvorig.exists()
    assert lnv.islink()
    assert fx_nvpath.strpath == lnv.readlink()


# -------------------------------------------------------------------------
def test_setup_link_xlinkdir_nonv_f(tmpdir, fx_nvpath):
    """
    existing link to an existing directory with no nv file with -f
    ./nv.py setup xlinkdir
    --> ln -s this xlinkdir/nv
    """
    testlink = tmpdir.join('_l')
    fdir = tmpdir.join('_d')
    fdir.ensure(dir=True)
    lnv = fdir.join('nv')
    assert not lnv.exists()
    testlink.mksymlinkto(fdir.strpath)
    nvp = fx_nvpath
    result = nv.setup_link(testlink.strpath, nvp.strpath, True)
    assert result == ''
    lnvorig = py.path.local(lnv.strpath + '.original')
    assert not lnvorig.exists()
    assert lnv.islink()
    assert nvp.strpath == lnv.readlink()


# -------------------------------------------------------------------------
def test_setup_link_xlinkdir_nv(tmpdir, fx_nvpath):
    """
    existing link to an existing directory with an nv file
    ./nv.py setup xlinkdir
    --> ln -s this xlinkdir/nv
    """
    stem = "fump"
    testlink = tmpdir.join(stem + "_l")
    fdir = tmpdir.join(stem + "_d")
    fdir.ensure(dir=True)
    lnv = fdir.join("nv")
    lnv.ensure()
    testlink.mksymlinkto(fdir)

    result = nv.setup_link(testlink.strpath, fx_nvpath.strpath, False)

    exp = "".join([testlink.join("nv").strpath,
                   " is a file or directory; rename it or use --force"])
    assert exp in result

    lnvorig = py.path.local(lnv.strpath + ".original")
    assert not lnvorig.exists()
    assert not lnv.islink()


# -------------------------------------------------------------------------
def test_setup_link_xlinkdir_nv_f(tmpdir, fx_nvpath):
    """
    existing link to an existing directory with an nv file with -f
    ./nv.py setup xlinkdir
    --> ln -s this xlinkdir/nv
    """
    stem = "fump"
    testlink = tmpdir.join(stem + "_l")
    fdir = tmpdir.join(stem + "_d")
    fdir.ensure(dir=True)
    lnv = fdir.join("nv")
    lnv.ensure()
    testlink.mksymlinkto(fdir)
    result = nv.setup_link(testlink.strpath, fx_nvpath.strpath, True)
    assert result == ""
    lnvorig = py.path.local(lnv.strpath + ".original")
    assert lnvorig.exists()
    assert lnv.islink()
    assert fdir.strpath == testlink.readlink()


# -------------------------------------------------------------------------
def test_setup_link_xlinkfile(tmpdir, fx_nvpath):
    """
    existing link pointing at existing file
    ./nv.py setup xlinkfile
    --> err: 'xlinkfile exists; rename or use --force'
    """
    stem = "fump"
    testfile = tmpdir.join(stem + "_file")
    testlink = tmpdir.join(stem + "_link")
    testfile.ensure()
    testlink.mksymlinkto(testfile.strpath)
    result = nv.setup_link(testlink.strpath, fx_nvpath.strpath, False)
    exp = "{} -> {}; remove {} or use --force".format(testlink.strpath,
                                                      testfile.strpath,
                                                      testlink.strpath)
    assert exp in result


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
