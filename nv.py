#!/usr/bin/env python
import glob
import optparse
import os
import pdb
import shutil
import stat
import sys
import time


# -----------------------------------------------------------------------------
def main(args=None):
    """
    Entrypoint for 'nv(1)'
    """
    args = sys.argv
    try:
        funcname = args[1]
    except IndexError:
        nv_help(args)

    if funcname in ['help', '-h', '--help']:
        nv_help(args)
        return

    mod = sys.modules[__name__]
    try:
        func = getattr(mod, "_".join(["nv", funcname]))
        func(args[2:])
    except AttributeError:
        fatal("nv function '%s' not found" % funcname)


# -----------------------------------------------------------------------------
def nv_help(args):
    """help - show a list of available functions

    With no arguments, show a list of functions
    With a function as argument, show help for that function
    """
    mod = sys.modules[__name__]
    prefix = "nv"
    if 3 <= len(args) and args[1] == "help" and args[2] == "help":
        print nv_help.__doc__
    elif 3 <= len(args) and args[1] == 'help':
        fname = "_".join([prefix, args[2]])
        func = getattr(mod, fname)
        print func.__doc__
    elif len(args) < 2 or args[1] in ['help', '-h', '--help']:
        # get a list of nv function names
        fnlist = [x for x in dir(mod) if x.startswith("nv_")]
        # get a list of actual functions
        clist = [getattr(mod, x) for x in fnlist]
        # build a list of docstring headers
        try:
            dlist = [x.__doc__.split("\n")[0] for x in clist]
        except AttributeError:
            fatal("Function %s() needs a __doc__ string" % x.func_name)

        # now show the list of function one-liners
        dlist.sort()
        for line in dlist:
            print("   %s" % line)


# -----------------------------------------------------------------------------
def nv_activate(args):
    """activate - copy enable.snippet into the startup script(s)

    usage: nv activate [-D p|l]

    Copy proc.d/enable.snippet and/or login.d/enable.snippet into .bashrc
    and/or .profile, respectively.

    If -D p|l is specified, only the indicated startup file (.bashrc or
    .profile) will be updated.
    """
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help="run under pdb")
    p.add_option('-D', '--dir',
                 action='store', default='b', dest='dir',
                 help="p=proc.d, l=login.d")
    p.add_option('-f', '--filename',
                 action='store', default=None, dest='filename',
                 help="e.g., .zprofile, .zshrc")
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    if o.dir in ['p', 'b']:
        engage('p', filename=o.filename)
    if o.dir in ['l', 'b']:
        engage('l', filename=o.filename)


# -----------------------------------------------------------------------------
def nv_deactivate(args):
    """deactivate - remove enable.snippet from the startup script(s)

    usage: nv deactivate [-D p|l] [-f <filename>]

    Remove proc.d/enable.snippet and/or login.d/enable.snippet from .bashrc
    and/or .profile, respectively.

    If -D p|l is specified, only the indicated startup file (.bashrc or
    .profile) will be updated.
    """
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help="run under pdb")
    p.add_option('-D', '--dir',
                 action='store', default='b', dest='dir',
                 help="p=proc.d, l=login.d")
    p.add_option('-f', '--filename',
                 action='store', default=None, dest='filename',
                 help="e.g., .zshrc, .zprofile")
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    if o.dir in ['p', 'b']:
        disengage('p', filename=o.filename)
    if o.dir in ['l', 'b']:
        disengage('l', filename=o.filename)


# -----------------------------------------------------------------------------
def nv_disable(args):
    """disable - make a snip non-executable so it cannot run

    usage: nv disable [-D p|l] {--all|<snip> ...}

    Make snip executable. If envy is enabled in the correct start up script
    (.bahsrc or .profile), executable snips will be sourced.

    If -D p|l is specified, only the indicated set of snips (proc.d or login.d)
    will be considered.
    """
    p = optparse.OptionParser()
    p.add_option('-a', '--all',
                 action='store_true', default=False, dest='all',
                 help="disable everything")
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help="run under pdb")
    p.add_option('-D', '--dir',
                 action='store', default='b', dest='dir',
                 help="p=proc.d, l=login.d")
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    if o.all:
        make_sure("disable")
        if o.dir in ['l', 'b']:
            for snip in sniplist('l'):
                disable('l', snip)
        if o.dir in ['p', 'b']:
            for snip in sniplist('p'):
                disable('p', snip)
    else:
        # 'p' -> proc.d
        # 'l' -> login.d
        # 'b' -> both
        for snip in a:
            if o.dir in ['p', 'b']:
                disable('p', snip)
            if o.dir in ['l', 'b']:
                disable('l', snip)


