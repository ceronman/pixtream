from gettext import gettext

from gobject import GError
import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk

class GtkBuilderWindow(object):
    """
    A magic window class for GtkBuilder Windows
    """

    builder_file = None

    def __init__(self):
        self._builder = gtk.Builder()

        assert isinstance(self.builder_file, str), 'builder_file not specified'

        try:
            self._builder.add_from_file(self.builder_file)
        except GError:
            raise IOError('GtkBuilder file not found')

        root_window = self.__class__.__name__
        self._window = self._builder.get_object(root_window)

        if self._window is None:
            error = 'Class name ({0}) should match with object in file {1}'
            error = error.format(root_window, self.builder_file)
            raise NameError(error)

        self._builder.connect_signals(self)

    def __getattr__(self, name):
        widget = self._builder.get_object(name)

        if widget is not None:
            return widget

        return getattr(self._window, name)

    def show_error(self, message):
        dialog = gtk.MessageDialog(self._window,
                                   gtk.DIALOG_MODAL|
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_ERROR,
                                   gtk.BUTTONS_OK)

        dialog.set_title(gettext('Error'))
        dialog.set_markup(message)
        response = dialog.run()
        dialog.destroy()
        return response

    def gtk_main_quit(self, *args):
        gtk.main_quit()

    def on_delete_event(self, *args):
        self.destroy()

    def set_watch_cursor(self):
        self._window.window.set_cursor(gdk.Cursor(gdk.WATCH))
        gtk.main_iteration(False)

    def set_normal_cursor(self):
        self._window.window.set_cursor(None)
        gtk.main_iteration(False)

    def get_real_widget(self):
        return self._window
