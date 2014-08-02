envy
====

Manage shell environment across platforms and accounts

git clone this project into $HOME/.nv (which will be called $NV in
this document).

    git clone https://github.com/tbarron/envy.git

To be able to push updates:

    git clone git@github.com:tbarron/envy.git

(NOTE: If you want to install in a different directory, you'll need to
edit $NV/{proc,login}.d/enable.snippet (two files).

The examples below assume $HOME/.nv ($NV). If you use some other
directory, adjust the filenames in the examples accordingly.

    cd $NV
    ./nv.py setup $HOME/bin
    nv help
    nv list

$HOME/bin above can be whatever you like as long as 1) you have write
permission to it, and 2) it's in your $PATH.

Add snippets to .bashrc, .bash_profile to activate nv

    nv activate

Enable one or more startup plugins

    nv enable setenv setaliases setpath

Disable one or more plugins

    nv disable hostname.rc tomcat rvm pythonbrew

Remove the activation snippets from .bashrc, .bash_profile (the
comment that says "# added by envy. please do not edit anything from
here down" must be in tact for this to work).

     nv deactivate -D p      # remove from .bashrc
     nv deactivate -D l      # remove from .bash_profile
     nv deactivate           # remove from both


Details
-------

$NV/nv.py setup <dir>

    Create link <dir>/nv -> $NV/nv.py so you can issue nv
    commands by simply typing, for example, 'nv help'. <dir> should be
    in your $PATH.

nv help

    List the available functions in the nv program.

nv status

    Report whether envy has been activated in your .bashrc and
    .bash_profile.

nv activate [-D {l|p}]

    Add a snippet to the bottom of .bashrc (-D p) and/or .bash_profile
    (-D l) which will iterate through the files in $NV/proc.d
    and $NV/login.d respectively and source the ones with the
    execute bit.

nv deactivate [-D {l|p}]

    Remove the activation snippet from .bashrc (-D p) and/or
    .bash_profile (-D l). This depends on the envy signature line
    being intact. Everything from the signature line to the bottom of
    the file is removed.

nv list

    List the files in $NV/{proc,login}.d, reporting which have
    the execute bit (and will therefore be sourced at shell startup or
    login, respectively, and showing the one line description of what
    each file does (see 'File Descriptions' below).

nv disable

    Turn off the execute bit for specific files in $NV/{proc,login}.d.

nv enable

    Turn on the execute bit for specific files in $NV/{proc,login}.d.


File Descriptions
~~~~~~~~~~~~~~~~~

If a line like the following appears in a file in
$NV/{proc,login}.d:

    #!@! run $HOME/.local if it exists

everything on the line after "#!@!" will be used as a description of
the file by 'nv list'.


Debugging
~~~~~~~~~

Copy $NV/00.debug.sample to $NV/login.d/00.debug, enable it, and
you'll see which files get sourced at shell startup or login.
Debugging can be turned on and off by editing $NV/login.d/00.debug or
by removing and recopying $NV/00.debug.sample when it's wanted.
