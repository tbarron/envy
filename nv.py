#!/usr/bin/env python
import glob
import optparse
import os
import pdb
import stat
import sys

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
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    if o.dir in ['p', 'b']:
        conditionally_append('p')
    if o.dir in ['l', 'b']:
        conditionally_append('l')


# -----------------------------------------------------------------------------
def nv_deactivate(args):
    """deactivate - remove enable.snippet from the startup script(s)

    usage: nv deactivate [-D p|l]

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
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    if o.dir in ['p', 'b']:
        conditionally_remove('p')
    if o.dir in ['l', 'b']:
        conditionally_remove('l')


# -----------------------------------------------------------------------------
def nv_disable(args):
    """disable - make a snip non-executable so it cannot run

    usage: nv disable [-D p|l] <snip>

    Make snip executable. If envy is enabled in the correct start up script
    (.bahsrc or .profile), executable snips will be sourced.

    If -D p|l is specified, only the indicated set of snips (proc.d or login.d)
    will be considered.
    """
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help="run under pdb")
    p.add_option('-D', '--dir',
                 action='store', default='b', dest='dir',
                 help="p=proc.d, l=login.d")
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    for snip in a:
        if o.dir in ['p', 'b']:
            disable('p', snip)
        if o.dir in ['l', 'b']:
            disable('l', snip)


# -----------------------------------------------------------------------------
def nv_enable(args):
    """enable - make a snip executable so it can run

    usage: nv enable [-D p|l] <snip>

    Make snip executable. If envy is enabled in the correct start up script
    (.bahsrc or .profile), executable snips will be sourced.

    If -D p|l is specified, only the indicated set of snips (proc.d or login.d)
    will be considered.
    """
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help="run under pdb")
    p.add_option('-D', '--dir',
                 action='store', default='b', dest='dir',
                 help="p=proc.d, l=login.d")
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    for snip in a:
        if o.dir in ['p', 'b']:
            enable('p', snip)
        if o.dir in ['l', 'b']:
            enable('l', snip)


# -----------------------------------------------------------------------------
def nv_link(args):
    """link - make a link from dir or file to this program

    usage: nv.py link [$HOME/bin|/somewhere/nosuch]
    """
    p = optparse.OptionParser()
    p.add_option('-d', '--debug',
                 action='store_true', default=False, dest='debug',
                 help="run under pdb")
    (o, a) = p.parse_args(args)

    if o.debug:
        pdb.set_trace()

    try:
        target = a[0]
    except IndexError:
        fatal("Target directory or file is required")

    this = os.path.abspath(__file__)
    if os.path.isdir(target):
        os.symlink(this, os.path.join(target, "nv"))
    elif os.path.exists(target):
        os.symlink(this, target)
    else:
        fatal("Argument must be a directory or non-existent file")


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
def conditionally_append(which):
    """
    If the enable_snippet is in the startup file, say so. Otherwise, append the
    enable_snippet to the startup file.
    """
    (dname, tname, sname) = porl(which)

    f = open(tname, 'r')
    d = f.readlines()
    f.close()


    g = open(sname, 'r')
    e = g.readlines()
    g.close()
    signature = e[0]

    if signature in d:
        print("%s is already activated in %s" % (dname, tname))
        return

    f = open(tname, 'a')
    f.writelines(e)
    f.close()


# -----------------------------------------------------------------------------
def conditionally_remove(which):
    """
    If the enable_snippet is in the startup file, remove it. Otherwise, whine
    and die.
    """
    (dname, tname, sname) = porl(which)

    f = open(tname, 'r')
    d = f.readlines()
    f.close()


    g = open(sname, 'r')
    e = g.readlines()
    g.close()
    signature = e[0]

    if signature not in d:
        print("%s is not active in %s" % (dname, tname))
        return

    r = open(tname, 'r')
    w = open(tname + ".new", 'w')
    line = r.readline()
    while line != signature:
        w.write(line)
        line = r.readline()
    w.close()
    r.close()

    os.rename(tname, tname + ".original")
    os.rename(tname + ".new", tname)


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
    os.chmod(snippath, mode(snippath) & 0644)

    
# -----------------------------------------------------------------------------
def enable(which, snip):
    (dname, tname, sname) = porl(which)
    snippath = os.path.join(dname, snip)
    os.chmod(snippath, mode(snippath) | 0111)

    
# -----------------------------------------------------------------------------
def fatal(msg):
    """
    Print an error message and exit
    """
    print("")
    print("   %s" % msg)
    print("")
    sys.exit(1)


# -----------------------------------------------------------------------------
def memoize(f):
    memo = {}
    def helper(*args):
        if ''.join(args) not in memo:
            memo[''.join(args)] = f(*args)
        return memo[''.join(args)]
    return helper


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
        tname = os.path.join(home(), ".profile")
        sname = os.path.join(dname, "enable.snippet")
    else:
        fatal("directory must be 'p' or 'l'")
    return(dname, tname, sname)


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv)