# -----------------------------------------------------------------------------
def nv_enable(args):
    """enable - make a snip executable so it can run

    usage: nv enable [-D p|l] {--all|<snip> ...}

    Make snip executable. If envy is enabled in the correct start up script
    (.bahsrc or .profile), executable snips will be sourced.

    If -D p|l is specified, only the indicated set of snips (proc.d or login.d)
    will be considered.
    """
    p = optparse.OptionParser()
    p.add_option('-a', '--all',
                 action='store_true', default=False, dest='all',
                 help="disable everything")
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help="run under pdb")
    p.add_option('-D', '--dir',
                 action='store', default='b', dest='dir',
                 help="p=proc.d, l=login.d")
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    if o.all:
        make_sure("enable")
        if o.dir in ['l', 'b']:
            for snip in sniplist('l'):
                enable('l', snip)
        if o.dir in ['p', 'b']:
            for snip in sniplist('p'):
                enable('p', snip)
    else:
        # 'p' -> proc.d
        # 'l' -> login.d
        # 'b' -> both
        for snip in a:
            if o.dir in ['p', 'b']:
                enable('p', snip)
            if o.dir in ['l', 'b']:
                enable('l', snip)


# -----------------------------------------------------------------------------
def nv_setup(args):
    """setup - make a link from dir or file to this program

    usage: nv.py setup [$HOME/bin|/somewhere/nosuch]

    Also, copy 00.debug.sample to login.d/00.debug if login.d/00.debug does not
    exist.
    """
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help="run under pdb")
    p.add_option('-f', '--force',
                 action='store_true', default=False, dest='force',
                 help="overwrite existing symlink")
    p.add_option('-l', '--linkname',
                 action='store', default="", dest='linkname',
                 help="alternate name for 'nv'")
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    try:
        linksrc = a[0]
    except IndexError:
        fatal("Link directory or file is required")

    msg = setup_link(linksrc, os.path.abspath(__file__), o.force)
    if msg != '':
        fatal(msg)

    # copy $NV/00.debug.sample $NV/login.d/00.debug
    nvroot = os.path.dirname(__file__)
    debug_sample = os.path.join(nvroot, "00.debug.sample")
    debug = os.path.join(nvroot, "login.d", "00.debug")
    if not os.path.exists(debug):
        shutil.copy(debug_sample, debug)


# -----------------------------------------------------------------------------
def nv_list(args):
    """list - list the snips that can be turned on or off

    usage: nv.py list [proc|login]
    """
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help="run under pdb")
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    try:
        home = os.environ["HOME"]
    except KeyError:
        fatal("Please set $HOME and try again")

    nvroot = os.path.join(home, ".nv")
    # pdir = os.path.join(nvroot, "proc.d")
    # ldir = os.path.join(nvroot, "login.d")
    for dir in [os.path.join(nvroot, "proc.d"),
                os.path.join(nvroot, "login.d")]:
        print os.path.basename(dir)
        for fname in glob.glob(os.path.join(dir, "*")):
            bname = os.path.basename(fname)
            if fname.endswith("~") or bname == "enable.snippet":
                continue
            if os.access(fname, os.X_OK):
                status = "on"
            else:
                status = "OFF"
            print("   %-15s %3s %s" %
                  (bname, status, description(fname)))


# -----------------------------------------------------------------------------
def memoize(f):
    memo = {}

    def helper(*args):
        if ''.join(args) not in memo:
            memo[''.join(args)] = f(*args)
        return memo[''.join(args)]

    return helper


# -----------------------------------------------------------------------------
def contents(filename):
    """
    return the contents of *filename*
    """
    f = open(filename, 'r')
    c = f.readlines()
    f.close()
    return c


