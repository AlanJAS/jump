#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jump
# Copyright (C) 2008, Joshua Seaver, Bimal Sadhwani, Natalie Rusk
# Copyright (C) 2012, 2013, Alan Aguiar
# Based on the original code in Logo of Natalie Rusk.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# Alan Aguiar alanjas@hotmail.com

import os
import random
from gettext import gettext as _

import pygame

gtk_present = True
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except (ImportError, ValueError):
    gtk_present = False

from levels import LEVELS
from model import Board
from rules import CELL_SIZE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
FPS = 30
BROWN_COLOR = (88, 47, 27)
# The original artwork places the sprite slightly outside the logical cell.
SPRITE_ORIGIN = (292, 106)


def load_image(name, colorkey=None):
    image = pygame.image.load(os.path.join(DATA_DIR, name)).convert()
    if colorkey is not None:
        image.set_colorkey(colorkey)
    return image


class NoneSound:
    def play(self):
        pass


def load_sound(name):
    try:
        return pygame.mixer.Sound(os.path.join(DATA_DIR, name))
    except pygame.error:
        return NoneSound()


class Button:
    """Preloaded button artwork; hovering never reloads files or state."""

    def __init__(self, position, normal, hover):
        self.image = load_image(normal)
        self.hover_image = load_image(hover)
        self.rect = self.image.get_rect(topleft=position)
        self.pressed = False

    def draw(self, screen, position):
        if self.rect.collidepoint(position):
            screen.blit(self.hover_image, self.rect)
        else:
            screen.blit(self.image, self.rect)


