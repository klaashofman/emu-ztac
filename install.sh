# ANSI color codes
RS='\e[0m'    	# reset
FRED='\e[31m' 	# foreground red
BRED='\e[1;31m' # bold red

echo -e "$BRED --- DGEN --- $RS"
# install prerequisites
sudo apt-get install --assume-yes libsdl1.2-dbg libsdl1.2-dev libsdl1.2debian
rm -rf dgen-sdl-1.33
if [ ! -f dgen-sdl-1.33.tar.gz ]; then
	wget http://sourceforge.net/projects/dgen/files/dgen/1.33/dgen-sdl-1.33.tar.gz
fi
tar xvzf dgen-sdl-1.33.tar.gz
cd dgen-sdl-1.33
./configure || exit "$FRED dgen: configure error $RS"
make && sudo make install || exit "$FRED dgen: error building $RS"

# frontend application
cd gtk
./install || exit "Error in frontend application"

