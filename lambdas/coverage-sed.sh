#!/bin/sh -eu

# SEDOPTION='-i ' 
SEDOPTION='-i '' '

sed -i '' "s@filename=\"@filename=\"lambda/@" coverage.xml