# -----------------------------------------------------------------------------
def disengage(which, filename=None):
    """
    if target.%Y.%m%d.%H%M%S exists,
       move target to target.nv
       move target.%Y.%m%d.%H%M%S to target
    """
    h = which_dict()
    z = h[which]
    target = filename or expand(z['target'])
    signature = h['signature']

    c = contents(target)

    if all([signature not in x for x in c]):
        print("%s is already deactivated" % target)
        return

    clist = sorted(glob.glob("%s.*" % target))
    if len(clist) < 1:
        print("Nothing to fall back to")
    else:
        fallback = clist[-1]
        os.unlink(target)
        os.rename(fallback, target)


# -----------------------------------------------------------------------------
def engage(which, filename=None):
    """
    if signature in target file, say so and stop
    move target file to target.YYYY.mmdd.HHMMSS
    put appropriate profile invocation in target file with signature
    """
    h = which_dict()
    z = h[which]
    target = filename or resolve(z['target'])
    signature = h['signature']
    try:
        c = contents(target)
    except IOError:
        c = []

    if signature in "\n".join(c):
        print('nv is already activated for %s' % target)
        return

    moved = ''
    if os.path.exists(target):
        newname = '%s.%s' % (target, time.strftime("%Y.%m%d.%H%M%S"))
        os.rename(target, newname)
        moved = '{0} has been moved to {1}'.format(target, newname)
        moved = '\n'.join(['{0} has been moved to {1}',
                           "for anything from {1} that needs to be kept,"
                           " please",
                           "put it in a script under {2} and enable it"])
        moved = moved.format(target, newname, z['dirname'])
    f = open(target, 'w')
    f.write('# added by nv. please do not edit.\n')
    f.write('%s\n' % z['cmd'])
    f.close()

    print("nv has been activated.")
    print(moved)


# -----------------------------------------------------------------------------
def expand(value):
    """
    Apply os.path.expanduser() and os.path.expandvars() to a string
    """
    return os.path.expandvars(os.path.expanduser(value))


# -----------------------------------------------------------------------------
def description(fpath):
    f = open(fpath, 'r')
    z = f.readlines()
    f.close()
    for x in z:
        if '#!@!' in x:
            return x.replace('#!@!', '').strip()
    return fpath


# -----------------------------------------------------------------------------
def disable(which, snip):
    (dname, tname, sname) = porl(which)
    snippath = os.path.join(dname, snip)
    if os.path.exists(snippath):
        os.chmod(snippath, mode(snippath) & 0666)


# -----------------------------------------------------------------------------
def enable(which, snip):
    (dname, tname, sname) = porl(which)
    snippath = os.path.join(dname, snip)
    if os.path.exists(snippath):
        os.chmod(snippath, mode(snippath) | 0111)


# -----------------------------------------------------------------------------
def fatal(msg):
    """
    Print an error message and exit
    """
    sys.exit("%s" % msg)


# -----------------------------------------------------------------------------
def sniplist(porl):
    """
    Return a list of snips from nvdir/proc.d (porl == 'p') or nvdir/login.d
    (porl == 'l').
    """
    nvdir = get_nvdir()
    which = {'p': 'proc.d', 'l': 'login.d'}[porl]
    bnlist = [os.path.basename(x) for x in glob.glob(os.path.join(nvdir,
                                                                  which,
                                                                  "*"))]
    if 'enable.snippet' in bnlist:
        bnlist.remove('enable.snippet')
    return bnlist


# -----------------------------------------------------------------------------
@memoize
def get_nvdir():
    script = __file__
    while os.path.islink(script):
        script = os.readlink(script)
    return os.path.dirname(script)


# -----------------------------------------------------------------------------
def make_sure(action):
    ans = raw_input("About to %s everything!!!\n" % action +
                    "If you're sure, type 'yes' > ")
    if ans != 'yes':
        sys.exit(0)


# -----------------------------------------------------------------------------
@memoize
def home():
    try:
        rval = os.environ["HOME"]
        return rval
    except KeyError:
        fatal("Please set $HOME and try again")


# -----------------------------------------------------------------------------
def mode(path):
    s = os.stat(path)
    return s[stat.ST_MODE]


