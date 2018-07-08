#
# gtkui.py
#
# Copyright (C) 2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2015 Chris Yereaztian <chris.yereaztian@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#
#

import gtk

from deluge.log import LOG as log
from deluge.ui.client import client
from deluge.plugins.pluginbase import GtkPluginBase
import deluge.component as component
import deluge.common

from common import get_resource

class GtkUI(GtkPluginBase):
    def enable(self):
        self.glade = gtk.glade.XML(get_resource("extractmod_prefs.glade"))

        # Preferences
        component.get("Preferences").add_page(_("ExtractMod"), self.glade.get_widget("extractmod_prefs_box"))
        component.get("PluginManager").register_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").register_hook("on_show_prefs", self.on_show_prefs)
        # self.on_show_prefs()

        # Submenu
        log.debug("add items to torrentview-popup menu.")
        torrentmenu = component.get("MenuBar").torrentmenu
        self.extractmod_menu = ExtractModMenu()
        torrentmenu.append(self.extractmod_menu)
        self.extractmod_menu.show_all()

    def disable(self):
        # Preferences
        component.get("Preferences").remove_page(_("ExtractMod"))
        component.get("PluginManager").deregister_hook("on_apply_prefs", self.on_apply_prefs)
        component.get("PluginManager").deregister_hook("on_show_prefs", self.on_show_prefs)
        # del self.glade

        try:
            # Submenu
            torrentmenu = component.get("MenuBar").torrentmenu
            torrentmenu.remove(self.extractmod_menu)
        except Exception, e:
            log.debug(e)

    def on_apply_prefs(self):
        log.debug("applying prefs for ExtractMod")
        if client.is_localhost():
            path = self.glade.get_widget("folderchooser_path").get_filename()
        else:
            path = self.glade.get_widget("entry_path").get_text()

        config = {
            "extract_path": path,
            "use_name_folder": self.glade.get_widget("chk_use_name").get_active(),
            "in_place_extraction": self.glade.get_widget("chk_in_place_extraction").get_active()
        }

        client.extractor.set_config(config)

    def on_show_prefs(self):
        if client.is_localhost():
            self.glade.get_widget("folderchooser_path").show()
            self.glade.get_widget("entry_path").hide()
        else:
            self.glade.get_widget("folderchooser_path").hide()
            self.glade.get_widget("entry_path").show()

        def on_get_config(config):
            if client.is_localhost():
                self.glade.get_widget("folderchooser_path").set_current_folder(config["extract_path"])
            else:
                self.glade.get_widget("entry_path").set_text(config["extract_path"])

            self.glade.get_widget("chk_use_name").set_active(config["use_name_folder"])
            self.glade.get_widget("chk_in_place_extraction").set_active(config["in_place_extraction"])

        client.extractor.get_config().addCallback(on_get_config)


class ExtractModMenu(gtk.MenuItem):
    def __init__(self):
        gtk.MenuItem.__init__(self, "ExtactMod")

        self.sub_menu = gtk.Menu()
        self.set_submenu(self.sub_menu)
        self.items = []

        #attach..
        torrentmenu = component.get("MenuBar").torrentmenu
        self.sub_menu.connect("show", self.on_show, None)

    def get_torrent_ids(self):
        return component.get("TorrentView").get_selected_torrents()


    def on_show(self, widget=None, data=None):
        try:
            for child in self.sub_menu.get_children():
                self.sub_menu.remove(child)
                
            extract_item = gtk.MenuItem('Exract')
            extract_item.connect("activate", self.on_select_extract)
            self.sub_menu.append(extract_item)

            self.show_all()
        except Exception, e:
            log.exception('AHH!')

    def on_select_extract(self, widget=None):
        log.debug("select extract: %s" % self.get_torrent_ids())
        for torrent_id in self.get_torrent_ids():
            client.extractmod.extract_and_chmod(torrent_id)

    # def on_show(self, widget=None, data=None):
    #     try:
    #         for child in self.sub_menu.get_children():
    #             self.sub_menu.remove(child)
    #         # TODO: Make thise times customizable, and/or add a custom popup
    #         for time in (None, 1, 2, 3, 7, 14, 30):
    #             if time is None:
    #                 item = gtk.MenuItem('Never')
    #             else:
    #                 item = gtk.MenuItem(str(time) + ' days')
    #             item.connect("activate", self.on_select_time, time)
    #             self.sub_menu.append(item)
    #         item = gtk.MenuItem('Custom')
    #         item.connect('activate', self.on_custom_time)
    #         self.sub_menu.append(item)
    #         self.show_all()
    #     except Exception, e:
    #         log.exception('AHH!')

    # def on_select_time(self, widget=None, time=None):
    #     log.debug("select seed stop time:%s,%s" % (time ,self.get_torrent_ids()) )
    #     for torrent_id in self.get_torrent_ids():
    #         client.seedtime.set_torrent(torrent_id, time)

    # def on_custom_time(self, widget=None):
    #     # Show the custom time dialog
    #     glade = gtk.glade.XML(get_resource("config.glade"))
    #     dlg = glade.get_widget('dlg_custom_time')
    #     result = dlg.run()
    #     if result == gtk.RESPONSE_OK:
    #         time = glade.get_widget('txt_custom_stop_time').get_text()
    #         try:
    #             self.on_select_time(time=float(time))
    #         except ValueError:
    #             log.error('Invalid custom stop time entered.')
    #     dlg.destroy()
