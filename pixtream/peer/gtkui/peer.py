"""
A Pixtream Peer Script with PyGTK gui
"""

from twisted.internet import gtk2reactor
gtk2reactor.install()
from twisted.internet import reactor

from pixtream.peer import scriptutils
from pixtream.peer.gtkui.mainwindow import MainWindow

def run():
    scriptutils.setup_logger()
    ip, port, tracker = scriptutils.parse_options()
    window = MainWindow(ip, port, tracker)
    window.show_all()
    reactor.run()
