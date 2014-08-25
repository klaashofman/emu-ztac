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

import Util
import Frontend
import math
import os
import pprint
import getpass
import pygame
import pygame.locals as pygl


class ListWeird_mode:
    font_size = 28
    font_size_big = 30
    antialias = True
    fontname = 'Arial'
    margin_between_roms = font_size / 2 #10
    vertical_distance_between_roms = font_size + margin_between_roms

    def __init__(self, util_param=None, frontend_param=None):
        self.util = util_param
        self.background = None
        self.frontend = frontend_param
        self.create_default_background()

    def create_default_background(self):
        self.default_background = pygame.Surface((self.util.options["screen_width"], self.util.options["screen_height"]))
        self.default_background.fill((0, 0, 0))

        temp = pygame.image.load(self.util.options["default_background"]).convert()
        width = temp.get_width()
        height = temp.get_height()

        dif_h = float(self.util.options["screen_height"]) / height
        dif_h = int(math.ceil(dif_h))
        dif_w = float(self.util.options["screen_width"]) / width
        dif_w = int(math.ceil(dif_w))

        if dif_h < 1:
            dif_h = 1

        if dif_w < 1:
            dif_w = 1

        #Fill all background with the mosaic of background file
        for iterator1 in range(dif_h):
            for iterator2 in range(dif_w):
                self.default_background.blit(temp,
                    (iterator2 * width, iterator1 * height))

    def check_background(self, select_rom):
        pass

    def load_background(self, select_rom):
        self.background = None
        background_dir = self.util.options["snapshots_directory"]
        # Try if exists some snapshot_dir and load some select_rom.png files
        if os.path.exists(background_dir):
            background_dir = self.util.options["snapshots_directory"] + "/"
            snap_file = background_dir + self.frontend.list_roms[select_rom][0] + ".png"
            if os.path.isfile(snap_file):
                self.background = pygame.image.load(snap_file).convert()
        if self.background:
            self.background = self.frontend.resize_with_aspect(
                self.background, 640, 480)
        else:
            self.background = self.default_background

    def paint_current_mode(self):
        myfont = pygame.font.SysFont(self.fontname, 18)
        title = "Showing %s roms (%s)" % (self.frontend.list_modes[self.frontend.current_mode].upper(), str(len(self.frontend.list_roms)))
        tempImg = myfont.render(title, self.antialias, (250, 250, 0))
        self.frontend.screen.blit(tempImg, (int((self.util.options["screen_width"] - tempImg.get_width()) / 2), 1))
        #self.frontend.screen.blit(tempImg, 100, 100)

    def paint_background(self):
        """Paint the background upright aligned"""
        screen_width = self.util.options["screen_width"]
        background_y = 0
        background_x = screen_width - self.background.get_width()

        self.frontend.screen.blit(self.background, (background_x, background_y))

    def paint_list_roms(self, list_roms, select_rom):

        screen_width = self.util.options["screen_width"]
        screen_height = self.util.options["screen_height"]

        count_roms = len(list_roms)

        middle_y_pos = (screen_height - self.font_size) / 2

        arialFont = pygame.font.SysFont(self.fontname, self.font_size)
        arialFont_bold = pygame.font.SysFont(self.fontname, self.font_size_big, bold = True)
        dataFont = pygame.font.SysFont(self.fontname, 24)
        #TODO
        ordened_list_roms = list_roms[select_rom:] + list_roms[:select_rom]

        count_roms_show_middle_screen = middle_y_pos / self.vertical_distance_between_roms

        if count_roms_show_middle_screen > count_roms / 2:
            list_roms_middle_to_bottom = ordened_list_roms[:count_roms / 2]
            list_roms_middle_to_top = ordened_list_roms[count_roms / 2:]
        else:
            list_roms_middle_to_bottom = ordened_list_roms[:count_roms_show_middle_screen]
            list_roms_middle_to_top = ordened_list_roms[-count_roms_show_middle_screen:]

        list_roms_middle_to_top.reverse()
        # Draws Year and manufacturer, if present

        if list_roms[select_rom][6]:
            manuImage = dataFont.render(list_roms[select_rom][6],self.antialias,(250, 255, 0))
            self.frontend.screen.blit(manuImage, (screen_width-manuImage.get_width(), screen_height-manuImage.get_height()))
        if list_roms[select_rom][5]:
            yearImage = dataFont.render(list_roms[select_rom][5],self.antialias,(250, 250, 0))
            self.frontend.screen.blit(yearImage, (screen_width-yearImage.get_width(),screen_height-manuImage.get_height()-yearImage.get_height()))

        y = middle_y_pos
        first = True
        for rom in list_roms_middle_to_bottom:

            if first:
                x = 20
                color = (0, 255, 0)
                tempImage =  arialFont_bold.render(rom[1], self.antialias, color)
                tempImage.set_alpha(255)
            else:
                x = 20
                color = (255, 255, 0)
                tempImage =  arialFont.render(rom[1], self.antialias, color)
                tempImage.set_alpha(128)
            tempImage.convert_alpha()
            #tempImage.set_alpha(255 * 0.75)
            self.frontend.screen.blit(tempImage, (x, y))
            y += self.vertical_distance_between_roms

            first = False

        y = middle_y_pos - self.vertical_distance_between_roms
        for rom in list_roms_middle_to_top:
            x = 20
            color = (255, 255, 0)
            tempImage = arialFont.render(rom[1], self.antialias, color)
            tempImage.set_alpha(128)
            tempImage.convert_alpha()
            #tempImage.set_alpha(255 * 0.75)
            self.frontend.screen.blit(tempImage, (x, y))
            y -= self.vertical_distance_between_roms

    def check_limits_select_rom(self, select_rom):
        if -(select_rom) == len(self.frontend.list_roms):
            select_rom = 0
        if select_rom == len(self.frontend.list_roms):
            select_rom = 0
        return select_rom


    def run(self):
        global select_rom, sleep_when_pressed_same_key, last_pressed_key, last_time_move, exit_var
        select_rom = 0
        exit_var = False

        last_pressed_key = None
        last_rom = None
        last_time_move = 0
        sleep_when_pressed_same_key = 800
        change_direction = False

        def key_pressed():
            global last_pressed_key
            g = dispatch_keys.get(e.key)
            if g is not None:
                g()
            last_pressed_key = e.key

        def key_up():
            global last_pressed_key
            last_pressed_key = None
            last_time_sleep = now

        def up():
            global select_rom, sleep_when_pressed_same_key, last_pressed_key, last_time_move
            select_rom -= 1
            sleep_when_pressed_same_key = 800
            last_time_move = now
            change_direction = True

        def down():
            global select_rom, sleep_when_pressed_same_key, last_pressed_key, last_time_move
            select_rom += 1
            sleep_when_pressed_same_key = 800
            last_time_move = now
            change_direction = True

        def right():
            """Move by letter forward"""
            global select_rom, sleep_when_pressed_same_key, last_pressed_key, last_time_move
            letter = self.frontend.list_roms[select_rom][1][0].upper() if self.frontend.list_roms[select_rom][1] else self.frontend.list_roms[select_rom][0][0].upper()
            cap = len(self.frontend.list_roms)
            while (self.frontend.list_roms[select_rom][1][0].upper() if self.frontend.list_roms[select_rom][1] else self.frontend.list_roms[select_rom][0][0].upper()) == letter :
                select_rom += 1
                select_rom %= cap
            sleep_when_pressed_same_key = 800
            last_time_move = now
            change_direction = True

        def left():
            """Move by letter reverse"""
            global select_rom, sleep_when_pressed_same_key, last_pressed_key, last_time_move
            letter = self.frontend.list_roms[select_rom][1][0].upper() if self.frontend.list_roms[select_rom][1] else self.frontend.list_roms[select_rom][0][0].upper()
            cap = len(self.frontend.list_roms)
            while (self.frontend.list_roms[select_rom][1][0].upper() if self.frontend.list_roms[select_rom][1] else self.frontend.list_roms[select_rom][0][0].upper()) == letter :
                select_rom -= 1
                select_rom %= cap
            sleep_when_pressed_same_key = 800
            last_time_move = now
            change_direction = True

        def switch_mode():
            """Toggle list mode between favorities and normal"""
            global select_rom
            select_rom = self.frontend.switch_mode(select_rom)

        def toggle_fav():
            global select_rom
            print self.frontend.list_roms[select_rom][4], select_rom
            self.frontend.toggle_fav(select_rom)

        def start_rom():
            if (id_rom_screensaver is None) or (id_rom_screensaver == False):
                self.frontend.execute_rom(select_rom)

        def exit_fe():
            """Exits the frontend"""
            global exit_var
            exit_var = True

        # Dictionaries for event dispatchers
        dispatch = { pygl.QUIT : exit_fe, pygl.KEYDOWN : key_pressed , pygl.KEYUP : key_up }

        dispatch_keys = { pygl.K_ESCAPE: exit_fe, pygl.K_UP: up, pygl.K_DOWN: down,
                         pygl.K_LEFT: left, pygl.K_RIGHT: right, pygl.K_1: start_rom,
                         pygl.K_RETURN: start_rom, pygl.K_SPACE: switch_mode,
                         pygl.K_c : toggle_fav, pygl.K_LALT : toggle_fav, pygl.K_2 : exit_fe }

        while not exit_var:
            now = pygame.time.get_ticks()

            if last_pressed_key is None:
                id_rom_screensaver = self.frontend.screen_saver()

            self.frontend.screen.fill((0, 0, 0))

            select_rom = self.check_limits_select_rom(select_rom)
            if select_rom != last_rom:
                self.load_background(select_rom)
                last_rom = select_rom
            elif self.background == self.default_background and last_pressed_key == pygl.K_RETURN:
                self.load_background(select_rom)

            self.paint_background()
            self.paint_current_mode()
            self.paint_list_roms(self.frontend.list_roms, select_rom)

            # Event dispatcher
            for e in pygame.event.get():
                f = dispatch.get(e.type)
                if f is not None:
                    f()

            if (last_pressed_key is not None) and (not change_direction):
                if (sleep_when_pressed_same_key + last_time_move) < now:
                    if last_pressed_key == pygl.K_DOWN:
                        select_rom += 1
                    elif last_pressed_key == pygl.K_UP:
                        select_rom -= 1

                    #Acelerate the movement across the list
                    if sleep_when_pressed_same_key > 50:
                        sleep_when_pressed_same_key -= 50
                    elif sleep_when_pressed_same_key > 10:
                        sleep_when_pressed_same_key -= 10

            if len(self.frontend.list_roms):
                select_rom %= len(self.frontend.list_roms)

            change_direction = False
            self.frontend.waitFrame()
            pygame.display.update()
        print "Exiting"
