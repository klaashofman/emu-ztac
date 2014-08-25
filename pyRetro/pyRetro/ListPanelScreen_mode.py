# -*- coding: utf-8 -*-
"""
   Copyright (C) 2011 David Skywalker (aka D_Skywalk)
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

import math

from pprint import *


class ListPanelScreen_mode:
    font_size = 15
    margin_between_roms = 4
    background_color = (0, 0, 0)
    first_font_color = (255, 255, 255)
    vertical_distance_between_roms = font_size + margin_between_roms


    def __init__(self, util_param = None, frontend_param = None):
        self.util = util_param
        self.snap = None
        self.video = None
        self.video_status = 0 # 0 none, 1 loaded, 2 playing, # 3 played # -1 not found
        self.frontend = frontend_param
        self.create_default_images()
        self.global_count_roms = len(self.frontend.list_roms)


    def create_default_images(self):
        self.default_snap = pygame.image.load(os.path.join(os.path.dirname(__file__),"layout","default_snap.png")).convert()
        self.background = pygame.Surface((self.util.options["screen_width"], self.util.options["screen_height"]))
        self.background.fill((0, 0, 0))

        temp = pygame.image.load(os.path.join(os.path.dirname(__file__),"layout","main.png")).convert_alpha()
        self.background.blit(temp, (0, 0))


    def load_snap(self, select_rom):
        del self.snap
        self.snap = None
        background_dir = self.util.options["snapshots_directory"] + "/" #+ self.frontend.list_roms[select_rom][0]
        # Try if exists some snapshot_dir and load some select_rom.png files there
        if os.path.exists(background_dir):
            background_dir = self.util.options["snapshots_directory"] + "/"
            snap_file = background_dir + self.frontend.list_roms[select_rom][0] + ".png"
            if os.path.isfile(snap_file):
                self.snap = pygame.image.load(snap_file).convert()
        #try with snap/romfile.png
        else:
            background_dir = self.util.options["snapshots_directory"] + "/"
            snap_file = background_dir + self.frontend.list_roms[select_rom][0] + ".png"
            if os.path.isfile(snap_file):
                self.snap = pygame.image.load(snap_file).convert()

        if self.snap:
            self.snap = self.frontend.resize_with_aspect(self.snap, 256, 230)
        else:
            self.snap = self.default_snap

    def load_video(self, select_rom):
        del self.video
        self.video = None
        video_file = self.util.options["dir_default_game_video"] + "/" + self.frontend.list_roms[select_rom][0] + ".mpg"
        if os.path.isfile(video_file):
            self.video = pygame.movie.Movie(video_file)

        if self.video:
            vsize = self.frontend.get_resize_with_aspect(self.video.get_size(), (256 , 230))
            vsize_width, vsize_height = vsize
            if (vsize_width > vsize_height):
                snap_x = 0
                snap_y = (230 - vsize_height) / 2
                snap_y &= 0xFFE # force even value
            else:
                snap_x = (256 - vsize_width) / 2
                snap_x &= 0xFFE # force even value
                snap_y = 0
            # 360x40 is safe position - take care if you change this,
            # some videos in odd positions should freeze whole frontend.
            self.video.set_display(self.frontend.screen, pygame.Rect((360 + snap_x, 40 + snap_y ), vsize))
            self.video.set_volume(0.5) #TODO: in cfg?

            self.video_status = 1
        else:
            self.video_status = -1

    def unload_video(self):
        self.video_status = 0
        if not self.video:
            return
        if self.video.get_busy():
            self.video.stop()

    def paint_list_roms(self, select_rom):
        #pos 29x39
        #base 249x403
        panel_width =  249
        panel_height = 403
        margin_left = 29
        margin_top = 42
        count_roms = self.global_count_roms
        roms_per_screen = int( panel_height / self.vertical_distance_between_roms)
        first_show_rom = (select_rom - (roms_per_screen/2))
        last_show_rom = (select_rom + 1) - (count_roms - (roms_per_screen / 2))

        if last_show_rom >= 0 and first_show_rom > 0:
            list_roms = self.frontend.list_roms[-roms_per_screen:]
            current_rom = (roms_per_screen / 2) + last_show_rom
        elif first_show_rom > 0:
            list_roms = self.frontend.list_roms[first_show_rom:(first_show_rom + roms_per_screen)]
            current_rom = (roms_per_screen / 2)
        else:
            current_rom = (roms_per_screen / 2) + first_show_rom
            list_roms = self.frontend.list_roms[:roms_per_screen]


        atariFont = pygame.font.SysFont('SF Atarian System Extended', self.font_size)

        n = 0
        y = 0
        for rom in list_roms:
            size = atariFont.size(rom[1])
            x = (panel_width - size[0]) / 2
            #TODO: check once?
            if n == current_rom:
                color = (255, 255, 0)
            else:
                color = (0, 255, 0)
            tempImage =  atariFont.render(rom[1], 1, color, self.background_color)

            #check to crop render font
            if tempImage.get_width() > panel_width:
                crop_width = (tempImage.get_width() - panel_width) / 2
                font_part = (crop_width, 0, panel_width, self.vertical_distance_between_roms ) # left,top,width,height of image area
                self.frontend.screen.blit(tempImage, (x + margin_left + crop_width, y + margin_top), font_part)
            else:
                self.frontend.screen.blit(tempImage, (x + margin_left, y + margin_top))

            y +=self.vertical_distance_between_roms
            n += 1


    def paint_main(self):
        #pos 15, 0
        #275x20
        atariFont = pygame.font.SysFont('SF Atarian System Extended', 15)
        tempImage =  atariFont.render("Listed " + str(self.global_count_roms) + " roms", 1, self.first_font_color, self.background_color)
        x = (275 - tempImage.get_width()) / 2 # calc center
        self.frontend.screen.blit(tempImage, (15 + x, 2))

        atariFont = pygame.font.SysFont('SF Atarian System Extended', 15)
        emulator_name = "M.A.M.E."
        tempImage =  atariFont.render(emulator_name, 1, self.first_font_color, self.background_color)
        x = (276 - tempImage.get_width()) / 2 # calc center
        self.frontend.screen.blit(tempImage, (347 + x, 2))


    def paint_gameinfo(self, select_rom):
        #pos 358x326
        #258x20
        panel_width = 258
        atariFont = pygame.font.SysFont('SF Atarian System Extended', 15)
        color = (255, 83, 0)
        color_wip = (205, 205, 53)
        rom = self.frontend.list_roms[select_rom]

        tempImage =  atariFont.render("Game Description", 1, color, self.background_color)
        x = (258 - tempImage.get_width()) / 2 # calc center
        self.frontend.screen.blit(tempImage, (358 + x, 326))

        # rom, name, custom_options, status, id, year, manufacturer, display_type, display_screen, input_players, input_control, input_buttons
        tempImage =  atariFont.render( rom[0]+ ".zip", 1, self.first_font_color, self.background_color)
        x = (258 - tempImage.get_width()) / 2 # calc center
        self.frontend.screen.blit(tempImage, (358 + x, 326 + 20))

        # year - manufacturer
        tempImage =  atariFont.render(rom[5] + " " + rom[6] , 1, color_wip, self.background_color)
        x = (258 - tempImage.get_width()) / 2 # calc center
        if tempImage.get_width() > panel_width:
            crop_width = (tempImage.get_width() - panel_width) / 2
            font_part = (crop_width, 0, panel_width, self.vertical_distance_between_roms ) # left,top,width,height of image area
            self.frontend.screen.blit(tempImage, (358 + (x + crop_width), 326 + 40), font_part)
        else:
            self.frontend.screen.blit(tempImage, (358 + x, 326 + 40))

        # display_type
        tempImage =  atariFont.render( rom[7], 1, color_wip, self.background_color)
        x = (258 - tempImage.get_width()) / 2 # calc center
        self.frontend.screen.blit(tempImage, (358 + x, 326 + 60))

        tempImage =  atariFont.render( ((str(rom[9]) + ' player' + ('s' if rom[9] > 1 else '') + " / ") if rom[9] > 0 else '') \
                                                                        + ((rom[10] + " / " ) if rom[10] else '') \
                                                                        + ((str(rom[11]) + " button" + ('s' if rom[11] > 0 else '')) if rom[11] > 0 else ''), 1, color_wip, self.background_color)
        x = (258 - tempImage.get_width()) / 2 # calc center
        self.frontend.screen.blit(tempImage, (358 + x, 326 + 80))

        tempImage =  atariFont.render( "Status (" + rom[3] + ")", 1, self.first_font_color, self.background_color)
        x = (258 - tempImage.get_width()) / 2 # calc center
        self.frontend.screen.blit(tempImage, (358 + x, 326 + 100))


    def paint_screen(self, select_rom):
        self.frontend.screen.fill(self.background_color)
        self.frontend.screen.blit(self.background, (0, 0))
        #pos 359x39
        #base 256x230
        if (self.snap.get_width() > self.snap.get_height()):
            snap_x = 0
            snap_y = (230 - self.snap.get_height()) / 2
        else:
            snap_x = (256 - self.snap.get_width()) / 2
            snap_y = 0

        self.frontend.screen.blit(self.snap, (360 + snap_x, 40 + snap_y))
        self.paint_gameinfo(select_rom)
        self.paint_list_roms(select_rom)
        self.paint_main()


    def check_limits_select_rom(self, select_rom):
        if select_rom >= self.global_count_roms:
            select_rom = self.global_count_roms - 1

        if select_rom < 0:
            select_rom = 0

        return select_rom


    def run(self):
        select_rom = self.check_limits_select_rom(self.util.load_value_db("internal_selected_rom", 0))

        exit_var = False

        last_pressed_key = None
        last_time_move = 0
        last_time_sleep = pygame.time.get_ticks()
        sleep_when_pressed_same_key = 800
        change_direction = False
        last_rom = select_rom

        #TODO: future use with name rom scroll
        force_update = 1

        #first run load first snap
        self.load_snap(select_rom)

        while not exit_var:
            now = pygame.time.get_ticks()
            # check key, is playing and if screen need an update
            if last_pressed_key is None and self.video_status != 2 and force_update == 0:
                id_rom_screensaver = self.frontend.screen_saver()

            select_rom = self.check_limits_select_rom(select_rom)
            if select_rom != last_rom:
                self.load_snap(select_rom)
                self.paint_screen(select_rom)
                last_rom = select_rom
            elif force_update:
                self.paint_screen(select_rom)
                force_update = 0

            for e in pygame.event.get():
                if e.type == QUIT:
                    exit_var = True
                    self.unload_video()
                elif e.type == KEYUP:
                    last_pressed_key = None
                    last_time_sleep = now
                elif e.type == KEYDOWN:
                    last_pressed_key = None
                    last_time_sleep = None
                    self.unload_video()
                    if e.key == K_ESCAPE:
                        exit_var = True
                    elif e.key == K_UP:
                        if last_pressed_key != e.key:
                            select_rom -= 1
                            sleep_when_pressed_same_key = 400
                            last_time_move = now
                            change_direction = True
                    elif e.key == K_DOWN:
                        if last_pressed_key != e.key:
                            select_rom += 1
                            sleep_when_pressed_same_key = 400
                            last_time_move = now
                            change_direction = True
                    elif e.key == K_LEFT:
                        if last_pressed_key != e.key:
                            select_rom -= 25
                            sleep_when_pressed_same_key = 400
                            last_time_move = now
                            change_direction = True
                    elif e.key == K_RIGHT:
                        if last_pressed_key != e.key:
                            select_rom += 25
                            sleep_when_pressed_same_key = 400
                            last_time_move = now
                            change_direction = True
                    elif e.key == K_2:
                        self.video.stop()
                    elif e.key == K_1 or e.key == K_RETURN:
                        if (id_rom_screensaver is None) or (id_rom_screensaver == False):
                            self.frontend.execute_rom(select_rom)
                        elif id_rom_screensaver is not False:
                            #Because id_rom_screensaver = None in other case
                            #and id_rom_screensaver = False in case
                            #the other image not rom or disabled playing roms of screensaver
                            select_rom = self.frontend.translate_idrom_to_arraykey(id_rom_screensaver)

                            self.frontend.execute_rom(select_rom)

                        force_update = 1 # force update screen

                    last_pressed_key = e.key

            if (last_pressed_key is not None) and (not change_direction):
                if (sleep_when_pressed_same_key + last_time_move) < now:
                    if last_pressed_key == K_DOWN:
                        select_rom += 1
                    elif last_pressed_key == K_UP:
                        select_rom -= 1
                    elif last_pressed_key == K_LEFT:
                        select_rom -= 25
                    elif last_pressed_key == K_RIGHT:
                        select_rom += 25

                    #Acelerate the movement across the list
                    if sleep_when_pressed_same_key > 50:
                        sleep_when_pressed_same_key -= 50
                    elif sleep_when_pressed_same_key > 10:
                        sleep_when_pressed_same_key -= 10

                    last_time_move = now

            change_direction = False
            if last_time_sleep is not None and ((self.util.options["seconds_wait_video"] * 1000) + last_time_sleep) < now:
                if self.video_status == 0:
                    self.load_video(select_rom)
                elif self.video_status == 1:
                    #TODO: if video is not resized atm we dont need this clean
                    pygame.draw.rect(self.frontend.screen, self.background_color, Rect(360, 40, 256, 230))
                    pygame.display.update() #TODO: update with clean snap?
                    self.video.play()
                    self.video_status = 2
                    last_time_sleep = None

            if self.video_status != 2: # if screen is not controlled by pymovie
                self.frontend.waitFrame()
                pygame.display.update()
            elif not self.video.get_busy(): # video finished
                self.unload_video()
                force_update = 1
                self.video_status = 3

        #end main loop - unload video
        if self.video:
            self.video.stop()
            del self.video
            self.video = None

        #save last position in save_data table in DB
        self.util.save_value_db("internal_selected_rom", select_rom, "int")
