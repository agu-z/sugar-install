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
import urllib
import logging

from sugar.activity import activity
from sugar.bundle.activitybundle import ActivityBundle

# Paths
LIST_DOWNLOAD = "http://www.fing.edu.uy/~aaguiar/files/store.lst"
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
    _file = open(LIST_PATH, 'w')
    _file.write(remote_file.read())
    _file.close()
    remote_file.close()


def get_store_list():
    """Returns the store list"""
    f = open(LIST_PATH, 'r')

    store_list = []
    e = True
    while e:
        line = f.readline()
        if not(line):
            e = False
        else:
            line = line.replace('\n', '')
            l = line.split('|')
            store_list.append(l)

    return store_list


def get_icon(activity_id):
    """Returns the icon of an specified activity"""
    store_list = get_store_list()
    activity_obj = store_list[activity_id]
    number = activity_obj[0]

    file_image = os.path.join(TMP_DIR, "icon%s" % number)
    if not os.path.exists(file_image):
        url =\
      'http://activities.sugarlabs.org/en-US/sugar/images/addon_icon/' + number
        f, headers = urllib.urlretrieve(url, file_image)

    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(file_image, 45, 45)

    return pixbuf


def download_activity(id, progress_function):
    """Download (and install) an activity"""
    store_list = get_store_list()
    activity_obj = store_list[id]

    name = activity_obj[1]
    name = name.lower()
    name = name.replace(' ', '_')
    n = activity_obj[0]
    web = 'http://activities.sugarlabs.org/es-ES/sugar/downloads/latest/'
    web = web + n + '/addon-' + n + '-latest.xo'
    version = activity_obj[3]

    def progress_changed(block, block_size, total_size):
        downloaded = block * block_size
        progress = downloaded * 100 / total_size

        progress_function(progress)

    xo = name + '-' + version + '.xo'
    file_path = os.path.join(activity.get_activity_root(), "data", xo)

    _logger.info("Downloading activity (%s)")
    urllib.urlretrieve(web,
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
