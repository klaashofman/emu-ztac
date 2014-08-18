# install prerequisites
sudo apt-get install libsdl1.2-dbg libsdl1.2-dev libsdl1.2debian
# dgen-sdl-x86 - genesis emulator
rm -rf dgen-sdl-1.33-w32-x86+SSE2
wget http://sourceforge.net/projects/dgen/files/dgen/1.33/dgen-sdl-1.33-w32-x86%2BSSE2.zip
unzip dgen-sdl-1.33-w32-x86+SSE2.zip
cd dgen-sdl-1.33-w32-x86+SSE2
./configure || exit "dgen: configure error"
make && sudo make install

# frontend application


