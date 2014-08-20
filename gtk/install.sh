sudo apt-get install libgtk2.0-dev
gcc `pkg-config --cflags gtk+-2.0` -o screen screen.c `pkg-config --libs gtk+-2.0`
