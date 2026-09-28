#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
import pygame

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ToolButton

from gettext import gettext as _

import sugargame.canvas

import jump

class JumpActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.sound_enable = True

        self.game = jump.SolitaireMain()
        self.build_toolbar()
        self.game.on_level_changed = self.sync_level_selector

        self.game.canvas = self._pygamecanvas = \
            sugargame.canvas.PygameCanvas(self,
                main=self.game.SuperLooper,
                modules=[pygame.display, pygame.font, pygame.mixer])

        self.set_canvas(self._pygamecanvas)
        self._pygamecanvas.grab_focus()

    def build_toolbar(self):
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        separator1 = Gtk.SeparatorToolItem()
        separator1.props.draw = True
        separator1.set_expand(False)
        toolbar_box.toolbar.insert(separator1, -1)
        separator1.show()

        item1 = Gtk.ToolItem()
        label1 = Gtk.Label()
        label1.set_text(_('Levels') + ' ')
        item1.add(label1)
        toolbar_box.toolbar.insert(item1, -1)

        item2 = Gtk.ToolItem()

        levels = (_('Cross'),
            _('Cross 2'),
            #TRANS:'chimney' - the place where you make fire
            _('Hearth'),
            _('Arrow'),
            _('Pyramid'),
            _('Diamond'),
            _('Solitaire'))
        combo = Combo(levels)
        item2.add(combo)
        self.level_combo = combo
        self.level_combo_handler = combo.connect('changed', self.change_combo)
        toolbar_box.toolbar.insert(item2, -1)

        separator2 = Gtk.SeparatorToolItem()
        separator2.props.draw = True
        separator2.set_expand(False)
        toolbar_box.toolbar.insert(separator2, -1)
        separator2.show()

        sound_button = ToolButton('speaker-muted-100')
        sound_button.set_tooltip(_('Sound'))
        sound_button.connect('clicked', self.sound_control)
        toolbar_box.toolbar.insert(sound_button, -1)

        separator3 = Gtk.SeparatorToolItem()
        separator3.props.draw = False
        separator3.set_expand(True)
        toolbar_box.toolbar.insert(separator3, -1)
        separator3.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.show_all()

    def change_combo(self, combo):
        level = combo.get_active()
        if level >= 0 and level != self.game.actual_level:
            self.game.change_level(level)

    def sync_level_selector(self, level):
        # Updating the toolbar must not reset the board a second time.
        self.level_combo.handler_block(self.level_combo_handler)
        try:
            self.level_combo.set_active(level)
        finally:
            self.level_combo.handler_unblock(self.level_combo_handler)

    def sound_control(self, button):
        self.sound_enable = not self.sound_enable
        self.game.change_sound(self.sound_enable)
        if not self.sound_enable:
            button.set_icon_name('speaker-muted-000')
            button.set_tooltip(_('No sound'))
        else:
            button.set_icon_name('speaker-muted-100')
            button.set_tooltip(_('Sound'))


class Combo(Gtk.ComboBox):

    def __init__(self, options):

        self.liststore = Gtk.ListStore(str)

        for o in options:
            self.liststore.append([o])

        Gtk.ComboBox.__init__(self)
        self.set_model(self.liststore)
        cell = Gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

        self.set_active(0)

