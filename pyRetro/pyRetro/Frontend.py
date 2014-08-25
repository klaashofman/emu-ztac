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
import pygame
from pygame.locals import *
import sqlite3
import subprocess
import random
import string
from pprint import *

from Util import *
from ListFullScreen_mode import *
from ListWeird_mode import *
from ListPanelScreen_mode import *




class Frontend:
    framesPerSecond = 60
    clock = None
    last_time_screensaver = 0
    disable_screensaver = False
    list_roms = None
    debug = False
    admin_mode = False
    util = None
    list_modes = ["normal","favorities"]
    current_mode = 0

    def __init__(self, config_mode = False, util_param = None):
        self.util = util_param
        self.clock = pygame.time.Clock()
        self.last_time_screensaver = pygame.time.get_ticks()
        self.load_current_mode()
        if config_mode:
            self.config_mode()
        else:
            self.normal_mode()

    def config_mode(self):
        return

    def normal_mode(self):
        width = self.util.options["screen_width"]
        height = self.util.options["screen_height"]
        if self.util.options['filter']:
            self.list_roms = self.get_all_roms()
        else:
            self.list_roms = self.get_roms_with_buttons(self.util.options['filter_game_buttons'])

        if not self.list_roms:
            print("Empty list roms, please check the DB.")
            return

        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption('pyRetro: Init')
        #TODO: little hacky but pygame-movie requires it here if you want sound (do not work in ListPanelScreen_mode.py)
        #      maybe we should init just joy/screen on pygame.init and remove this shit :?
        pygame.mixer.quit()

        if self.util.options['windowed'] == False:
            screen_vars = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        else:
            screen_vars = 0

        self.screen = pygame.display.set_mode((width, height), screen_vars, 32) # force 32bit mode (for smooth scale)


        if self.util.options["view_mode"] == 1:
            pygame.display.set_caption('pyRetro: Snapshop Fullscreen mode')
            mode = ListFullScreen_mode(self.util, self)
            mode.run()
        elif self.util.options["view_mode"] == 2:
            print("No Grid-mode yet! Quit...")
        elif self.util.options["view_mode"] == 3:
            pygame.display.set_caption('pyRetro: Layout mode')
            mode = ListPanelScreen_mode(self.util, self)
            mode.run()
        elif self.util.options["view_mode"] == 4:
            pygame.display.set_caption('pyRetro: Snapshop Weird mode')
            mode = ListWeird_mode(self.util, self)
            mode.run()

        pygame.mixer.init() #TODO: little hacky but pygame-movie requires it here (do not work in ListPanelScreen_mode.py)
        pygame.quit()


    def execute_rom(self, select_rom):
        self.set_screensaver(False)

        #clear screen
        self.screen.fill((0, 0, 0))
        pygame.display.update()

        connection = sqlite3.connect(self.util.frontend_db)
        cursor = connection.cursor()
        cursor.execute("UPDATE roms SET times_executed = times_executed + 1 WHERE id = %i;" % self.list_roms[select_rom][4])
        connection.commit()

        pygame.display.toggle_fullscreen()

        command = self.util.options["mame_executable"] + " " + self.util.options["mame_options"] + " " + self.list_roms[select_rom][2]
        command += " " + self.list_roms[select_rom][0]
        proc = subprocess.Popen(command, shell=True)
        proc.wait()

        pygame.display.toggle_fullscreen()
        self.set_screensaver(True)


    def translate_idrom_to_arraykey(self, idrom):
        return_var = None

        iterator = 0
        for rom in self.list_roms:
            if rom[4] == idrom:
                return_var = iterator
                break

            iterator += 1


        return return_var

    def waitFrame(self):
        self.clock.tick(self.framesPerSecond)

    def set_screensaver(self, enable = True):
        if enable:
            self.disable_screensaver = False
            self.last_time_screensaver = pygame.time.get_ticks()
        else:
            self.disable_screensaver = True

    def screen_saver(self):
        return_var = None

        if pygame.event.peek(KEYDOWN):
            self.set_screensaver(False)
        elif self.disable_screensaver == True:
            #If before is disabled reset the timer of screensaver
            self.set_screensaver(True)

        if not self.disable_screensaver:
            if self.last_time_screensaver + 1000 * self.util.options['time_to_show_screensaver'] <= pygame.time.get_ticks():
                return_var = self.run_screen_saver()

        return return_var


    def screen_saver_transition_normal(self, new_image = None, last_image = None):
        """Blit the image centered on screen"""
        pos_y = (self.util.options["screen_height"] - new_image.get_height()) / 2
        pos_x = (self.util.options["screen_width"] - new_image.get_width()) / 2
        self.screen.blit(new_image, (pos_x, pos_y))


    def run_screen_saver(self):
        connection = sqlite3.connect(self.util.frontend_db)
        cursor = connection.cursor()

        exit_var = False
        return_var = False

        last_image = None
        new_image = None
        screenshot_roms_showed = []
        rom_is_showing = False

        default_images = os.listdir(self.util.options['dir_default_images_screensaver'])
        copy_default_images = default_images[:]
        random.shuffle(copy_default_images)
        no_default_images = False
        if (len(default_images) == 0):
            no_default_images = True

        time_last_image = pygame.time.get_ticks()

        while not exit_var:
            if time_last_image + 1000 * self.util.options['seconds_wait_between_screensaver_images'] <= pygame.time.get_ticks():
                time_last_image = pygame.time.get_ticks()
                new_image = None
                rom_is_showing = False

                if not no_default_images:
                    if random.randint(0, 100) <= self.util.options['random_percent_default_images_screensaver']:
                        default_image = copy_default_images.pop()
                        if len(copy_default_images) == 0:
                            copy_default_images = default_images[:]
                            random.shuffle(copy_default_images)

                        file_str = os.path.join(self.util.options['dir_default_images_screensaver'], default_image)
                        try:
                            new_image = pygame.image.load(file_str).convert()
                        except pygame.error, message:
                            pass #Can't load the image
                        else:
                            new_image = self.resize_to_screen(new_image)

                if not new_image:
                    id_list = ''
                    while len(screenshot_roms_showed) < len(self.list_roms):
                        cursor.execute("SELECT id, rom " + \
                                "FROM roms " + \
                                "WHERE disabled = 0 AND found = 1 AND id NOT IN (" + id_list + ") " + \
                                "ORDER BY times_executed ASC, random() LIMIT 1;")
                        row = cursor.fetchall()[0]
                        id_rom = row[0]
                        rom_name = row[1]

                        #Try to load image
                        dir_rom = os.path.join(self.util.options["snapshots_directory"], rom_name)
                        if os.path.exists(dir_rom):
                            snaps = os.listdir(dir_rom)
                            if (len(snaps) > 0):
                                try:
                                    new_image = pygame.image.load(os.path.join(dir_rom, snaps[0])).convert()
                                except pygame.error, message:
                                    pass #Can load the image
                                else:
                                    new_image = self.resize_to_screen(new_image)
                                    rom_is_showing = True

                        screenshot_roms_showed.append(id_rom)

                        if len(screenshot_roms_showed) >= len(self.list_roms):
                            #Clean the list of roms "showed"
                            screenshot_roms_showed = [id_rom]

                        break

                        #IMPLODE IN PYTHON
                        id_list = ','.join(map( str, screenshot_roms_showed ))

                if not new_image:
                    #Load default image
                    new_image = pygame.Surface((self.util.options["screen_width"], self.util.options["screen_height"]))
                    new_image.fill((0, 0, 0))

                self.screen.fill((0, 0, 0))

                if self.util.options['transational_effect_screensaver'] == 0:
                    self.screen_saver_transition_normal(new_image, last_image)
                else:
                    #TODO MAKE OTHER EFECTS BETWEEN IMAGES
                    #self.effect(last_image, new_image)
                    pass

                last_image = new_image


            self.waitFrame()
            pygame.display.update()

            if pygame.event.peek((KEYDOWN, QUIT)):
                if rom_is_showing and self.util.options['can_played_game_show_in_screensaver'] == 1:
                    return_var = id_rom

                exit_var = True
                self.disable_screensaver = True

        return return_var

    def get_resize_with_aspect(self, org_size, max_size):
        width, height = org_size
        max_width, max_height = max_size

        img_scale_x = float(max_width) / float(width)
        img_scale_y = float(max_height) / float(height)
        #scale to width or height - from wah!cade
        if (height) * img_scale_x > max_height:
            #scale to height
            new_width = int(float(width) * img_scale_y)
            new_height = int(float(height) * img_scale_y)
        else:
            #scale to width - from wah!cade
            new_width = int(float(width) * img_scale_x)
            new_height = int(float(height) * img_scale_x)

        return new_width, new_height

    def resize_to_screen(self, image):
        new_width, new_height = self.get_resize_with_aspect(image.get_size(), (self.util.options["screen_width"], self.util.options["screen_height"]))
        return_image = pygame.transform.smoothscale(image, (new_width, new_height))
        return return_image

    def resize_with_aspect(self, image, max_width, max_height):
        new_width, new_height = self.get_resize_with_aspect(image.get_size(), (max_width, max_height))
        return_image = pygame.transform.smoothscale(image, (new_width, new_height))
        return return_image

    def get_all_roms(self):
        connection = sqlite3.connect(self.util.frontend_db)
        cursor = connection.cursor()
        cursor.execute("SELECT rom, name, custom_options, status, roms.id, year, manufacturer, display_type, display_screen, input_players, input_control, input_buttons \
                                                FROM roms LEFT JOIN rom_info \
                                                ON roms.id = rom_info.id WHERE disabled = 0 AND found = 1 ORDER BY name ASC;")
        return cursor.fetchall()

    def add_to_favorities(self, select_rom):
        """Adds a rom to favorities"""
        token = "favorities"
        rom_id = self.list_roms[select_rom][4] # ID
        s = self.util.load_value_db(token)
        l = s.split(',')
        if s:
            try:
                l.index(str(rom_id))
            except ValueError:
                s += ","+str(rom_id)
        else:
            s = str(rom_id)
        self.util.save_value_db(token,s)

    def remove_from_favorities(self, select_rom):
        """Delete a rom from favorities"""
        token = "favorities"
        rom_id = self.list_roms[select_rom][4] # ID
        s = self.util.load_value_db(token)
        if s:
            l = s.split(",")
            del l[l.index(str(rom_id))]
            self.util.save_value_db(token,string.join(l,","))
            self.list_roms = self.get_favorite_roms()

    def get_favorite_roms(self):
        """Load the list of favorite roms"""
        token = "favorities"
        s = self.util.load_value_db(token)
        if s:
            connection = sqlite3.connect(self.util.frontend_db)
            cursor = connection.cursor()
            sql = "SELECT rom, name, custom_options, status, roms.id, year, manufacturer, "
            sql += "display_type, display_screen, input_players, input_control, input_buttons "
            sql += "FROM roms LEFT JOIN rom_info ON roms.id = rom_info.id WHERE roms.id IN "
            sql += "("+s+") AND disabled = 0 AND found = 1 ORDER BY name ASC;"

            cursor.execute(sql)
            return cursor.fetchall()
        else: return [["","EMPTY ROM LIST","","","","","","","","",0,0]]

    def toggle_fav(self, select_rom):
        """Add/remove from favorities"""
        if self.list_modes[self.current_mode] == "favorities":
            if self.show_dialog("Are you sure you want to remove from favorities?"):
                self.remove_from_favorities(select_rom)
        elif self.list_modes[self.current_mode] == "normal":
            if self.show_dialog("Do you want to add to favorities?"):
                self.add_to_favorities(select_rom)

    def switch_mode(self, select_rom):
        """Toggle list mode between favorities and normal
        return modified select_rom"""
        self.current_mode = (self.current_mode + 1) % len(self.list_modes)
        if self.list_modes[self.current_mode] == "favorities":
            self.list_roms = self.get_favorite_roms()
            if len(self.list_roms)>0:
                select_rom %= len(self.list_roms)
        elif self.list_modes[self.current_mode] == "normal":
            if self.util.options['filter']:
                self.list_roms = self.get_all_roms()
            else:
                self.list_roms = self.get_roms_with_buttons(self.util.options['filter_game_buttons'])
            select_rom %= len(self.list_roms)
        return select_rom

    def load_current_mode(self):
        """It's to be called one time only"""
        m = self.util.load_value_db("current_mode")
        if m:
            self.current_mode = int(m)
        if self.list_modes[self.current_mode] == "favorities":
            self.list_roms = self.get_favorite_roms()

    def save_current_mode(self):
        self.util.save_value_db("current_mode", self.current_mode)

    def get_roms_with_buttons(self, buttons):
        """Load the list of roms having n. of buttons < buttons param"""
        connection = sqlite3.connect(self.util.frontend_db)
        cursor = connection.cursor()
        cursor.execute("SELECT rom, name, custom_options, status, roms.id, year, manufacturer, display_type, display_screen, input_players, input_control, input_buttons \
                                                FROM roms LEFT JOIN rom_info \
                                                ON roms.id = rom_info.id WHERE disabled = 0 AND found = 1 AND (input_buttons between 0 and " + str(buttons)+ " OR input_buttons = -1) ORDER BY name ASC;")
        return cursor.fetchall()

    def show_dialog(self, question):
        """
        Display a question dialog
        returns True = Yes and False = No
        """
        fontname = "Arial"

        WIDTH = 400
        HEIGHT = 200
        # TODO: optimize a lot the whole thing
        # Prepare the dialog surface
        color = (255, 255, 0)
        surface = pygame.Surface((WIDTH, HEIGHT))
        myFont = pygame.font.SysFont(fontname, 15)

        message_surface =  myFont.render(question, True, color)
        message_surface.set_alpha(128)
        yes_surface = myFont.render("Yes", True, color)
        no_surface = myFont.render("No", True, color)
        selector_surfaces = [myFont.render("<<", True, color),myFont.render(">>", True, color)]
        selector_erasers = [pygame.Surface((selector_surfaces[0].get_width(), selector_surfaces[0].get_height())),
                            pygame.Surface((selector_surfaces[1].get_width(), selector_surfaces[1].get_height()))]

        message_position = ((WIDTH - message_surface.get_width()) / 2,
            (HEIGHT - message_surface.get_height()) /2 - 15)
        yes_position = (message_position[0],HEIGHT - yes_surface.get_height() - 50)
        no_position = (message_position[0] + message_surface.get_width() - no_surface.get_width(), HEIGHT - no_surface.get_height() - 50)
        selector_positions = [(yes_position[0]+yes_surface.get_width(),yes_position[1]),
            (no_position[0] - no_surface.get_width(),no_position[1])]
        selector_position = selector_positions[0]

        surface.blit(message_surface,message_position)
        surface.blit(yes_surface, yes_position)
        surface.blit(no_surface, no_position)
        pos, pos_rev = 1, 0 # default in "no" selected
        exit_var = False
        dialog_centered = ((self.screen.get_width()-WIDTH) / 2, (self.screen.get_height() - HEIGHT) / 2)
        while not exit_var:
            now = pygame.time.get_ticks()
            # Event dispatcher
            for e in pygame.event.get():
                if e.type == pygl.KEYDOWN:
                    if e.key == pygl.K_LEFT:
                        pos, pos_rev = 0, 1
                    elif e.key == pygl.K_RIGHT:
                        pos, pos_rev = 1, 0
                    elif e.key == pygl.K_RETURN or e.key == pygl.K_LCTRL:
                        return bool(pos_rev)
            # draw the dialog
            pygame.draw.rect(surface, (255,255,255), pygame.Rect(0,0,WIDTH,HEIGHT), 1)
            surface.blit(selector_erasers[pos_rev], selector_positions[pos_rev])
            surface.blit(selector_surfaces[pos], selector_positions[pos])
            self.screen.blit(surface, dialog_centered)
            pygame.display.update()
