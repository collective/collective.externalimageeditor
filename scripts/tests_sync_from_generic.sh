#!/usr/bin/env bash
PROJECT="collective.externalimageeditor"
IMPORT_URL="git@github.com:collective/collective.externalimageeditor.git"
cd $(dirname $0)/..
[[ ! -d t ]] && mkdir t
rm -rf t/*
tar xzvf $(ls -1t ~/cgwb/$PROJECT*z) -C t
files="
src/collective/externalimageeditor/tests/globals.py
src/collective/externalimageeditor/tests/base.py
src/collective/externalimageeditor/testing.py
"
for f in $files;do
    rsync -azv t/$PROJECT/$f $f
done
# vim:set et sts=4 ts=4 tw=80: 
