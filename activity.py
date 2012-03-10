#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import gtk

from sugar.activity import activity
from sugar.activity.widgets import ActivityToolbarButton
from sugar.activity.widgets import StopButton
from sugar.graphics.toolbarbox import ToolbarBox


class ActivitiesStore(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle, True)

        # Toolbars
        toolbarbox = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbarbox.toolbar.insert(activity_button, 0)

        separator = gtk.SeparatorToolItem()
        separator.set_draw(False)
        separator.set_expand(True)
        toolbarbox.toolbar.insert(separator, -1)

        stopbtn = StopButton(self)
        toolbarbox.toolbar.insert(stopbtn, -1)

        self.set_toolbar_box(toolbarbox)
        self.show_all()
