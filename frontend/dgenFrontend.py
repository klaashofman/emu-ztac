__author__ = 'KH'


import os
import pygame
from pygame.locals import *
import sqlite3
import subprocess
import random
import string
from pprint import *
from db import *


class Frontend:
    screenWidth=640
    screenHeight=480
    screenVars = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
    background  = None
    font_size = 30
    font_size_big = 36
    fontname = 'Arial'
    margin_between_roms = 10
    vertical_distance_between_roms = font_size + margin_between_roms
    db = None

    def __init__(self, db_param = None):
        self.db = db_param
        self.list_roms = self.get_all_roms()
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption("Dgen-Frontend")
        self.screen = pygame.display.set_mode([self.screenWidth, self.screenHeight], self.screenVars, 32)
        self.run()

    def get_all_roms(self):
        connection = sqlite3.connect(self.db.frontend_db)
        cursor = connection.cursor()
        cursor.execute("SELECT rom, name, custom_options, status, roms.id, year, manufacturer, display_type, display_screen, input_players, input_control, input_buttons \
                                                FROM roms LEFT JOIN rom_info \
                                                ON roms.id = rom_info.id WHERE disabled = 0 AND found = 1 ORDER BY name ASC;")
        return cursor.fetchall()


    def paint_list_roms(self, select_rom):
        count_roms = len(self.list_roms)

        middle_y_pos = (self.screenHeight - self.font_size) / 2

        arialFont = pygame.font.SysFont(self.fontname, self.font_size)
        arialFont_bold = pygame.font.SysFont(self.fontname, self.font_size_big, bold = True)

        #TODO optimize this sentence
        ordened_list_roms = self.list_roms[select_rom:] + self.list_roms[:select_rom]

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
                x = (self.screenWidth - size[0]) / 2
                color = (255, 255, 0)
                tempImage =  arialFont_bold.render(rom[1], False, color)
                tempImage.set_alpha(255)
            else:
                size = arialFont.size(rom[1])
                x = (self.screenWidth - size[0]) / 2
                color = (255, 255, 255)
                tempImage =  arialFont.render(rom[1], False, color)
                tempImage.set_alpha(128)
            tempImage.convert_alpha()
            #tempImage.set_alpha(255 * 0.75)
            self.screen.blit(tempImage, (x, y))
            y +=self.vertical_distance_between_roms

            first = False

        y = middle_y_pos - self.vertical_distance_between_roms
        for rom in list_roms_middle_to_top:
            size = arialFont.size(rom[1])
            x = (self.screenWidth - size[0]) / 2
            color = (255, 255, 255)
            tempImage =  arialFont.render(rom[1], False, color)
            tempImage.set_alpha(128)
            tempImage.convert_alpha()
            #tempImage.set_alpha(255 * 0.75)
            self.screen.blit(tempImage, (x, y))
            y -=self.vertical_distance_between_roms

    def check_limits_select_rom(self, select_rom):
        if -(select_rom) == len(self.list_roms):
            select_rom = 0
        if select_rom == len(self.list_roms):
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

                # if last_pressed_key is None:
                #         id_rom_screensaver = self.frontend.screen_saver()

                self.screen.fill((0, 0, 0))

                select_rom = self.check_limits_select_rom(select_rom)
                if select_rom != last_rom:
                        # self.load_background(select_rom)
                        last_rom = select_rom
#                elif self.background == self.default_background and last_pressed_key == K_RETURN:
                        #Check if have a screenshot of rom that haven't screenshot before.
 #                       self.load_background(select_rom)

 #               self.paint_background()
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
#                                        if (id_rom_screensaver is None) or (id_rom_screensaver == False):
#                                                self.frontend.execute_rom(select_rom)
#                                        elif id_rom_screensaver is not False:
#                                                #Because id_rom_screensaver = None in other case
#                                                #and id_rom_screensaver = False in case
#                                                #the other image not rom or disabled playing roms of screensaver
#                                                select_rom = self.frontend.translate_idrom_to_arraykey(id_rom_screensaver)

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
                # self.frontend.waitFrame()
                pygame.display.update()
        else:
            pass

if __name__ == '__main__':
    db = Db()
    frontend = Frontend(db_param = db)

