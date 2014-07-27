import sys

# -----------------------------------------------------------------------------
def main():
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

    try:
        func = getattr(__main__, "_".join(["nv", funcname]))
        func(args[2:])
    except AttributeError:
        fatal("nv function '%s' not found" % funcname)
                       
# -----------------------------------------------------------------------------
def nv_help(args):
    """help - show a list of available functions

    With no arguments, show a list of functions
    With a function as argument, show help for that function
    """
    if 3 <= len(args) and args[1] == "help" and args[2] == "help":
        print __doc__
    elif 3 <= len(args) and args[1] == 'help':
        fname = "_".join([prefix, args[2]])
        func = getattr(__main__, fname)
        print func.__doc__
    elif len(args) < 2 or args[1] in ['help', '-h', '--help']:
        # get a list of nv function names
        fnlist = [x for x in dir(__main__) if x.startswith("nv_")]
        # get a list of actual functions
        clist = [getattr(__main__, x) for x in fnlist]
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
def fatal(msg):
    """
    Print an error message and exit
    """
    print("")
    print("   %s" % msg)
    print("")
