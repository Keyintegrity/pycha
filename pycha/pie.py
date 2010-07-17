# Copyright(c) 2007-2009 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of PyCha.
#
# PyCha is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyCha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PyCha.  If not, see <http://www.gnu.org/licenses/>.

import math

import cairo

from pycha.chart import Chart, Option, Layout, Area, get_text_extents
from pycha.color import hex2rgb


class PieChart(Chart):

    def __init__(self, surface=None, options={}):
        super(PieChart, self).__init__(surface, options)
        self.slices = []
        self.centerx = 0
        self.centery = 0
        self.layout = PieLayout(self.slices)

    def _updateChart(self):
        """Evaluates measures for pie charts"""
        slices = [dict(name=key,
                       value=(i, value[0][1]))
                  for i, (key, value) in enumerate(self.datasets)]

        s = float(sum([slice['value'][1] for slice in slices]))

        fraction = angle = 0.0

        del self.slices[:]
        for slice in slices:
            if slice['value'][1] > 0:
                angle += fraction
                fraction = slice['value'][1] / s
                self.slices.append(Slice(slice['name'], fraction,
                                         slice['value'][0], slice['value'][1],
                                         angle))

    def _updateTicks(self):
        """Evaluates pie ticks"""
        self.xticks = []
        if self.options.axis.x.ticks:
            lookup = dict([(slice.xval, slice) for slice in self.slices])
            for tick in self.options.axis.x.ticks:
                if not isinstance(tick, Option):
                    tick = Option(tick)
                slice = lookup.get(tick.v, None)
                label = tick.label or str(tick.v)
                if slice is not None:
                    label += ' (%.1f%%)' % (slice.fraction * 100)
                    self.xticks.append((tick.v, label))
        else:
            for slice in self.slices:
                label = '%s (%.1f%%)' % (slice.name, slice.fraction * 100)
                self.xticks.append((slice.xval, label))

    def _renderLines(self, cx):
        """Aux function for _renderBackground"""
        # there are no lines in a Pie Chart

    def _renderChart(self, cx):
        """Renders a pie chart"""
        self.centerx = self.layout.chart.x + self.layout.chart.w * 0.5
        self.centery = self.layout.chart.y + self.layout.chart.h * 0.5

        if self.debug:
            cx.set_source_rgba(1, 0, 0, 0.5)
            px = max(cx.device_to_user_distance(1, 1))
            for x, y in self.layout._lines:
                cx.arc(x, y, 5 * px, 0, 2 * math.pi)
                cx.fill()
                cx.new_path()
                cx.move_to(self.centerx, self.centery)
                cx.line_to(x, y)
                cx.stroke()

        cx.set_line_join(cairo.LINE_JOIN_ROUND)

        if self.options.stroke.shadow and False:
            cx.save()
            cx.set_source_rgba(0, 0, 0, 0.15)

            cx.new_path()
            cx.move_to(self.centerx, self.centery)
            cx.arc(self.centerx + 1, self.centery + 2, self.layout.radius + 1, 0,
                   math.pi * 2)
            cx.line_to(self.centerx, self.centery)
            cx.close_path()
            cx.fill()
            cx.restore()

        cx.save()
        for slice in self.slices:
            if slice.isBigEnough():
                cx.set_source_rgb(*self.colorScheme[slice.name])
                if self.options.shouldFill:
                    slice.draw(cx, self.centerx, self.centery, self.layout.radius)
                    cx.fill()

                if not self.options.stroke.hide:
                    slice.draw(cx, self.centerx, self.centery, self.layout.radius)
                    cx.set_line_width(self.options.stroke.width)
                    cx.set_source_rgb(*hex2rgb(self.options.stroke.color))
                    cx.stroke()

        cx.restore()

    def _renderAxis(self, cx):
        """Renders the axis for pie charts"""
        if self.options.axis.x.hide or not self.xticks:
            return

        self.xlabels = []

        if self.debug:
            px = max(cx.device_to_user_distance(1, 1))
            cx.set_source_rgba(0, 0, 1, 0.5)
            for x, y, w, h in self.layout.ticks:
                cx.rectangle(x, y, w, h)
                cx.stroke()
                cx.arc(x + w/2.0, y + h/2.0, 5 * px, 0, 2 * math.pi)
                cx.fill()

        cx.select_font_face(self.options.axis.tickFont,
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        cx.set_font_size(self.options.axis.tickFontSize)

        cx.set_source_rgb(*hex2rgb(self.options.axis.labelColor))

        for i, tick in enumerate(self.xticks):
            label = tick[1]
            x, y, w, h = self.layout.ticks[i]

            xb, yb, width, height, xa, ya = cx.text_extents(label)

            # draw label with text tick[1]
            cx.move_to(x - xb, y - yb)
            cx.show_text(label)
            self.xlabels.append(label)


class Slice(object):

    def __init__(self, name, fraction, xval, yval, angle):
        self.name = name
        self.fraction = fraction
        self.xval = xval
        self.yval = yval
        self.startAngle = 2 * angle * math.pi
        self.endAngle = 2 * (angle + fraction) * math.pi

    def __str__(self):
        return ("<pycha.pie.Slice from %.2f to %.2f (%.2f%%)>" %
                (self.startAngle, self.endAngle, self.fraction))

    def isBigEnough(self):
        return abs(self.startAngle - self.endAngle) > 0.001

    def draw(self, cx, centerx, centery, radius):
        cx.new_path()
        cx.move_to(centerx, centery)
        cx.arc(centerx, centery, radius, -self.endAngle, -self.startAngle)
        cx.close_path()

    def getNormalisedAngle(self):
        normalisedAngle = (self.startAngle + self.endAngle) / 2

        if normalisedAngle > math.pi * 2:
            normalisedAngle -= math.pi * 2
        elif normalisedAngle < 0:
            normalisedAngle += math.pi * 2

        return normalisedAngle


class PieLayout(Layout):
    """Set of chart areas for pie charts"""

    def __init__(self, slices):
        self.slices = slices

        self.title = Area()
        self.chart = Area()

        self.ticks = []
        self.radius = 0

        self._areas = (
            (self.title, (1, 126/255.0, 0)), # orange
            (self.chart, (75/255.0, 75/255.0, 1.0)), # blue
            )

        self._lines = []

    def update(self, cx, options, width, height, xticks, yticks):
        self.title.x = options.padding.left
        self.title.y = options.padding.top
        self.title.w = width - (options.padding.left + options.padding.right)
        self.title.h = get_text_extents(cx,
                                        options.title,
                                        options.titleFont,
                                        options.titleFontSize,
                                        options.encoding)[1]

        lookup = dict([(slice.xval, slice) for slice in self.slices])

        self.chart.x = self.title.x
        self.chart.y = self.title.y + self.title.h
        self.chart.w = self.title.w
        self.chart.h = height - self.title.h - (options.padding.top
                                                + options.padding.bottom)

        self.radius = min(self.chart.w / 2.0, self.chart.h / 2.0)
        for tick in xticks:
            slice = lookup.get(tick[0], None)
            self.radius = min(self.radius,
                              self.get_min_radius(cx, options, tick[1], slice))


    def get_min_radius(self, cx, options, text, slice):
        centerx = self.chart.x + self.chart.w * 0.5
        centery = self.chart.y + self.chart.h * 0.5

        w, h = get_text_extents(cx, text,
                                options.axis.tickFont,
                                options.axis.tickFontSize,
                                options.encoding)

        min_radius = None

        # computes the intersection between the rect that has
        # that angle with the X axis and the bounding chart box
        angle = slice.getNormalisedAngle()
        if 0.25 * math.pi <= angle < 0.75 * math.pi:
            # intersects with the top rect
            y = self.chart.y
            x = centerx + (centery - y) / math.tan(angle)
            self._lines.append((x, y))

            x1 = x - w / 2.0 - ((h / 2.0) / math.tan(angle))
            self.ticks.append((x1, self.chart.y, w, h))

            min_radius = abs((y + h) - centery)
        elif 0.75 * math.pi <= angle < 1.25 * math.pi:
            # intersects with the left rect
            x = self.chart.x
            y = math.tan(angle) * (x - centerx) + centery
            y = self.chart.y + self.chart.h - y
            self._lines.append((x, y))

            y1 = y - h / 4.0 - ((w / 2.0) * math.tan(angle))
            self.ticks.append((x, y1, w, h))

            min_radius = abs(centerx - (x + w))
        elif 1.25 * math.pi <= angle < 1.75 * math.pi:
            # intersects with the down rect
            y = self.chart.y + self.chart.h
            x = centerx + (y - centery) / math.tan(angle)
            self._lines.append((x, y))

            x1 = x - w / 2.0 - ((h / 2.0) / math.tan(angle))
            self.ticks.append((x1, y - h, w, h))

            min_radius = abs((y - h) - centery)
        else:
            # intersects with the right rect
            x = self.chart.x + self.chart.w
            y = math.tan(angle) * (x - centerx) + centery
            y = self.chart.y + self.chart.h - y
            self._lines.append((x, y))

            y1 = y - h / 4.0 + ((w / 2.0) * math.tan(angle))
            self.ticks.append((x - w, y1, w, h))

            min_radius = abs((x - w) - centerx)

        return min_radius
