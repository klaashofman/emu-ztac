__author__ = 'KH'

import os
import sys
import getopt
import subprocess
import threading
import ConfigParser
import sqlite3
import time


class Db:
    options = {}
    options['debug'] = True
    options['romdir'] ="./roms"
    frontend_db = None

    def __init__ (self):
        self.frontend_db = os.path.join(os.path.expanduser('~'), ".pyRetro", "frontend.db")
        if (self.db_fail):
            self.create_db()
            self.scan_roms()
        # else:
        #    self.update_db()

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

    def scan_roms_thread(self):
        a = time.time()
        command = 'cd ' + self.options['romdir'] + '; find .'

        if self.options['debug']:
            sys.stderr.write("\nDEBUG: %s\n" % command)

        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

        output = proc.communicate()[0]
        output_lines = output.split("\n")

        if self.options['debug']:
            sys.stderr.write("DEBUG:\n%s\n" % output)
            b = time.time()
            sys.stderr.write("Taked %s seconds to get the middle-list\n" % str(int(b - a)))

        self.scan_roms = []

        for line in output_lines:
            if line:
                name = line.strip('./')
                romname = name.replace(' ', '_')
                status = 'OK'

                if self.options['debug']:
                    sys.stderr.write("DEBUG: %s\n" % command)

                # proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

                # name = proc.communicate()[0].replace("\n", '')

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

    def db_fail(self):
        if not os.path.exists(self.frontend_db):
            return True

        connection = sqlite3.connect(self.frontend_db)
        cursor = connection.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'roms'")
        result = cursor.fetchall()
        if not result:
            return True

        return False