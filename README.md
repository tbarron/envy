shnv
====

Manage shell environment across platforms and accounts

git clone this project into $HOME/.nv

If you want to install in a different directory, you'll need to edit
$GITROOT/proc.d/enable.snippet and $GITROOT/login.d/enable.snippet

The examples below assume $HOME/.nv. If you use some other directory,
adjust the filenames in the examples accordingly.

    cd $HOME/.nv
    ./nv.py link $HOME/bin
    nv help
    nv list

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
