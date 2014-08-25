# -*- coding: utf-8 -*-
"""
   Copyright (C) 2011 Miguel de Dios

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
import getopt
import subprocess
import threading
import ConfigParser
import sqlite3
import time

# from pprint import *
#thanks to Trent Mick (http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/475126)
try:
    import xml.etree.cElementTree as ET # python >=2.5 C module
except ImportError:
    try:
        import xml.etree.ElementTree as ET # python >=2.5 pure Python module
    except ImportError:
        try:
            import cElementTree as ET # effbot's C module
        except ImportError:
            try:
                import elementtree.ElementTree as ET # effbot's pure Python module
            except ImportError:
                try:
                    import lxml.etree as ET # ElementTree API using libxml2
                except ImportError:
                    import warnings
                    warnings.warn("could not import ElementTree "
                                              "(http://effbot.org/zone/element-index.htm)")

class Util:
    file_config = None
    frontend_db = None
    options = {}

    def __init__(self):
        # self.import_etree()
        self.file_config = os.path.join(os.path.expanduser('~'), ".pyRetro", "config.cfg")
        self.frontend_db = os.path.join(os.path.expanduser('~'), ".pyRetro", "frontend.db")
        self.mameinfo_xml = os.path.join(os.path.expanduser('~'), ".pyRetro", "mameinfo.xml")

        self.parse_args()

        if not self.options['run']:
            return

        if os.path.exists(self.file_config):
            self.parse_config_file()
            self.get_mame_confs()
            self.create_mameinfo()
            if self.db_fail():
                self.create_db()
                self.scan_roms()
            else:
                self.update_db()
        else:
            print("Don't exist the config file in " + self.file_config)
            print("Create the default config.")
            self.create_default_config()
            self.parse_config_file()
            self.get_mame_confs()
            self.create_mameinfo()
            self.create_db()
            self.scan_roms()


    def load_value_db(self, token, default_var = None):
        connection = sqlite3.connect(self.frontend_db)
        cursor = connection.cursor()
        cursor.execute("SELECT value, type FROM save_data WHERE token = '" + token + "';")
        rows = cursor.fetchall()

        if not rows:
            return default_var
        row = rows[0]
        if row[1] == 'int':
            return int(row[0])
        elif row[1] == 'float':
            return float(row[0])
        else:
            return row[0]


    def save_value_db(self, token, value, type_token = "string"):
        connection = sqlite3.connect(self.frontend_db)
        cursor = connection.cursor()

        cursor.execute("SELECT value, type FROM save_data WHERE token = '" + token + "';")
        rows = cursor.fetchall()

        if not rows:
            cursor.execute("INSERT INTO save_data (token, value, type) " + \
                    "values ('" + token + "', '" + str(value) + "', '" + type_token + "')")
            connection.commit()
        else:
            row = rows[0]
            if row[0] != str(value) or row[1] != type_token:
                cursor.execute("UPDATE save_data " + \
                        "set value = '" + str(value) + "', type = '" + type_token + "'" + \
                        "WHERE token = '" + token + "';")
                connection.commit()


    def create_default_config(self):
        if not os.path.exists(os.path.join(os.path.expanduser('~'), ".pyRetro")):
            os.mkdir(os.path.join(os.path.expanduser('~'),".pyRetro"))

        default_conf = ""
        default_conf += "#CONF FILE -- pyRetro\n"
        default_conf += "\n"
        default_conf += "[pyRetro]"
        default_conf += "\n"
        default_conf += "#MAME EXECUTABLE LOCATION\n"
        default_conf += "mame_executable=mame\n"
        default_conf += "mame_options=\n"
        default_conf += "\n"
        default_conf += "#VIEW MODE\n"
        default_conf += "# 1 SNAPSHOP FULLSCREEN\n"
        default_conf += "# 2 GRID (sorry, no Grid-mode yet)\n"
        default_conf += "# 3 LAYOUT\n"
        default_conf += "# 4 WEIRD SNAPSHOP\n"
        default_conf += "\n"
        default_conf += "view_mode=3\n" # changed to layout by default :P
        default_conf += "\n"
        default_conf += "#GENERAL OPTIONS\n"
        default_conf += "screen_width=640\n"
        default_conf += "screen_height=480\n"
        default_conf += "shutdown_on_exit=0\n"
        default_conf += "shutdown_command=/usr/bin/sudo /sbin/shutdown -h now\n"
        default_conf += "\n"
        default_conf += "#VIDEO OPTIONS\n"
        default_conf += "dir_default_game_video=video\n"
        default_conf += "seconds_wait_video=5\n"
        default_conf += "\n"
        default_conf += "#SCREEN SAVER OPTIONS\n"
        default_conf += "time_to_show_screensaver=240\n"
        default_conf += "seconds_wait_between_screensaver_images=3\n"
        default_conf += "can_played_game_show_in_screensaver=1\n"
        default_conf += "dir_default_images_screensaver=screen_saver_images\n"
        default_conf += "random_percent_default_images_screensaver=50\n"
        default_conf += "# 1 OFF\n"
        default_conf += "# 1 ALL\n"
        default_conf += "transational_effect_screensaver=0\n"
        default_conf += "\n"
        default_conf += "#VIEW MODE (SNAPSHOP FULLSCREEN) OPTIONS\n"
        default_conf += "default_background=background_default_small.png\n"
        default_conf += "\n"
        default_conf += "#HERE YOU CAN FILTER YOU GAME LIST (only by gamebutton number) 0 - OFF 1 - ON\n"
        default_conf += "filter=0\n"
        default_conf += "filter_game_buttons=3\n"
        open(self.file_config, 'w').write(default_conf)

        print("Create default conf file in: " + self.file_config)


    def create_mameinfo(self):
        if os.path.exists(self.mameinfo_xml):
            return

        print("MAMEINFO in progress, please wait.")
        command = self.options["mame_executable"] + " -listxml > " + self.mameinfo_xml
        if self.options['debug']:
            sys.stderr.write("DEBUG: %s\n" % command)
        proc = subprocess.Popen(command, shell=True)
        proc.wait()
        print("Create mameinfo file in: " + self.mameinfo_xml)


    def parse_args(self):
        options, args = getopt.getopt(sys.argv[1:], "hcsawdv", \
                ["help", "config", "scan_roms", "admin_mode", "windowed", "debug", "version"])

        self.options = {}
        self.options['config'] = False
        self.options['scan_roms'] = False
        self.options['admin_mode'] = False
        self.options['windowed'] = False
        self.options['debug'] = True
        self.options['run'] = True
        self.options['shutdown_on_exit'] = False

        if options:
            for option, value in options:
                if (option == "-h") or (option == "--help") :
                    print(sys.argv[0] + " is a minimal frontend for MAME. It is especial for arcade machine installation.")
                    print(" -h, --help to show the help")
                    print(" -s, --scan_roms to rescan the roms directories for new roms or changes in this")
                    #print(" -c, --config to execute the frontend in configuration mode")
                    #print(" -a, --admin_mode set the admin mode to run the frontend")
                    print(" -w, --windowed start in window mode")
                    print(" -d, --debug set the frontend to work with hight verbose")
                    print(" -v, --version show the actual version of " + sys.argv[0])

                    self.options['run'] = False

                    break
                elif (option == "-v") or (option == "--version"):
                    print(sys.argv[0] + " v0.20110826")
                    print("Copyright © 2011 Miguel de Dios.")
                    print("License GPLv3+: GNU GPL versión 3 or higher <http://gnu.org/licenses/gpl.html>.")

                    self.options['run'] = False

                    break
                elif (option == "-c") or (option == "--config"):
                    self.options['config'] = True
                    break
                elif (option == "-s") or (option == "--scan_roms"):
                    self.options['scan_roms'] = True
                    break
                elif (option == "-a") or (option == '--admin_mode'):
                    self.options['admin_mode'] = True
                elif (option == "-w") or (option == '--windowed'):
                    self.options['windowed'] = True
                elif (option == "-d") or (option == '--debug'):
                    self.options['debug'] = True


    def scan_roms_thread(self):
        a = time.time()
        command = self.options["mame_executable"] + " " + self.options["mame_options"]
        command += ' -verifyroms  | grep "^romset" |'
        command += ' sed "s/romset //" | sed "s/\[.*\] //" |'
        command += ' sed "s/ is good/|good/" | sed "s/ is bad/|bad/" | sed "s/ is best available/|best/"'

        if self.options['debug']:
            sys.stderr.write("\nDEBUG: %s\n" % command)

        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

        output = proc.communicate()[0]
        output_lines = output.split("\n")

        if self.options['debug']:
            sys.stderr.write("DEBUG: SHOW THE ALL LOG OF MAME (WITH THE BAD AND GOOD) IN THE SCAN\n")
            #command = self.options["mame_executable"] + " " + self.options["mame_options"]
            #command +=  " -verifyroms"

            #proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

            #output = proc.communicate()[0]

            sys.stderr.write("DEBUG:\n%s\n" % output)
            b = time.time()
            sys.stderr.write("Taked %s seconds to get the middle-list\n" % str(int(b - a)))

        self.scan_roms = []

        for line in output_lines:
            if line:
                chunks = line.split('|')
                romname = chunks[0]
                status = chunks[1]

                command = self.options["mame_executable"] + " " + self.options["mame_options"]
                command += " -listfull " + romname + " 2>/dev/null |"
                command += " grep " + romname + " | sed 's/[^ ]*[ ]*\\\"\\(.*\\)\\\"/\\1/'"

                if self.options['debug']:
                    sys.stderr.write("DEBUG: %s\n" % command)

                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

                name = proc.communicate()[0].replace("\n", '')

                self.scan_roms.append({"rom": romname, "name": name, "status": status})

        if self.options['debug']:
            c = time.time()
            sys.stderr.write("DEBUG: taked %s seconds to get the final-list" % (str(int(c - b))))
        return 1

    def scan_roms(self):
        connection = sqlite3.connect(self.frontend_db)
        cursor = connection.cursor()

        sys.stdout.write("Scan roms in progress, please wait.")
        sys.stdout.flush()

        t = threading.Thread(target=self.scan_roms_thread)
        t.start()

        while t.isAlive():
            time.sleep(1)
            sys.stdout.write(".")
            sys.stdout.flush()
        t.join()

        print("")

        print("Found %i roms" % len(self.scan_roms))

        sys.stdout.write("Save list roms in DB, please wait.")
        sys.stdout.flush()

        cursor.execute("SELECT COUNT(*) FROM roms;")
        result = cursor.fetchall()
        roms_db = result[0][0]
        new_roms = 0
        bad_roms = 0

        cursor.execute("UPDATE roms SET found = 0, status='';") #Mark as not found all roms and clear status field
        connection.commit()

        for item_rom in self.scan_roms:
            sys.stdout.write(".")
            sys.stdout.flush()

            cursor.execute("SELECT id FROM roms WHERE rom = '%s'" % item_rom["rom"])
            result = cursor.fetchall()
            if not result:
                disable = 0
                if item_rom["status"] == 'bad':
                    bad_roms += 1
                    disable = 1

                cursor.execute("INSERT INTO roms(rom, name, status, disabled, found, custom_options, times_executed) " + \
                        " VALUES(\"%s\", \"%s\", \"%s\", %i, 1, '', 0);" % \
                        (item_rom["rom"], item_rom["name"], item_rom['status'], disable)) #added times_executed field and 0 to its valour
                new_roms += 1
            else:
                cursor.execute("UPDATE roms SET found = 1 , status = '%s' WHERE rom = '%s'" %(item_rom["status"], item_rom["rom"])) #actualizado el status
                roms_db -= 1

        connection.commit()

        print("")
        print("New roms added: %i" % new_roms)
        print("New roms deleted: %i" % roms_db)
        print("Bad roms: %i" % bad_roms)

        new_info = 0

        if self.options["view_mode"] == 3:
            print("Getting MAME info...")
            sys.stdout.write(" Please Wait.")
            sys.stdout.flush()

            #games - from wah!cade
            for event, game in ET.iterparse(self.mameinfo_xml):
                #for each game
                if game.tag == 'game':
                    info = {'name': '',
                                    'year': '',
                                    'display-type': '',
                                    'display-screen': -1,
                                    'driver': '',
                                    'manufacturer': '',
                                    'input-players': -1,
                                    'input-control': '',
                                    'input-buttons': -1 }

                    info['name'] = game.attrib['name']
                    info['year'] = game.findtext('year') or ''
                    info['manufacturer'] = game.findtext('manufacturer') or ''
                    # driver = game.find('driver')

                    display = game.find('display')
                    if display is not None:
                        info['display-type'] = display.attrib['type'].title()
                        info['display-screen'] = display.attrib['rotate']

                    input_tag = game.find('input')
                    if input_tag is not None:
                        for at in input_tag.items():
                            if at[0] == 'players':
                                info['input-players'] = at[1]
                            if at[0] == 'buttons':
                                info['input-buttons'] = at[1]
                        control = input_tag.find('control')
                        if control is not None:
                            if 'type' in control.keys():
                                info['input-control'] = control.attrib['type']

                    cursor.execute("SELECT rom, id FROM roms WHERE rom = '" + info['name'] +"';")
                    roms = cursor.fetchall()
                    for rom in roms:
                        sql = "INSERT OR REPLACE INTO rom_info(id, year, manufacturer, display_type, display_screen, input_players, input_control, input_buttons) " + \
                                " VALUES(%s, \"%s\", \"%s\", \"%s\", %s, %s, \"%s\", %s);" % \
                                (str(rom[1]), info['year'], info['manufacturer'], info['display-type'], info['display-screen'], \
                                info['input-players'], info['input-control'], info['input-buttons'])
                        # print sql
                        cursor.execute(sql)
                        new_info += 1
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        break

            print("")
            connection.commit() # save changes on db

        print(" New total roms info added/replaced: %i" % new_info)
        print("")


    def update_db(self):
        connection = sqlite3.connect(self.frontend_db)
        cursor = connection.cursor()

        cursor.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'roms';")
        result = cursor.fetchall()
        sql = result[0][0]
        if sql.find('disabled') == -1:
            cursor.execute("ALTER TABLE roms ADD COLUMN disabled INTEGER;")
            connection.commit()
            cursor.execute("UPDATE roms SET disabled = 0;")
            connection.commit()
            print("Update the table add 'disabled' field.")

        cursor.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'roms';")
        result = cursor.fetchall()
        sql = result[0][0]
        if sql.find('found') == -1:
            cursor.execute("ALTER TABLE roms ADD COLUMN found INTEGER;")
            connection.commit()
            cursor.execute("UPDATE roms SET found = 1;")
            connection.commit()
            print("Update the table add 'found' field.")


        if sql.find('status') == -1:
            cursor.execute("ALTER TABLE roms ADD COLUMN status TEXT;")
            connection.commit()
            cursor.execute("UPDATE roms SET status = '';")
            connection.commit()
            print("Update the table add 'status' field.")

        if sql.find('custom_options') == -1:
            cursor.execute("ALTER TABLE roms ADD COLUMN custom_options TEXT;")
            connection.commit()
            cursor.execute("UPDATE roms SET custom_options = '';")
            connection.commit()
            print("Update the table add 'custom_options' field.")

        if sql.find('times_executed') == -1:
            cursor.execute("ALTER TABLE roms ADD COLUMN times_executed INTEGER not null default 0;")
            connection.commit()
            cursor.execute("UPDATE roms SET times_executed = 0;")
            connection.commit()
            print("Update the table add 'times_executed' field.")

        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'save_data'")
        result = cursor.fetchall()
        if not result:
            cursor.execute("CREATE TABLE save_data(" + \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " + \
                    #The token name.
                    "token TEXT, " + \
                    #The value with name token.
                    "value TEXT, " + \
                    #The type of value.
                    "type TEXT" + \
                    ");")
            connection.commit()
            print("Create the table save_data.")

        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'rom_info'")
        result = cursor.fetchall()
        if not result:
            cursor.execute("CREATE TABLE rom_info(" + \
                    #ROM internal id
                    "id INTEGER PRIMARY KEY, " + \
                    #Game year in text (some strings are: 197?)
                    "year TEXT, " + \
                    "manufacturer TEXT, " + \
                    "display_type TEXT, " + \
                    "display_screen INTEGER, " + \
                    "input_players INTEGER, " + \
                    "input_control TEXT, " + \
                    "input_buttons INTEGER " + \
                    ");")
            connection.commit()
            print("Create the table rom_info.")


    def create_db(self):
        print("Create the DB.")

        create_table = False
        if not os.path.exists(self.frontend_db):
            create_table = True

        connection = sqlite3.connect(self.frontend_db)
        cursor = connection.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'roms'")
        result = cursor.fetchall()
        if not result:
            create_table = True

        if create_table:
            cursor.execute("CREATE TABLE roms(" + \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " + \
                    #ROM name
                    "rom TEXT, " + \
                    #Game name
                    "name TEXT, " + \
                    #For to hide games in the list
                    "disabled INTEGER, " + \
                    #For to mark and hide games that disappear when rescan the roms
                    "found INTEGER, " + \
                    #For to status of the rom
                    "status TEXT, " + \
                    #For to add custom option to mame execution
                    "custom_options TEXT, " + \
                    #For to count the times executed the game
                    "times_executed INTEGER not null default 0" + \
                    ");")
            connection.commit()
            print("Create the table roms.")

        create_table = False # reset flag
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'save_data'")
        result = cursor.fetchall()
        if not result:
            create_table = True

        if create_table:
            cursor.execute("CREATE TABLE save_data(" + \
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, " + \
                    #The token name.
                    "token TEXT, " + \
                    #The value with name token.
                    "value TEXT, " + \
                    #The type of value.
                    "type TEXT" + \
                    ");")
            connection.commit()
            print("Create the table save_data.")

        create_table = False # reset flag
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'rom_info'")
        result = cursor.fetchall()
        if not result:
            create_table = True

        if create_table:
            cursor.execute("CREATE TABLE rom_info(" + \
                    #ROM internal id
                    "id INTEGER PRIMARY KEY, " + \
                    #Game year in text (some strings are: 197?)
                    "year TEXT, " + \
                    "manufacturer TEXT, " + \
                    "display_type TEXT, " + \
                    "display_screen INTEGER, " + \
                    "input_players INTEGER, " + \
                    "input_control TEXT, " + \
                    "input_buttons INTEGER " + \
                    ");")
            connection.commit()
            print("Create the table rom_info.")

    def parse_config_file(self):
        cfg = ConfigParser.ConfigParser()
        cfg.read(self.file_config)

        self.options["mame_executable"] = cfg.get("pyRetro", "mame_executable")
        self.options["mame_options"] = cfg.get("pyRetro", "mame_options")
        self.options["view_mode"] = int(cfg.get("pyRetro", "view_mode"))
        self.options["screen_width"] = int(cfg.get("pyRetro", "screen_width"))
        self.options["screen_height"] = int(cfg.get("pyRetro", "screen_height"))
        self.options["default_background"] = self.handle_relative_path(cfg.get("pyRetro", "default_background"))
        self.options["time_to_show_screensaver"] = int(cfg.get("pyRetro", "time_to_show_screensaver"))
        self.options["seconds_wait_between_screensaver_images"] = int(cfg.get("pyRetro", "seconds_wait_between_screensaver_images"))
        self.options["can_played_game_show_in_screensaver"] = int(cfg.get("pyRetro", "can_played_game_show_in_screensaver"))
        self.options["dir_default_images_screensaver"] = self.handle_relative_path(cfg.get("pyRetro", "dir_default_images_screensaver"))
        self.options["dir_default_game_video"] = self.handle_relative_path(cfg.get("pyRetro", "dir_default_game_video"))
        self.options["seconds_wait_video"] = int(cfg.get("pyRetro", "seconds_wait_video"))
        self.options["random_percent_default_images_screensaver"] = int(cfg.get("pyRetro", "random_percent_default_images_screensaver"))
        self.options["transational_effect_screensaver"] = int(cfg.get("pyRetro", "transational_effect_screensaver"))
        self.options['shutdown_on_exit'] = int(cfg.get("pyRetro", "shutdown_on_exit"))
        self.options['shutdown_command'] = cfg.get("pyRetro","shutdown_command")
        self.options['filter'] = int(cfg.get("pyRetro","filter"))
        self.options['filter_game_buttons'] = int(cfg.get("pyRetro","filter_game_buttons"))

    def handle_relative_path(self, p):
        if p.startswith(os.path.sep):
            return p
        else:
            return os.path.join(os.path.dirname(__file__),p)

    def save_config_file(self, last_rom_selected):
        cfg = ConfigParser.ConfigParser()
        cfg.read(self.file_config)
        cfg.set("pyRetro", "internal_selected_rom", last_rom_selected)
        filep = open(self.file_config, 'w')
        cfg.write(filep)


    def get_mame_confs(self):
        command = "mame -showconfig | grep snapshot_directory | sed 's/snapshot_directory[ ]*\\([^ ]*\\)/\\1/'"
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        self.options["snapshots_directory"] = proc.communicate()[0].replace("\n", '') # = proc.communicate()[0] [: -1]
        self.options["snapshots_directory"] = self.options["snapshots_directory"].replace("$HOME", os.path.expanduser('~'))


    def db_fail(self):
        if not os.path.exists(self.frontend_db):
            return True

        connection = sqlite3.connect(self.frontend_db)
        cursor = connection.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'roms'")
        result = cursor.fetchall()
        if not result:
            return True

        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'save_data'")
        result = cursor.fetchall()
        if not result:
            return True

        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'rom_info'")
        result = cursor.fetchall()
        if not result:
            return True

        cursor.execute("SELECT COUNT(*) FROM roms;")
        result = cursor.fetchall()

        if result[0][0] == 0:
            return True

        cursor.execute("SELECT COUNT(*) FROM rom_info;")
        result = cursor.fetchall()

        if result[0][0] == 0 and self.options["view_mode"] == 3:
            print("Current roms in Layout mode != Rom Information, rescan need it")
            print("")
            return True

        return False
