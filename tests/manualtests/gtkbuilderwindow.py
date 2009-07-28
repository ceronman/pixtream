import sys
sys.path.append('..')

import pygtk
pygtk.require('2.0')

import gtk

from pixtream.peer.gtkui.gtkbuilderwindow import GtkBuilderWindow

class TestWindow(GtkBuilderWindow):

    builder_file = 'testwindow.glade'

    def on_button_clicked(self, sender, *args):
        print 'clicked'
        self.title_label.set_text('clicked')


win = TestWindow()
win.show_all()

gtk.main()
