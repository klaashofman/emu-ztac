# -*- coding: utf-8 -*-
"""
   Copyright (C) 2011 Oscar José Rivera Verde

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3 of the License, or
   higher any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software Foundation,
   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
"""

import os
import subprocess


print("")
print("")
print(" Clear bad roms may make some roms stop working because some are related to ")
print(" oters. I recommend to make a backup from the roms directory to test this ")
print(" feature, to merge the roms with an auditory aplication or something like that")
print(" would be nice. Make this at your own risk.")
print("")

key = raw_input("Do you wish to continue? ")
if not key.lower() == "y":
    exit()

deleted_roms = 0
ghost_roms = 0

command = 'mame -verifyroms | grep romset | grep bad | '
command += 'sed "s/romset //" | sed "s/\[.*\] //" |'
command += '  sed "s/ is bad/.zip/"'

proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

print("")
print("")
print("Scaning roms. This may belongs a few minutes")
print("")

output = proc.communicate()[0]
output_lines = output.split("\n")

for line in output_lines:
    Absolute_Path = os.path.expanduser('~') + '/MAME/roms/' + line
    if os.path.isfile(Absolute_Path):
        os.remove(Absolute_Path)
        deleted_roms += 1

    else:
        ghost_roms += 1

print("Deleted roms: %i" % deleted_roms)
print("Ghost roms: %i" % ghost_roms)
print("")
print("Ghost roms may be contained inside another working rom, this hapens")
print("when there are merged roms.")
print("")

