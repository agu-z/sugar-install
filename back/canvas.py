#!/usr/bin/env python
# -*- coding: utf-8 -*-

# canvas.py by:
#    Agustin Zubiaga <aguz@sugarlabs.org>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
import gobject
import pango
import threading
import utils

from gettext import gettext as _

BTN_COLOR = gtk.gdk.color_parse("blue")

# Logging
_logger = utils.get_logger()


class Canvas(gtk.Notebook):

    def __init__(self, parent):
        gtk.Notebook.__init__(self)

        self._parent = parent

        # Search List
        self.gtk_list = List(self._parent)

        eventbox = gtk.EventBox()
        eventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#FFFFFF"))
        eventbox.add(self.gtk_list)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(eventbox)

        self.append_page(scroll)

        # Download List
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        scroll.add_with_viewport(self.gtk_list.download_list)
        self.append_page(scroll)

        self.set_property('show-tabs', False)

        self.show_all()

    def switch_to_list(self, widget):
        self.set_page(0)
        if not widget:
            self._parent.store_list.set_active(True)

    def switch_to_downloads_list(self, widget):
        self.set_page(1)


class List(gtk.VBox):

    def __init__(self, parent):
        gtk.VBox.__init__(self)

        self.download_list = DownloadList()

        self._parent = parent
        self.thread = None
        self.words = ''
        self._list = utils.get_store_list()
        self.can_search = True
        self.stopped = False

        self.show_all()

    def stop_search(self, *args):
        self.stopped = True

    def _add_activity(self, widget):
        self.pack_start(widget, False, False, 7)
        separator = gtk.HSeparator()
        self.pack_start(separator, False, False, 2)

        widget.show()
        separator.show()

    def clear(self):
        for child in self.get_children():
            self.remove(child)
            child = None

    def search(self, entry):
        #_logger.debug(threading.enumerate())
        if self.can_search:
            self.can_search = False
            self.w = entry.get_text().lower()
            self.clear()
            self.thread = threading.Thread(target=self._search)
            self.thread.start()
        else:
            self.stop_search()
            gobject.idle_add(self.search, entry)

    def _search(self):
        w = str(self.w)
        _id = -1
        for activity in self._list:
            if self.stopped:
                break
            _id += 1
            name = activity[1].lower()
            description = activity[2].lower()
            if (w in name) or (w in description):
                activity_widget = ActivityWidget(_id, self)
                self._add_activity(activity_widget)
        self.can_search = True


class ActivityWidget(gtk.HBox):

    def __init__(self, _id, parent):
        gtk.HBox.__init__(self, False, 0)

        self._id = _id
        self._download_list = parent.download_list
        self._downloads_icon = parent._parent.downloads_icon

        self.name_label = self._label()
        self.icon = gtk.Image()
        self.install_button = gtk.Button(_("INSTALL"))
        self.install_button.connect("clicked", self._btn_clicked)
        self.install_button.modify_bg(gtk.STATE_NORMAL, BTN_COLOR)
        self.install_button.modify_bg(gtk.STATE_PRELIGHT, BTN_COLOR)
        self.install_button.modify_bg(gtk.STATE_ACTIVE, BTN_COLOR)
        self.install_button.set_size_request(gtk.gdk.screen_width() / 10, -1)

        self._activity_props = parent._list[_id]

        self._left_box = gtk.VBox()
        self._right_box = gtk.VBox()
        self._icon_and_label = gtk.HBox()

        self._icon_and_label.pack_start(self.icon, False, True, 0)
        self._icon_and_label.pack_end(self.name_label, True, True, 6)
        self._left_box.pack_start(self._icon_and_label, False, True, 0)
        self._left_box.pack_end(self.install_button, False, True, 0)

        self.desc_label = self._label()
        self.vers_label = self._label()
        self.suga_label = self._label()
        self.upda_label = self._label()
        self.down_label = self._label()
        self.home_label = self._label()

        self._right_box.pack_start(self.desc_label, False, True, 0)
        self._right_box.pack_start(self.vers_label, False, True, 0)
        self._right_box.pack_start(self.suga_label, False, True, 0)
        self._right_box.pack_start(self.upda_label, False, True, 0)
        self._right_box.pack_start(self.down_label, False, True, 0)
        self._right_box.pack_start(self.home_label, False, True, 0)

        self.pack_start(self._left_box, False, True, 10)
        self.pack_end(self._right_box, False, True, 50)

        self.connect("expose-event", self._expose_event_cb)

        self._setup()

        self.show_all()

    def _expose_event_cb(self, widget, event):
        self.install_button.set_size_request(gtk.gdk.screen_width() / 10, -1)

    def _label(self):
        label = gtk.Label()
        label.set_justify(gtk.JUSTIFY_LEFT)
        label.set_line_wrap(True)

        return label

    def _setup(self):
        self.name_label.set_markup("<b>%s</b>" % self._activity_props[1])

        self.desc_label.set_markup(self._activity_props[2])
        self.vers_label.set_markup('<b>Version:</b> ' + self._activity_props[3])
        self.suga_label.set_markup('<b>Works with:</b> ' +\
                     self._activity_props[4] + ' - ' + self._activity_props[5])
        self.upda_label.set_markup('<b>Updated:</b> ' + self._activity_props[6])
        self.down_label.set_markup('<b>Downloads:</b> ' +\
                                                        self._activity_props[7])
        self.home_label.set_markup('<b>Homepage:</b> ' +\
                                                        self._activity_props[8])

        try:
            pixbuf_icon = utils.get_icon(self._id)
            self.icon.set_from_pixbuf(pixbuf_icon)
        except:
            pass

    def _btn_clicked(self, widget):
        _logger.info("Install button clicked (%s)")
        self._downloads_icon.animate()

        threading.Thread(target=utils.download_activity, args=(self._id,
                                self._progress_changed)).start()

        self._download_id = self._download_list.add_download(
                                                       self._activity_props[1])

    def _progress_changed(self, progress):
        self._download_list.set_download_progress(self._download_id, progress)


class DownloadList(gtk.TreeView):

    def __init__(self):
        gtk.TreeView.__init__(self)

        self._model = gtk.ListStore(str, str, int)
        self.set_model(self._model)

        renderer_text = gtk.CellRendererText()
        column_text = gtk.TreeViewColumn(_("Name"), renderer_text, text=0)
        self.append_column(column_text)

        renderer_text = gtk.CellRendererText()
        column_text = gtk.TreeViewColumn(_("State"), renderer_text, text=1)
        self.append_column(column_text)

        renderer_progress = gtk.CellRendererProgress()
        column_progress = gtk.TreeViewColumn(_("Progress"), renderer_progress,
            value=2)
        self.append_column(column_progress)

        self.show_all()

    def add_download(self, name):
        _iter = self._model.append([name, _("Starting download..."), 0])
        return _iter

    def set_download_progress(self, _id, progress):
        if progress <= 100:
            self._model[_id][2] = int(progress)

        if progress > 0:
            self._model[_id][1] = _("Downloading...")

        if progress >= 150:
            self._model[_id][1] = _("Installing...")
            self._model[_id][2] = 100

        if progress == 200:
            self._model[_id][1] = _("Installed!")
