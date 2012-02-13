#!/usr/bin/env bash
PROJECT="collective.externalimageeditor"
IMPORT_URL="git@github.com:collective/collective.externalimageeditor.git"
cd $(dirname $0)/..
[[ ! -d t ]] && mkdir t
rm -rf t/*
tar xzvf $(ls -1t ~/cgwb/$PROJECT*z) -C t
files="
./
"
for f in $files;do
    rsync -aKzv t/$PROJECT/$f $f
done
find t -name CHANG* -delete
# vim:set et sts=4 ts=4 tw=80: 
