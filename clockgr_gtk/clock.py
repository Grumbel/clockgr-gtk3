# clockgr - A fullscreen clock for Gtk+
# Copyright (C) 2012,2018 Ingo Ruhnke <grumbel@gmail.com>
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


from __future__ import print_function

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

import sys

from datetime import datetime

from clockgr_gtk.style import Style
from clockgr_gtk.desklets.digital_clock import DigitalClock
from clockgr_gtk.desklets.analog_clock import AnalogClock
from clockgr_gtk.desklets.world import WorldDesklet
from clockgr_gtk.desklets.calendar import CalendarDesklet
from clockgr_gtk.desklets.stop_watch import StopWatch


def is_olpc():
    try:
        with open("/etc/fedora-release") as f:
            content = f.read()
        return content[0:4] == "OLPC"
    except IOError:
        return False


class ClockWidget(Gtk.DrawingArea):

    def __init__(self, renderer):
        Gtk.DrawingArea.__init__(self)
        self.renderer = renderer
        self.renderer.set_parent(self)
        self.connect("draw", self.do_draw_event)

    def do_draw_event(self, widget, cr):
        self.renderer.draw(cr, 1680, 1050)


class ClockMode:
    calendar = 1
    stopwatch = 2


class ClockRenderer(object):

    def __init__(self):
        self.parent = None
        self.my_style = Style()
        self.desklets = []
        self.active_desklets = []

        self.digital_clock = self.add_desklet(DigitalClock(), (32, 670, 640, 200))
        self.analog_clock = self.add_desklet(AnalogClock(), (900 - 256, 32, 512, 512))
        self.calendar = self.add_desklet(CalendarDesklet(), (32, 32, 512, 412))
        self.world = self.add_desklet(WorldDesklet(), (1200 - 540 - 32, 900 - 276 - 32, 540, 276))
        self.stopwatch = self.add_desklet(StopWatch(), (32, 64, 500, 180))

        self.mode = ClockMode.calendar
        self.apply_mode()

    def next_mode(self):
        print(self.mode)

        if self.mode == ClockMode.calendar:
            self.mode = ClockMode.stopwatch
        else:
            self.mode = ClockMode.calendar

        self.apply_mode()
        self.queue_draw()

    def apply_mode(self):
        if self.mode == ClockMode.calendar:
            self.active_desklets = [d for d in self.desklets if d != self.stopwatch]
        elif self.mode == ClockMode.stopwatch:
            self.active_desklets = [d for d in self.desklets if d != self.calendar]

    def add_desklet(self, desklet, rect):
        desklet.set_parent(self)
        desklet.set_style(self.my_style)
        desklet.set_rect(*rect)
        self.desklets.append(desklet)
        return desklet

    def set_parent(self, parent):
        self.parent = parent

    def queue_draw_area(self, x, y, width, height):
        if self.parent:
            self.parent.queue_draw_area(x, y, width, height)

    def queue_draw(self):
        if self.parent:
            self.parent.queue_draw()
        else:
            root = Gtk.gdk.get_default_root_window()
            rect = root.get_frame_extents()
            root.invalidate_rect(rect, False)
            cr = root.cairo_create()
            self.draw(cr, rect.width, rect.height)

    def draw(self, cr, width, height):
        # Fill the background with gray
        cr.set_source_rgb(*self.my_style.background_color)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        now = datetime.now()

        for desklet in self.active_desklets:
            desklet.draw(cr, now)

    def update(self):
        self.queue_draw()
        return True

    def invert(self):
        (self.my_style.background_color,
         self.my_style.foreground_color) = (self.my_style.foreground_color,
                                            self.my_style.background_color)
        self.queue_draw()


def realize_cb(widget):
    print("realize_cb")
    pixmap = Gtk.gdk.Pixmap(None, 1, 1, 1)
    color = Gtk.gdk.Color()
    cursor = Gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)
    widget.window.set_cursor(cursor)


def main(argv):
    import argparse

    parser = argparse.ArgumentParser(description='ClockGr - A toy clock application')
    parser.add_argument('--root-window', action='store_true', help='Display the clock on the root window')
    args = parser.parse_args()

    use_root_window = args.root_window

    if use_root_window:
        renderer = ClockRenderer()
        renderer.invert()
        GObject.timeout_add(1000, renderer.update)
    else:
        renderer = ClockRenderer()
        widget = ClockWidget(renderer)
        window = Gtk.Window()
        window.set_title("ClockGr")
        widget.show()
        window.add(widget)
        window.present()

        window.set_default_size(1200, 900)
        if is_olpc():
            window.fullscreen()

        accelgroup = Gtk.AccelGroup()

        key, modifier = Gtk.accelerator_parse('Escape')
        accelgroup.connect(key,
                           modifier,
                           Gtk.AccelFlags.VISIBLE,
                           Gtk.main_quit)
        key, modifier = Gtk.accelerator_parse('f')
        accelgroup.connect(key,
                           modifier,
                           Gtk.AccelFlags.VISIBLE,
                           lambda *args: window.fullscreen())
        key, modifier = Gtk.accelerator_parse('space')
        accelgroup.connect(key,
                           modifier,
                           Gtk.AccelFlags.VISIBLE,
                           lambda *args: renderer.stopwatch.start_stop_watch())
        key, modifier = Gtk.accelerator_parse('Return')
        accelgroup.connect(key,
                           modifier,
                           Gtk.AccelFlags.VISIBLE,
                           lambda *args: renderer.stopwatch.clear_stop_watch())

        key, modifier = Gtk.accelerator_parse('1')
        accelgroup.connect(key,
                           modifier,
                           Gtk.AccelFlags.VISIBLE,
                           lambda *args: renderer.calendar.previous_month())
        key, modifier = Gtk.accelerator_parse('2')
        accelgroup.connect(key,
                           modifier,
                           Gtk.AccelFlags.VISIBLE,
                           lambda *args: renderer.calendar.next_month())

        key, modifier = Gtk.accelerator_parse('i')
        accelgroup.connect(key,
                           modifier,
                           Gtk.AccelFlags.VISIBLE,
                           lambda *args: renderer.invert())

        key, modifier = Gtk.accelerator_parse('m')
        accelgroup.connect(key,
                           modifier,
                           Gtk.AccelFlags.VISIBLE,
                           lambda *args: renderer.next_mode())

        window.add_accel_group(accelgroup)

        window.set_size_request(1200, 900)
        window.connect("delete-event", Gtk.main_quit)
        window.connect("realize", realize_cb)

        GObject.timeout_add(1000, renderer.update)

    Gtk.main()


def main_entrypoint():
    main(sys.argv)


# EOF #
