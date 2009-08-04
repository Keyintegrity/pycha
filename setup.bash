#!/usr/bin/env bash

pkg=pycha
. simple-setup.bash

version=$( python -c "import sys; print '.'.join(map(str,sys.version_info[:2]))" )
install lib/python$version/site-packages/ pycha
