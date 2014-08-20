
#include <gtk/gtk.h>
int main (int argc, char *argv[])
{
	/*** The Widgets we'll be using ***/
	GtkWidget *win = NULL;
	GtkWidget *close = NULL;
	
	/*** Initialize GTK+ ***/
	g_log_set_handler ("Gtk", G_LOG_LEVEL_WARNING, (GLogFunc) gtk_false, NULL);
	gtk_init (&argc, &argv);
	g_log_set_handler ("Gtk", G_LOG_LEVEL_WARNING, g_log_default_handler, NULL);
	
	/*** Make that Window!!! ***/
	win = gtk_window_new (GTK_WINDOW_TOPLEVEL);
	gtk_container_set_border_width (GTK_CONTAINER (win), 10);
	gtk_widget_realize (win);
	gtk_window_fullscreen(win);
	
	/*** this is a button that'll help us close the window ***/
	close = gtk_button_new_with_label("Close Window");
	gtk_container_add(win, close);
	
	/*** Callbacks ***/
	g_signal_connect (close, "clicked", gtk_main_quit, NULL);
	g_signal_connect (win, "destroy", gtk_main_quit, NULL);
	/*** Enter the main loop ***/
	gtk_widget_show_all (win);
	gtk_main ();
	return 0;
}


