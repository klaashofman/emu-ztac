#!/bin/sh

cd `dirname "$0"`
python pyRetro/pyRetro.py 2>&1 | tee pyretro.log
