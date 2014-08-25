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

from Util import *
from Frontend import *
import math, os
from pprint import *

class ListFullScreen_mode:
    font_size = 30
    font_size_big = 36
    fontname = 'Arial'
    margin_between_roms = 10
    vertical_distance_between_roms = font_size + margin_between_roms

    def __init__(self, util_param = None, frontend_param = None):
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
                self.default_background.blit(temp, (iterator2 * width, iterator1 * height))


    def check_background(self, select_rom):
        pass

    def load_background(self, select_rom):
        self.background = None

        background_dir = self.util.options["snapshots_directory"]
        # Try if exists some snapshot_dir and load some select_rom.png files there
        if os.path.exists(background_dir):
            #background_dir = self.util.options["snapshots_directory"] + "/"
            snap_file = os.path.join(background_dir, self.frontend.list_roms[select_rom][0] + ".png")
            if os.path.isfile(snap_file):
                self.background = pygame.image.load(snap_file).convert()
        if self.background:
            self.background = self.frontend.resize_to_screen(self.background)
        else:
            self.background = self.default_background;


    def paint_background(self):
        """Paint the background screen-centered"""
        screen_width = self.util.options["screen_width"]
        screen_height = self.util.options["screen_height"]
        background_y = (screen_height - self.background.get_height()) / 2
        background_x = (screen_width - self.background.get_width()) / 2
        self.frontend.screen.blit(self.background, (background_x, background_y))


    def paint_list_roms(self, select_rom):
        screen_width = self.util.options["screen_width"]
        screen_height = self.util.options["screen_height"]
        count_roms = len(self.frontend.list_roms)

        middle_y_pos = (screen_height - self.font_size) / 2

        arialFont = pygame.font.SysFont(self.fontname, self.font_size)
        arialFont_bold = pygame.font.SysFont(self.fontname, self.font_size_big, bold = True)

        #TODO optimize this sentence
        ordened_list_roms = self.frontend.list_roms[select_rom:] + self.frontend.list_roms[:select_rom]

        count_roms_show_middle_screen = middle_y_pos / self.vertical_distance_between_roms

        if count_roms_show_middle_screen > count_roms/2:
            list_roms_middle_to_bottom = ordened_list_roms[:count_roms / 2]
            list_roms_middle_to_top = ordened_list_roms[count_roms / 2:]
        else:
            list_roms_middle_to_bottom = ordened_list_roms[:count_roms_show_middle_screen]
            list_roms_middle_to_top = ordened_list_roms[-count_roms_show_middle_screen:]

        list_roms_middle_to_top.reverse()

        y = middle_y_pos
        first = True
        for rom in list_roms_middle_to_bottom:

            if first:
                size = arialFont_bold.size(rom[1])
                x = (screen_width - size[0]) / 2
                color = (255, 255, 0)
                tempImage =  arialFont_bold.render(rom[1], False, color)
                tempImage.set_alpha(255)
            else:
                size = arialFont.size(rom[1])
                x = (screen_width - size[0]) / 2
                color = (255, 255, 255)
                tempImage =  arialFont.render(rom[1], False, color)
                tempImage.set_alpha(128)
            tempImage.convert_alpha()
            #tempImage.set_alpha(255 * 0.75)
            self.frontend.screen.blit(tempImage, (x, y))
            y +=self.vertical_distance_between_roms

            first = False

        y = middle_y_pos - self.vertical_distance_between_roms
        for rom in list_roms_middle_to_top:
            size = arialFont.size(rom[1])
            x = (screen_width - size[0]) / 2
            color = (255, 255, 255)
            tempImage =  arialFont.render(rom[1], False, color)
            tempImage.set_alpha(128)
            tempImage.convert_alpha()
            #tempImage.set_alpha(255 * 0.75)
            self.frontend.screen.blit(tempImage, (x, y))
            y -=self.vertical_distance_between_roms

    def check_limits_select_rom(self, select_rom):
        if -(select_rom) == len(self.frontend.list_roms):
            select_rom = 0
        if select_rom == len(self.frontend.list_roms):
            select_rom = 0
        return select_rom
    
    def run(self):
        select_rom = 0
        exit_var = False
       
        last_pressed_key = None
        last_rom = None
        last_time_move = 0
        sleep_when_pressed_same_key = 800
        change_direction = False
        
        while not exit_var:
                now = pygame.time.get_ticks()
                
                if last_pressed_key is None:
                        id_rom_screensaver = self.frontend.screen_saver()
                
                self.frontend.screen.fill((0, 0, 0))
                
                select_rom = self.check_limits_select_rom(select_rom)
                if select_rom != last_rom:
                        self.load_background(select_rom)
                        last_rom = select_rom
                elif self.background == self.default_background and last_pressed_key == K_RETURN:
                        #Check if have a screenshot of rom that haven't screenshot before.
                        self.load_background(select_rom)
                
                self.paint_background()
                self.paint_list_roms(select_rom)
                
                for e in pygame.event.get():
                        if e.type == QUIT:
                                exit_var = True
                        elif e.type == KEYUP:
                                last_pressed_key = None
                                last_time_to_wait_move = now
                        elif e.type == KEYDOWN:
                                last_pressed_key = None
                                if e.key == K_ESCAPE:
                                        exit_var = True
                                elif e.key == K_UP:
                                        if last_pressed_key != e.key:
                                                select_rom -= 1
                                                sleep_when_pressed_same_key = 800
                                                last_time_move = now
                                                change_direction = True
                                elif e.key == K_DOWN:
                                        if last_pressed_key != e.key:
                                                select_rom += 1
                                                sleep_when_pressed_same_key = 800
                                                last_time_move = now
                                                change_direction = True
                                elif e.key == K_RIGHT:
                                        if last_pressed_key != e.key:
                                                select_rom += 10
                                                sleep_when_pressed_same_key = 800
                                                last_time_move = now
                                                change_direction = True
                                elif e.key == K_LEFT:
                                        if last_pressed_key != e.key:
                                                select_rom -= 10
                                                sleep_when_pressed_same_key = 800
                                                last_time_move = now
                                                change_direction = True
                                elif e.key == K_1 or e.key == K_RETURN:
                                        if (id_rom_screensaver is None) or (id_rom_screensaver == False):
                                                self.frontend.execute_rom(select_rom)
                                        elif id_rom_screensaver is not False:
                                                #Because id_rom_screensaver = None in other case
                                                #and id_rom_screensaver = False in case
                                                #the other image not rom or disabled playing roms of screensaver
                                                select_rom = self.frontend.translate_idrom_to_arraykey(id_rom_screensaver)
                                                
                                                self.frontend.execute_rom(select_rom)
                                
                                last_pressed_key = e.key
                
                if (last_pressed_key is not None) and (not change_direction):
                        if (sleep_when_pressed_same_key + last_time_move) < now:
                                if last_pressed_key == K_DOWN:
                                        select_rom += 1
                                elif last_pressed_key == K_UP:
                                        select_rom -= 1
                                #Acelerate the movement across the list
                                if sleep_when_pressed_same_key > 100:
                                        sleep_when_pressed_same_key -= 100
                                last_time_move = now
                change_direction = False
                self.frontend.waitFrame()
                pygame.display.update()