class SolitaireMain:
    """Input and rendering controller. Board owns all game rules and state."""

    def __init__(self, width=1200, height=825):
        self.width, self.height = width, height
        self.actual_level = 0
        self.on_level_changed = None
        self.sound_enable = True
        self.clock = pygame.time.Clock()
        self.screen = None
        self.assets_loaded = False
        self.running = True
        self.reset_board()

    def change_sound(self, sound):
        self.sound_enable = bool(sound)

    def play_sound(self, sound):
        if self.sound_enable:
            sound.play()

    def reset_board(self, level=None):
        previous_level = self.actual_level
        if level is not None:
            self.actual_level = level
        self.board = Board(LEVELS[self.actual_level], random.randrange(23))
        self.selected = None
        self.completion_pressed = False
        self.help_visible = False
        self.played_milestones = set()
        self.update_moves()
        if self.assets_loaded:
            self.new_button.pressed = self.help_button.pressed = False
        if self.actual_level != previous_level and self.on_level_changed is not None:
            self.on_level_changed(self.actual_level)

    def change_level(self, level):
        # Sugar calls this while GTK events are pumped by the existing loop
        self.reset_board(level)

    def increase_level(self):
        self.change_level((self.actual_level + 1) % len(LEVELS))

    def update_moves(self):
        self.updated_text = self.board.marble_count()
        self.updated_moves = self.board.move_count()
        self.game_over = self.updated_moves == 0
        self.level_completed = self.updated_text == 1

    def load_things(self):
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(_('Jump'))
        self.background = load_image('Background2.png')
        self.helpscreen = load_image('Instructions.png')
        self.font = pygame.font.Font(None, 50)
        self.marble_images = [load_image('%d.png' % i, (0, 0, 0))
                              for i in range(23)]
        self.special_marbles = [load_image(f'S{i}.png')
                              for i in range(1, 37)]
        self.flags = [load_image('Flag%02d.png' % i) for i in range(1, 8)]
        self.target_image = load_image('S1.png')
        self.level_sounds = [load_sound('%d.ogg' % i) for i in range(8)]
        self.move_sound = load_sound('drop.ogg')
        self.picked_sound = load_sound('pop1.ogg')
        self.new_sound = load_sound('newboard.ogg')
        self.new_button = Button((31, 614), 'NewBoard.png', 'NewBoardOn.png')
        self.help_button = Button((970, 614), 'HelpOff.png', 'HelpOn.png')
        self.overlay = pygame.Surface(self.background.get_size())
        self.overlay.fill((100, 100, 100))
        self.overlay.set_alpha(200)
        self.assets_loaded = True

    def pick_marble(self, position):
        if self.game_over or self.help_visible or self.selected is not None:
            return
        cell = self.board.cell_at(position)
        if self.board.has_marble(cell):
            self.selected = cell
            self.play_sound(self.picked_sound)

    def drop_marble(self, position):
        start, self.selected = self.selected, None
        if start is None:
            return False
        moved = self.board.move(start, self.board.cell_at(position))
        if moved:
            self.play_sound(self.move_sound)
            self.update_moves()
            self.play_progress_sound()
        return moved

    def play_progress_sound(self):
        thresholds = (28, 24, 20, 16, 12, 8, 4, 1)
        remaining = self.board.marble_count()
        if remaining in thresholds and remaining not in self.played_milestones:
            self.play_sound(self.level_sounds[thresholds.index(remaining)])
            self.played_milestones.add(remaining)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            return
        if self.level_completed:
            self.handle_completion_event(event)
            return
        if self.help_visible:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.help_visible = False
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.selected is not None:
                self.selected = None
            else:
                self.running = False
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in (self.new_button, self.help_button):
                if button.rect.collidepoint(event.pos):
                    button.pressed = True
                    return
            self.pick_marble(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            new_board = (self.new_button.pressed and
                         self.new_button.rect.collidepoint(event.pos))
            show_help = (self.help_button.pressed and
                         self.help_button.rect.collidepoint(event.pos))
            self.new_button.pressed = self.help_button.pressed = False
            if new_board:
                self.reset_board()
                self.play_sound(self.new_sound)
            elif show_help:
                self.selected = None
                self.help_visible = True
            else:
                self.drop_marble(event.pos)

    def completion_rects(self):
        panel = pygame.Rect(0, 0, min(700, self.screen.get_width() - 40), 300)
        panel.center = self.screen.get_rect().center
        button = pygame.Rect(0, 0, min(420, panel.width - 40), 64)
        button.midbottom = (panel.centerx, panel.bottom - 30)
        return panel, button

    def continue_after_completion(self):
        if not self.level_completed:
            return
        # On the final level, the button explicitly offers a new game.
        self.increase_level()
        self.play_sound(self.new_sound)

    def handle_completion_event(self, event):
        _, button = self.completion_rects()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.continue_after_completion()
            elif event.key == pygame.K_ESCAPE:
                self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.completion_pressed = button.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            activate = self.completion_pressed and button.collidepoint(event.pos)
            self.completion_pressed = False
            if activate:
                self.continue_after_completion()

    def draw_completion(self):
        panel, button = self.completion_rects()
        pygame.draw.rect(self.screen, (250, 232, 196), panel, border_radius=18)
        pygame.draw.rect(self.screen, BROWN_COLOR, panel, 3, border_radius=18)
        last_level = self.actual_level == len(LEVELS) - 1
        title = (_('Final level completed!') if last_level else
                 _('Level %d completed!') % (self.actual_level + 1))
        label = _('Play again') if last_level else _('Next level')
        hovered = button.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, (115, 64, 34) if hovered else BROWN_COLOR,
                         button, border_radius=12)
        lines = ((title, panel.top + 65, BROWN_COLOR),
                 (_('Well done!'), panel.top + 120, BROWN_COLOR),
                 (label, button.centery, (255, 245, 225)))
        for text, y, color in lines:
            surface = self.font.render(text, True, color)
            max_width = button.width - 24 if y == button.centery else panel.width - 40
            if surface.get_width() > max_width:
                ratio = max_width / surface.get_width()
                surface = pygame.transform.smoothscale(
                    surface, (max_width, max(1, int(surface.get_height() * ratio))))
            self.screen.blit(surface, surface.get_rect(center=(panel.centerx, y)))

    def marble_rect(self, cell):
        """Use the same artwork geometry for marbles and destination hints."""
        row, column = cell
        return self.marble_images[self.board.color].get_rect(
            topleft=(SPRITE_ORIGIN[0] + column * CELL_SIZE,
                     SPRITE_ORIGIN[1] + row * CELL_SIZE))

    def draw_marble(self, cell, position=None):
        image = self.marble_images[self.board.color]
        if position is None:
            rect = self.marble_rect(cell)
        else:
            rect = image.get_rect(center=position)
        self.screen.blit(image, rect)

    def draw(self):
        position = pygame.mouse.get_pos()
        self.screen.fill(BROWN_COLOR)
        self.screen.blit(self.background, (0, 0))
        for cell in self.board.marbles():
            if cell != self.selected:
                self.draw_marble(cell)
        if self.selected is not None:
            # Legal targets are derived from exactly the same rules as dropping.
            for start, end in self.board.legal_moves():
                if start == self.selected:
                    center = self.marble_rect(end).center
                    pygame.draw.circle(self.screen, BROWN_COLOR, center, 24, 3)
            self.draw_marble(self.selected, position)
        remaining = self.board.marble_count()
        for index, threshold in enumerate((28, 24, 20, 16, 12, 8, 4)):
            if threshold - 4 < remaining <= threshold:
                self.screen.blit(self.flags[index], (1038, 110))
                break
        self.screen.blit(self.target_image, (1067, 45))
        self.screen.blit(self.font.render(str(remaining), True, BROWN_COLOR),
                         (1000, 50))
        if self.game_over and not self.level_completed:
            self.screen.blit(self.overlay, (0, 0))
        self.new_button.draw(self.screen, position)
        self.help_button.draw(self.screen, position)
        if self.help_visible:
            self.screen.blit(self.overlay, (0, 0))
            self.screen.blit(self.helpscreen, (0, 0))
        if self.level_completed:
            self.screen.blit(self.overlay, (0, 0))
            self.draw_completion()

    def SuperLooper(self):
        """Big loop"""
        self.load_things()
        self.running = True
        try:
            while self.running:
                if gtk_present:
                    while Gtk.events_pending():
                        Gtk.main_iteration()
                for event in pygame.event.get():
                    self.handle_event(event)
                    if not self.running:
                        break
                if self.running:
                    self.draw()
                    pygame.display.flip()
                    self.clock.tick(FPS)
        finally:
            self.running = False
        return False


def main():
    pygame.init()
    try:
        SolitaireMain().SuperLooper()
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
