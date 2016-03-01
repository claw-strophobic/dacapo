#!/bin/bash
xgettext -j --omit-header -d dacapo-plugins -p ./po/ dacapo/ql-plugins/*.py
find . -iname "*.py" | xargs xgettext -j --omit-header -d dacapo -p ./po/ 
