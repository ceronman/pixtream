"""
Main Window of the Pixtream GUI
"""

import gtk

from pixtream.peer.gtkui.gtkbuilderwindow import GtkBuilderWindow
from pixtream.peer.gtkui import resources
from pixtream.peer.peerservice import PeerService

class MainWindow(GtkBuilderWindow):

    builder_file = resources.get_file('glade', 'mainwindow.glade')

    def __init__(self, ip, port, tracker_url, streaming_port):
        super(MainWindow, self).__init__()
        self._create_peer_service(ip, port, tracker_url, streaming_port)
        self._configure_gui()

    def _create_peer_service(self, ip, port, tracker_url, streaming_port):
        self.peer_service = PeerService(ip, port, tracker_url, streaming_port)
        self.peer_service.on_peers_update.add_handler(self._update_peers)
        self.peer_service.listen()
        self.peer_service.connect_to_tracker()

    def _configure_gui(self):
        self.id_label.set_text(self.peer_service.peer_id)
        self.port_label.set_text(str(self.peer_service.port))

    def _update_peers(self, peers):
        for child in self.in_peers_box.get_children():
            self.in_peers_box.remove(child)

        for peer_id in self.peer_service.incoming_peers:
            label = gtk.Label(peer_id)
            self.in_peers_box.pack_start(label)

        self.in_peers_box.show_all()

        for child in self.out_peers_box.get_children():
            self.out_peers_box.remove(child)

        for peer_id in self.peer_service.outgoing_peers:
            label = gtk.Label(peer_id)
            self.out_peers_box.pack_start(label)

        self.out_peers_box.show_all()


