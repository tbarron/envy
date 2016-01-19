#!@! setup db2 environment
debug
DB2PROF=/var/hpss/hpssdb/sqllib/db2profile
if [ -x $DB2PROF ]; then
   . /var/hpss/hpssdb/sqllib/db2profile
fi