# -----------------------------------------------------------------------------
def porl(which):
    """
    Return ($HOME/.nv/proc.d, $HOME/.bashrc, $HOME/.nv/enable.snippet),
    ($HOME/.nv/login.d, $HOME/.profile, $HOME/.nv/enable.snippet), or
    whine and die.
    """
    if which == 'p':
        dname = os.path.join(home(), ".nv", "proc.d")
        tname = os.path.join(home(), ".bashrc")
        sname = os.path.join(dname, "enable.snippet")
    elif which == 'l':
        dname = os.path.join(home(), ".nv", "login.d")
        sname = os.path.join(dname, "enable.snippet")
        for tname in [os.path.join(home(), ".zprofile"),
                      os.path.join(home(), ".profile"),
                      os.path.join(home(), ".bash_profile")]:
            if os.path.exists(tname):
                break
    else:
        fatal("directory must be 'p' or 'l'")
    return(dname, tname, sname)


# -----------------------------------------------------------------------------
def setup_link(linksrc, dstpath, force):
    rval = ""
    if os.path.islink(linksrc):
        if os.path.isdir(linksrc):
            rval = setup_link_indir(linksrc, dstpath, force)
        elif os.readlink(linksrc) == dstpath:
            rval = "%s -> %s already" % (linksrc, dstpath)
        elif force:
            os.rename(linksrc, linksrc + ".original")
            os.symlink(dstpath, linksrc)
        else:
            rval = ("%s -> %s; remove %s or use --force" %
                    (linksrc, os.readlink(linksrc), linksrc))
    elif os.path.isdir(linksrc):
        rval = setup_link_indir(linksrc, dstpath, force)
    elif os.path.isfile(linksrc):
        if force:
            os.rename(linksrc, linksrc + ".original")
            os.symlink(dstpath, linksrc)
        else:
            rval = ("%s is a file; rename it or use --force" % linksrc)
    elif not os.path.exists(linksrc):
        os.symlink(dstpath, linksrc)
    else:
        if force:
            os.rename(linksrc, linksrc + ".original")
            os.symlink(dstpath, linksrc)
        else:
            rval = ("%s exists;" % linksrc +
                    " rename it or use --force")
    return rval


# -----------------------------------------------------------------------------
def setup_link_indir(linksrc, dstpath, force):
    rval = ""
    linknv = os.path.join(linksrc, "nv")
    if not os.path.exists(linknv):
        os.symlink(dstpath, linknv)
    elif os.path.isfile(linknv) or os.path.isdir(linknv):
        if force:
            os.rename(linknv, linknv + ".original")
            os.symlink(dstpath, linknv)
        else:
            rval = ("%s is a file or directory; rename it or use --force" %
                    linknv)
    elif os.path.islink(linknv):
        if os.readlink(linknv) == dstpath:
            rval = ("%s -> %s already" % (linknv, dstpath))
        elif force:
            os.rename(linknv, linknv + ".original")
            os.symlink(dstpath, linknv)
        else:
            rval = ("%s is a link to %s; rename it or use --force" %
                    (linknv, os.readlink(linknv)))
    elif force:
        os.rename(linknv, linknv + ".original")
        os.symlink(dstpath, linknv)
    else:
        rval = ("%s exists; rename it or use --force" % linknv)
    return rval


# -----------------------------------------------------------------------------
def resolve(poss):
    """
    Figure out which file of a list exists.
    """
    if type(poss) == str:
        return expand(poss)
    elif type(poss) == list:
        for z in poss:
            p = expand(z)
            if os.path.exists(p):
                return p


# -----------------------------------------------------------------------------
def which_dict():
    h = {'p': {'stem': 'proc',
               'dirname': '$HOME/.nv/proc.d',
               'target': '$HOME/.bashrc',
               'cmd': '. $HOME/.nv/nv_enable proc'},
         'l': {'stem': 'login',
               'dirname': '$HOME/.nv/login.d',
               'target': ['$HOME/.bash_profile', '$HOME/.profile'],
               'cmd': '. $HOME/.nv/nv_enable login'},
         'signature': '# added by nv.'}
    return h


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv)
