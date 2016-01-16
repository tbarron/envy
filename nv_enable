export DIR=$HOME/.nv/${1}.d
if [ -d $DIR ]; then
    for FILE in $DIR/* ; do
        test -f "$FILE" || continue
        test -x "$FILE" || continue
        . "$FILE"
    done
fi
