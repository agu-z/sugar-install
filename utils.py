#!/usr/bin/env python
# -*- coding: utf-8 -*-

# utils.py by:
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

import os
import gtk
import time
import json
import urllib
import logging

from sugar.activity import activity
from sugar.bundle.activitybundle import ActivityBundle

# Paths
LIST_DOWNLOAD = "https://sites.google.com/site/agustinzubiaga/archivos/store.lst"
LIST_PATH = os.path.join(activity.get_activity_root(), 'data', 'store.lst')
TMP_DIR = os.path.join(activity.get_activity_root(), "tmp")

# Logging
_logger = logging.getLogger('activitiesstore-activity')
_logger.setLevel(logging.DEBUG)
logging.basicConfig()


def get_logger():
    return _logger


def update_list():
    """Download the latest list version"""
    remote_file = urllib.urlopen(LIST_DOWNLOAD)
    file = open(LIST_PATH, 'w')
    file.write(remote_file.read())
    file.close()
    remote_file.close()


def get_store_list():
    """Returns the store list"""
    file = open(LIST_PATH, 'r')

    try:
        store_list = json.load(file)

    finally:
        file.close()

    return store_list


def get_icon(activity_id):
    """Get the icon of an specified activity"""
    store_list = get_store_list()
    activity_obj = store_list[activity_id]

    url = activity_obj["Icon"]
    file = "%s/icon%s" % (TMP_DIR, time.time())

    fileimage, headers = urllib.urlretrieve(url, file)
    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(fileimage, 45, 45)

    return pixbuf


def download_activity(id, progress_function):
    """Download (and install) an activity"""
    store_list = get_store_list()
    activity_obj = store_list[id]

    def progress_changed(block, block_size, total_size):
        downloaded = block * block_size
        progress = downloaded * 100 / total_size

        progress_function(progress)

    xo = '%s.xo' % activity_obj['Name'].replace('=', '')
    file_path = os.path.join(activity.get_activity_root(), "data", "%s" % (xo))

    _logger.info("Downloading activity (%s)")
    urllib.urlretrieve(activity_obj['Download'],
                       file_path,
                       reporthook=progress_changed)

    _logger.info("Installing activity (%s)")
    install_activity(file_path, progress_function)


def install_activity(xofile, progress_function):
    """Install an downloaded activity"""
    # Show "Installing..." message
    progress_function(150)

    # Install the .xo
    bundle = ActivityBundle(xofile)
    bundle.install()

    # Remove the .xo
    os.remove(xofile)

    # Show "Installed..." message
    progress_function(200)

    _logger.info("Activity installed! (%s)")
