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
import sqlite3
import subprocess


frontend_db = os.path.expanduser('~') + "/.pyRetro/frontend.db"
disabled_roms = 0

command = "mame -showconfig | grep 'snapshot_directory' | sed 's/snapshot_directory//' | sed 's/[ ]*//'"
proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
snapshot_directory = proc.communicate()[0].replace("$HOME", os.path.expanduser('~')) [: -1]

print("")
print(" Reading data base. Please wait")
print("")

connection = sqlite3.connect(frontend_db)
cursor = connection.cursor()
cursor.execute("UPDATE roms SET disabled = 0 WHERE status != 'bad';")
connection.commit()
print("")
cursor.execute("SELECT rom, id FROM roms WHERE found = 1;")
list_roms = cursor.fetchall()

for line in list_roms:
	rom_directory = line[0]
	id_rom = line[1]
	Absolute_Path = snapshot_directory + "/" + rom_directory
	Absolute_File = snapshot_directory + "/" + rom_directory + ".png"
	if not os.path.isdir(Absolute_Path) and not os.path.isfile(Absolute_File):
		cursor.execute("UPDATE roms SET disabled = 1 WHERE id = %i;" %id_rom)
		disabled_roms += 1

connection.commit()
print(" Disabled Roms: %i" % disabled_roms)
print("")
