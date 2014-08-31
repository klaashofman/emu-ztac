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

from Util import Util
from Frontend import Frontend
import os


def main():
    util = Util()
    if util.options['run']:
        if util.options['config']:
            print("Enter in configuration mode")
            frontend = Frontend(config_mode=True, util_param = util)
        elif util.options['scan_roms']:
            print("Scan new roms")
            # util.scan_roms()
            frontend = Frontend(config_mode=False, util_param = util)
        else:
            frontend = Frontend(config_mode=False, util_param = util)
    frontend.save_current_mode()
    if util.options['shutdown_on_exit']:
        os.system(util.options['shutdown_command'])

if __name__ == '__main__':
    main()
