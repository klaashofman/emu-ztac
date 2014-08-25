# -*- coding: utf-8 -*-
"""
   Copyright (C) 2011 David Colmenero - D_Skywalk

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
import sys
import subprocess
import getopt
import threading
import ConfigParser
import sqlite3

EXTENSION="avi"
FFMPEG_EXE="ffmpeg"
FFMPEG_FLG=" -y -vcodec mpeg1video -pix_fmt yuv422p -qscale 1 -qmin 3 -intra -acodec mp2 -ar 44100 "
FFMPEG_FLG_LO=" -y -r 30 -vcodec mpeg1video -pix_fmt yuv422p -qscale 1 -qmin 6 -intra -acodec mp2 -ar 44100 "

print "pyRetro - TOOLS"

frontend_db = os.path.expanduser('~') + "/.pyRetro/frontend.db"
file_config = os.path.expanduser('~') + "/.pyRetro/config.cfg"
converted_videos = 0
found_games = 0

ret = subprocess.call("which ffmpeg", shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
if ret != 0:
	print "err! Sorry ffmpeg is need it for convert videos..."
	exit()

args = sys.argv[1:]
if len(args) < 1:
	print " Simple convert pygame video"
	print " * Converts AVI files (using rom db) to compatible MPEG1 videos."
	print "   (need ffmpeg already installed)"
	print " "
	print "USAGE: " + sys.argv[0] + " [-l] DIRECTORY"
	print "  -l: convert using low-quality ffmpeg opts."
	exit()


cfg = ConfigParser.ConfigParser()
cfg.read(file_config)
dir_output = cfg.get("pyRetro", "dir_default_game_video")

if dir_output == "":
	print "err! Please update your config.cfg -  'dir_default_game_video' not found"
	exit(2)
elif not os.path.exists(dir_output):
	print "err! DIR: \"" + dir_output + "\" not found... Create it!"
	exit(2)
elif not dir_output[-1] == '/':
	dir_output += '/'

DIRECTORY = ""

for opt in args:
	if opt == "-l":
		FFMPEG_FLG = FFMPEG_FLG_LO
		print " Using LOW-QUALITY opts!"
	else:
		DIRECTORY = opt

if DIRECTORY == "":
	print "err! Please set directory..."
	exit(2)
elif not os.path.exists(DIRECTORY):
	print "err! DIR: \"" + DIRECTORY + "\" not found..."
	exit(2)
elif not DIRECTORY[-1] == '/':
	DIRECTORY += '/'



print "Config: Ok!"
print "Video Output: " + dir_output
print "Video Input: " + DIRECTORY
print " "

connection = sqlite3.connect(frontend_db)
cursor = connection.cursor()
cursor.execute("SELECT rom, id FROM roms WHERE found = 1 AND disabled = 0;")
list_roms = cursor.fetchall()

for line in list_roms:
	rom_directory = line[0]
	Absolute_FileAVI = DIRECTORY + rom_directory + "." + EXTENSION
	found_games += 1
	if os.path.isfile(Absolute_FileAVI):
		Absolute_FileMPG = dir_output + rom_directory + ".mpg"
		Absolute_FileTMP = "/tmp/" + rom_directory + ".mpg"
		command = FFMPEG_EXE + " -i \"" + Absolute_FileAVI + "\"" + FFMPEG_FLG + "\"" + Absolute_FileTMP + "\""
		sys.stdout.write(Absolute_FileAVI + " >> " + Absolute_FileMPG + " ")
		sys.stdout.flush()
		proc = subprocess.Popen(command, shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		proc.wait()
		if proc.returncode != 0:
			print "FFMPEG Error Output:"
			print "===================="
			stout, sterr = proc.communicate()
			for line in sterr.split('\n'):
				if not 'configuration' in line:
					print line
			break
		converted_videos += 1
		os.system("mv " + Absolute_FileTMP + " " + Absolute_FileMPG)
		print("[OK]")
		
print "... process finished ( %i / %i )" % ( converted_videos, found_games )
