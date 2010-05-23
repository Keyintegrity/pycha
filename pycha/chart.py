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

import copy
import inspect
import math

import cairo

from pycha.color import ColorScheme, hex2rgb, DEFAULT_COLOR
from pycha.utils import safe_unicode


class Chart(object):

    def __init__(self, surface, options={}):
        # this flag is useful to reuse this chart for drawing different data
        # or use different options
        self.resetFlag = False

        # initialize storage
        self.datasets = []

        # computed values used in several methods
        self.area = None # chart area without padding or text labels
        self.minxval = None
        self.maxxval = None
        self.minyval = None
        self.maxyval = None
        self.xscale = 1.0
        self.yscale = 1.0
        self.xrange = None
        self.yrange = None
        self.origin = 0.0

        self.xticks = []
        self.yticks = []

        # set the default options
        self.options = copy.deepcopy(DEFAULT_OPTIONS)
        if options:
            self.options.merge(options)

        # initialize the surface
        self._initSurface(surface)

        self.colorScheme = None

    def addDataset(self, dataset):
        """Adds an object containing chart data to the storage hash"""
        self.datasets += dataset

    def _getDatasetsKeys(self):
        """Return the name of each data set"""
        return [d[0] for d in self.datasets]

    def _getDatasetsValues(self):
        """Return the data (value) of each data set"""
        return [d[1] for d in self.datasets]

    def setOptions(self, options={}):
        """Sets options of this chart"""
        self.options.merge(options)

    def getSurfaceSize(self):
        cx = cairo.Context(self.surface)
        x, y, w, h = cx.clip_extents()
        return w, h

    def reset(self):
        """Resets options and datasets.

        In the next render the surface will be cleaned before any drawing.
        """
        self.resetFlag = True
        self.options = copy.deepcopy(DEFAULT_OPTIONS)
        self.datasets = []

    def render(self, surface=None, options={}):
        """Renders the chart with the specified options.

        The optional parameters can be used to render a chart in a different
        surface with new options.
        """
        self._update(options)
        if surface:
            self._initSurface(surface)

        cx = cairo.Context(self.surface)

        # calculate area data
        surface_width, surface_height = self.getSurfaceSize()
        width = (surface_width
                 - self.options.padding.left - self.options.padding.right)
        height = (surface_height
                  - self.options.padding.top - self.options.padding.bottom)

        self.title_area = Area(self.options.padding.left,
                               self.options.padding.top,
                               surface_width - (self.options.padding.left
                                                + self.options.padding.right),
                               self._getTitleHeight(cx))

        y_axis_label_width = self._getYAxisLabelWidth(cx)
        x_axis_label_height = self._getXAxisLabelHeight(cx)
        y_axis_tick_labels_width = self._getYAxisTickLabelsWidth(cx)
        x_axis_tick_labels_height = self._getXAxisTickLabelsHeight(cx)

        self.y_label_area = Area(self.options.padding.left,
                                 self.options.padding.top + self.title_area.h,
                                 y_axis_label_width,
                                 surface_height - (self.options.padding.bottom
                                                   + self.options.padding.top
                                                   + x_axis_label_height
                                                   + x_axis_tick_labels_height
                                                   + self.options.axis.tickSize
                                                   + self.title_area.h))
        self.x_label_area = Area(self.options.padding.left
                                 + y_axis_label_width
                                 + y_axis_tick_labels_width
                                 + self.options.axis.tickSize,
                                 surface_height - (self.options.padding.bottom
                                                   + x_axis_label_height),
                                 surface_width - (self.options.padding.left
                                                  + self.options.padding.right
                                                  + self.options.axis.tickSize
                                                  + y_axis_label_width
                                                  + y_axis_tick_labels_width),
                                 x_axis_label_height)

        self.y_tick_labels_area = Area(self.y_label_area.x
                                       + self.y_label_area.w,
                                       self.y_label_area.y,
                                       y_axis_tick_labels_width,
                                       self.y_label_area.h)
        self.x_tick_labels_area = Area(self.x_label_area.x,
                                       self.x_label_area.y
                                       - x_axis_tick_labels_height,
                                       self.x_label_area.w,
                                       x_axis_tick_labels_height)

        self.y_ticks_area = Area(self.y_tick_labels_area.x
                                 + self.y_tick_labels_area.w,
                                 self.y_tick_labels_area.y,
                                 self.options.axis.tickSize,
                                 self.y_label_area.h)
        self.x_ticks_area = Area(self.x_tick_labels_area.x,
                                 self.x_tick_labels_area.y
                                 - self.options.axis.tickSize,
                                 self.x_label_area.w,
                                 self.options.axis.tickSize)
        self.chart_area = Area(self.y_ticks_area.x + self.y_ticks_area.w,
                               self.title_area.y + self.title_area.h,
                               self.x_ticks_area.w,
                               self.y_ticks_area.h)

        self.area = Area(self.options.padding.left, self.options.padding.top,
                         width, height)

        self._renderBackground(cx)

        def draw_area(area, r, g, b):
            cx.rectangle(area.x, area.y, area.w, area.h)
            cx.set_source_rgba(r, g, b, 0.5)
            cx.fill()

        cx.save()
        draw_area(self.title_area, 1, 126/255.0, 0)
        draw_area(self.y_label_area, 41/255.0, 91/255.0, 41/255.0)
        draw_area(self.x_label_area, 41/255.0, 91/255.0, 41/255.0)
        draw_area(self.y_tick_labels_area, 0, 115/255.0, 0)
        draw_area(self.x_tick_labels_area, 0, 115/255.0, 0)
        draw_area(self.y_ticks_area, 229/255.0, 241/255.0, 18/255.0)
        draw_area(self.x_ticks_area, 229/255.0, 241/255.0, 18/255.0)
        draw_area(self.chart_area, 75/255.0, 75/255.0, 1.0)
        cx.restore()

        self._renderChart(cx)
        self._renderAxis(cx)
        self._renderTitle(cx)
        self._renderLegend(cx)

    def clean(self):
        """Clears the surface with a white background."""
        cx = cairo.Context(self.surface)
        cx.save()
        cx.set_source_rgb(1, 1, 1)
        cx.paint()
        cx.restore()

    def _setColorscheme(self):
        """Sets the colorScheme used for the chart using the
        options.colorScheme option
        """
        name = self.options.colorScheme.name
        keys = self._getDatasetsKeys()
        colorSchemeClass = ColorScheme.getColorScheme(name, None)
        if colorSchemeClass is None:
            raise ValueError('Color scheme "%s" is invalid!' % name)

        # Remove invalid args before calling the constructor
        kwargs = dict(self.options.colorScheme.args)
        validArgs = inspect.getargspec(colorSchemeClass.__init__)[0]
        kwargs = dict([(k, v) for k, v in kwargs.items() if k in validArgs])
        self.colorScheme = colorSchemeClass(keys, **kwargs)

    def _initSurface(self, surface):
        self.surface = surface

        if self.resetFlag:
            self.resetFlag = False
            self.clean()

    def _update(self, options={}):
        """Update all the information needed to render the chart"""
        self.setOptions(options)
        self._setColorscheme()
        self._updateXY()
        self._updateChart()
        self._updateTicks()

    def _updateXY(self):
        """Calculates all kinds of metrics for the x and y axis"""
        x_range_is_defined = self.options.axis.x.range is not None
        y_range_is_defined = self.options.axis.y.range is not None

        if not x_range_is_defined or not y_range_is_defined:
            stores = self._getDatasetsValues()

        # gather data for the x axis
        if x_range_is_defined:
            self.minxval, self.maxxval = self.options.axis.x.range
        else:
            xdata = [pair[0] for pair in reduce(lambda a, b: a+b, stores)]
            self.minxval = float(min(xdata))
            self.maxxval = float(max(xdata))
            if self.minxval * self.maxxval > 0 and self.minxval > 0:
                self.minxval = 0.0

        self.xrange = self.maxxval - self.minxval
        if self.xrange == 0:
            self.xscale = 1.0
        else:
            self.xscale = 1.0 / self.xrange

        # gather data for the y axis
        if y_range_is_defined:
            self.minyval, self.maxyval = self.options.axis.y.range
        else:
            ydata = [pair[1] for pair in reduce(lambda a, b: a+b, stores)]
            self.minyval = float(min(ydata))
            self.maxyval = float(max(ydata))
            if self.minyval * self.maxyval > 0 and self.minyval > 0:
                self.minyval = 0.0

        self.yrange = self.maxyval - self.minyval
        if self.yrange == 0:
            self.yscale = 1.0
        else:
            self.yscale = 1.0 / self.yrange

        if self.minyval * self.maxyval < 0: # different signs
            self.origin = abs(self.minyval) * self.yscale
        else:
            self.origin = 0.0

    def _updateChart(self):
        raise NotImplementedError

    def _updateTicks(self):
        """Evaluates ticks for x and y axis.

        You should call _updateXY before because that method computes the
        values of xscale, minxval, yscale, and other attributes needed for
        this method.
        """
        stores = self._getDatasetsValues()

        # evaluate xTicks
        self.xticks = []
        if self.options.axis.x.ticks:
            for tick in self.options.axis.x.ticks:
                if not isinstance(tick, Option):
                    tick = Option(tick)
                if tick.label is None:
                    label = str(tick.v)
                else:
                    label = tick.label
                pos = self.xscale * (tick.v - self.minxval)
                if 0.0 <= pos <= 1.0:
                    self.xticks.append((pos, label))

        elif self.options.axis.x.interval > 0:
            interval = self.options.axis.x.interval
            label = (divmod(self.minxval, interval)[0] + 1) * interval
            pos = self.xscale * (label - self.minxval)
            prec = self.options.axis.x.tickPrecision
            while 0.0 <= pos <= 1.0:
                pretty_label = round(label, prec)
                if prec == 0:
                    pretty_label = int(pretty_label)
                self.xticks.append((pos, pretty_label))
                label += interval
                pos = self.xscale * (label - self.minxval)

        elif self.options.axis.x.tickCount > 0:
            uniqx = range(len(uniqueIndices(stores)) + 1)
            roughSeparation = self.xrange / self.options.axis.x.tickCount
            i = j = 0
            while i < len(uniqx) and j < self.options.axis.x.tickCount:
                if (uniqx[i] - self.minxval) >= (j * roughSeparation):
                    pos = self.xscale * (uniqx[i] - self.minxval)
                    if 0.0 <= pos <= 1.0:
                        self.xticks.append((pos, uniqx[i]))
                        j += 1
                i += 1

        # evaluate yTicks
        self.yticks = []
        if self.options.axis.y.ticks:
            for tick in self.options.axis.y.ticks:
                if not isinstance(tick, Option):
                    tick = Option(tick)
                if tick.label is None:
                    label = str(tick.v)
                else:
                    label = tick.label
                pos = 1.0 - (self.yscale * (tick.v - self.minyval))
                if 0.0 <= pos <= 1.0:
                    self.yticks.append((pos, label))

        elif self.options.axis.y.interval > 0:
            interval = self.options.axis.y.interval
            label = (divmod(self.minyval, interval)[0] + 1) * interval
            pos = 1.0 - (self.yscale * (label - self.minyval))
            prec = self.options.axis.y.tickPrecision
            while 0.0 <= pos <= 1.0:
                pretty_label = round(label, prec)
                if prec == 0:
                    pretty_label = int(pretty_label)
                self.yticks.append((pos, pretty_label))
                label += interval
                pos = 1.0 - (self.yscale * (label - self.minyval))

        elif self.options.axis.y.tickCount > 0:
            prec = self.options.axis.y.tickPrecision
            num = self.yrange / self.options.axis.y.tickCount
            if (num < 1 and prec == 0):
                roughSeparation = 1
            else:
                roughSeparation = round(num, prec)

            for i in range(self.options.axis.y.tickCount + 1):
                yval = self.minyval + (i * roughSeparation)
                pos = 1.0 - ((yval - self.minyval) * self.yscale)
                if 0.0 <= pos <= 1.0:
                    pretty_label = round(yval, prec)
                    if prec == 0:
                        pretty_label = int(pretty_label)
                    self.yticks.append((pos, pretty_label))

    def _renderBackground(self, cx):
        """Renders the background area of the chart"""
        if self.options.background.hide:
            return

        cx.save()

        if self.options.background.baseColor:
            cx.set_source_rgb(*hex2rgb(self.options.background.baseColor))
            cx.paint()

        if self.options.background.chartColor:
            cx.set_source_rgb(*hex2rgb(self.options.background.chartColor))
            cx.rectangle(self.area.x, self.area.y, self.area.w, self.area.h)
            cx.fill()

        if self.options.background.lineColor:
            cx.set_source_rgb(*hex2rgb(self.options.background.lineColor))
            cx.set_line_width(self.options.axis.lineWidth)
            self._renderLines(cx)

        cx.restore()

    def _renderLines(self, cx):
        """Aux function for _renderBackground"""
        if self.options.axis.y.showLines and self.yticks:
            for tick in self.yticks:
                self._renderLine(cx, tick, False)
        if self.options.axis.x.showLines and self.xticks:
            for tick in self.xticks:
                self._renderLine(cx, tick, True)

    def _renderLine(self, cx, tick, horiz):
        """Aux function for _renderLines"""
        x1, x2, y1, y2 = (0, 0, 0, 0)
        if horiz:
            x1 = x2 = tick[0] * self.chart_area.w + self.chart_area.x
            y1 = self.chart_area.y
            y2 = y1 + self.chart_area.h
        else:
            x1 = self.chart_area.x
            x2 = x1 + self.chart_area.w
            y1 = y2 = tick[0] * self.chart_area.h + self.chart_area.y

        cx.new_path()
        cx.move_to(x1, y1)
        cx.line_to(x2, y2)
        cx.close_path()
        cx.stroke()

    def _renderChart(self, cx):
        raise NotImplementedError

    def _renderYTick(self, cx, tick):
        """Aux method for _renderAxis"""

        if callable(tick):
            return

        x = self.y_ticks_area.x + self.y_ticks_area.w
        y = self.y_ticks_area.y + tick[0] * self.y_ticks_area.h

        cx.new_path()
        cx.move_to(x, y)
        cx.line_to(x - self.options.axis.tickSize, y)
        cx.close_path()
        cx.stroke()

        cx.select_font_face(self.options.axis.tickFont,
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        cx.set_font_size(self.options.axis.tickFontSize)

        label = safe_unicode(tick[1], self.options.encoding)
        extents = cx.text_extents(label)
        labelWidth = extents[2]
        labelHeight = extents[3]

        if self.options.axis.y.rotate:
            radians = math.radians(self.options.axis.y.rotate)
            cx.move_to(x - self.options.axis.tickSize
                       - (labelWidth * math.cos(radians))
                       - 4,
                       y + (labelWidth * math.sin(radians))
                       + labelHeight / (2.0 / math.cos(radians)))
            cx.rotate(-radians)
            cx.show_text(label)
            cx.rotate(radians) # this is probably faster than a save/restore
        else:
            cx.move_to(x - self.options.axis.tickSize - labelWidth - 4,
                       y + labelHeight / 2.0)
            cx.show_text(label)

        return label

    def _renderXTick(self, cx, tick, fontAscent):
        if callable(tick):
            return

        x = self.x_ticks_area.x + tick[0] * self.x_ticks_area.w
        y = self.x_ticks_area.y

        cx.new_path()
        cx.move_to(x, y)
        cx.line_to(x, y + self.options.axis.tickSize)
        cx.close_path()
        cx.stroke()

        cx.select_font_face(self.options.axis.tickFont,
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        cx.set_font_size(self.options.axis.tickFontSize)

        label = safe_unicode(tick[1], self.options.encoding)
        extents = cx.text_extents(label)
        labelWidth = extents[2]
        labelHeight = extents[3]

        if self.options.axis.x.rotate:
            radians = math.radians(self.options.axis.x.rotate)
            cx.move_to(x - (labelHeight * math.cos(radians)),
                       y + self.options.axis.tickSize
                       + (labelHeight * math.cos(radians))
                       + 4.0)
            cx.rotate(radians)
            cx.show_text(label)
            cx.rotate(-radians)
        else:
            cx.move_to(x - labelWidth / 2.0,
                       y + self.options.axis.tickSize
                       + fontAscent + 4.0)
            cx.show_text(label)
        return label

    def _getTickSize(self, cx, ticks, rotate):
        su = lambda t: safe_unicode(t, self.options.encoding)
        tickExtents = [cx.text_extents(su(tick[1]))[2:4]
                       for tick in ticks]
        tickWidth = tickHeight = 0.0
        if tickExtents:
            tickHeight = self.options.axis.tickSize + 4.0
            tickWidth = self.options.axis.tickSize + 4.0
            widths, heights = zip(*tickExtents)
            maxWidth, maxHeight = max(widths), max(heights)
            if rotate:
                radians = math.radians(rotate)
                sinRadians = math.sin(radians)
                cosRadians = math.cos(radians)
                maxHeight = maxWidth * sinRadians + maxHeight * cosRadians
                maxWidth = maxWidth * cosRadians + maxHeight * sinRadians
            tickWidth += maxWidth
            tickHeight += maxHeight
        return tickWidth, tickHeight

    def _renderAxisLabel(self, cx, label, x, y, vertical=False):
        cx.select_font_face(self.options.axis.labelFont,
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_BOLD)
        cx.set_font_size(self.options.axis.labelFontSize)
        label_width, label_height = cx.text_extents(label)[2:4]
        font_ascent = cx.font_extents()[0]
        if vertical:
            cx.move_to(x + label_height, y + label_width / 2)
            radians = math.radians(90)
            cx.rotate(-radians)
        else:
            cx.move_to(x - label_width / 2.0, y + label_height)

        cx.show_text(label)

    def _getYAxisLabelWidth(self, cx):
        if self.options.axis.y.label:
            cx.save()
            cx.select_font_face(self.options.axis.labelFont,
                                cairo.FONT_SLANT_NORMAL,
                                cairo.FONT_WEIGHT_BOLD)
            cx.set_font_size(self.options.axis.labelFontSize)
            extents = cx.text_extents(self.options.axis.y.label)
            cx.restore()
            return extents[3]
        return 0.0

    def _renderYAxisLabel(self, cx, label_text):
        cx.save()
        cx.rectangle(self.y_label_area.x, self.y_label_area.y,
                     self.y_label_area.w, self.y_label_area.h)
        cx.clip()
        label = safe_unicode(label_text, self.options.encoding)
        x = self.y_label_area.x
        y = self.y_label_area.y + self.y_label_area.h / 2.0
        self._renderAxisLabel(cx, label, x, y, True)
        cx.restore()

    def _renderYAxis(self, cx):
        """Draws the vertical line represeting the Y axis"""
        cx.new_path()
        cx.move_to(self.chart_area.x, self.chart_area.y)
        cx.line_to(self.chart_area.x, self.chart_area.y + self.chart_area.h)
        cx.close_path()
        cx.stroke()

    def _getXAxisLabelHeight(self, cx):
        if self.options.axis.x.label:
            cx.save()
            cx.select_font_face(self.options.axis.labelFont,
                                cairo.FONT_SLANT_NORMAL,
                                cairo.FONT_WEIGHT_BOLD)
            cx.set_font_size(self.options.axis.labelFontSize)
            extents = cx.text_extents(self.options.axis.x.label)
            cx.restore()
            return extents[3]

        return 0.0

    def _renderXAxisLabel(self, cx, label_text):
        cx.save()
        cx.rectangle(self.x_label_area.x, self.x_label_area.y,
                     self.x_label_area.w, self.x_label_area.h)
        cx.clip()
        label = safe_unicode(label_text, self.options.encoding)
        x = self.x_label_area.x + self.x_label_area.w / 2.0
        y = self.x_label_area.y
        self._renderAxisLabel(cx, label, x, y, False)
        cx.restore()

    def _renderXAxis(self, cx):
        """Draws the horizontal line representing the X axis"""
        cx.new_path()
        cx.move_to(self.chart_area.x,
                   self.chart_area.y + self.chart_area.h * (1.0 - self.origin))
        cx.line_to(self.chart_area.x + self.chart_area.w,
                   self.chart_area.y + self.chart_area.h * (1.0 - self.origin))
        cx.close_path()
        cx.stroke()

    def _getXAxisTickLabelsHeight(self, cx):
        cx.save()
        cx.select_font_face(self.options.axis.tickFont,
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        cx.set_font_size(self.options.axis.tickFontSize)

        max_width = max_height = 0.0
        if not self.options.axis.x.hide:
            extents = [cx.text_extents(safe_unicode(
                        tick[1], self.options.encoding,
                        ))[2:4] # get width and height as a tuple
                      for tick in self.xticks]
            if extents:
                widths, heights = zip(*extents)
                max_width, max_height = max(widths), max(heights)
                if self.options.axis.x.rotate:
                    radians = math.radians(self.options.axis.x.rotate)
                    sinRadians = math.sin(radians)
                    cosRadians = math.cos(radians)
                    max_height = (max_width * sinRadians
                                  + max_height * cosRadians)
                    max_width = (max_width * cosRadians
                                 + max_height * sinRadians)
        cx.restore()
        return max_height

    def _getYAxisTickLabelsWidth(self, cx):
        cx.save()
        cx.select_font_face(self.options.axis.tickFont,
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        cx.set_font_size(self.options.axis.tickFontSize)

        max_width = max_height = 0.0
        if not self.options.axis.y.hide:
            extents = [cx.text_extents(safe_unicode(
                        tick[1], self.options.encoding,
                        ))[2:4] # get width and height as a tuple
                      for tick in self.yticks]
            if extents:
                widths, heights = zip(*extents)
                max_width, max_height = max(widths), max(heights)
                if self.options.axis.y.rotate:
                    radians = math.radians(self.options.axis.y.rotate)
                    sinRadians = math.sin(radians)
                    cosRadians = math.cos(radians)
                    max_height = (max_width * sinRadians
                                  + max_height * cosRadians)
                    max_width = (max_width * cosRadians
                                 + max_height * sinRadians)
        cx.restore()
        return max_width

    def _renderAxis(self, cx):
        """Renders axis"""
        if self.options.axis.x.hide and self.options.axis.y.hide:
            return

        cx.save()
        cx.set_source_rgb(*hex2rgb(self.options.axis.lineColor))
        cx.set_line_width(self.options.axis.lineWidth)

        if not self.options.axis.y.hide:
            if self.yticks:
                cx.save()
                cx.rectangle(self.y_tick_labels_area.x,
                             self.y_tick_labels_area.y,
                             self.y_tick_labels_area.w + self.y_ticks_area.w,
                             self.y_tick_labels_area.h)
                cx.clip()
                for tick in self.yticks:
                    self._renderYTick(cx, tick)
                cx.restore()

            if self.options.axis.y.label:
                self._renderYAxisLabel(cx, self.options.axis.y.label)

            self._renderYAxis(cx)

        if not self.options.axis.x.hide:
            font_ascent = cx.font_extents()[0]
            if self.xticks:
                cx.save()
                cx.rectangle(self.x_ticks_area.x, self.x_ticks_area.y,
                             self.x_ticks_area.w,
                             self.x_ticks_area.h + self.x_tick_labels_area.h)
                cx.clip()
                for tick in self.xticks:
                    self._renderXTick(cx, tick, font_ascent)
                cx.restore()

            if self.options.axis.x.label:
                self._renderXAxisLabel(cx, self.options.axis.x.label)

            self._renderXAxis(cx)

        cx.restore()

    def _getTitleHeight(self, cx):
        if self.options.title:
            cx.save()
            cx.select_font_face(self.options.titleFont,
                                cairo.FONT_SLANT_NORMAL,
                                cairo.FONT_WEIGHT_BOLD)
            cx.set_font_size(self.options.titleFontSize)
            title = safe_unicode(self.options.title, self.options.encoding)
            extents = cx.text_extents(title)
            cx.restore()
            return extents[3]
        return 0.0

    def _renderTitle(self, cx):
        if self.options.title:
            cx.save()
            cx.rectangle(self.title_area.x, self.title_area.y,
                         self.title_area.w, self.title_area.h)
            cx.clip()
            cx.select_font_face(self.options.titleFont,
                                cairo.FONT_SLANT_NORMAL,
                                cairo.FONT_WEIGHT_BOLD)
            cx.set_font_size(self.options.titleFontSize)
            cx.set_source_rgb(*hex2rgb(self.options.titleColor))

            title = safe_unicode(self.options.title, self.options.encoding)
            extents = cx.text_extents(title)
            title_width = extents[2]

            x = self.title_area.x + self.title_area.w / 2.0 - title_width / 2.0
            y = self.title_area.y + cx.font_extents()[0] # font ascent

            cx.move_to(x, y)
            cx.show_text(title)

            cx.restore()

    def _renderLegend(self, cx):
        """This function adds a legend to the chart"""
        if self.options.legend.hide:
            return

        surface_width, surface_height = self.getSurfaceSize()

        # Compute legend dimensions
        padding = 4
        bullet = 15
        width = 0
        height = padding
        keys = self._getDatasetsKeys()
        for key in keys:
            extents = cx.text_extents(key)
            width = max(extents[2], width)
            height += max(extents[3], bullet) + padding
        width = padding + bullet + padding + width + padding

        # Compute legend position
        legend = self.options.legend
        if legend.position.right is not None:
            legend.position.left = (surface_width
                                    - legend.position.right
                                    - width)
        if legend.position.bottom is not None:
            legend.position.top = (surface_height
                                   - legend.position.bottom
                                   - height)

        # Draw the legend
        cx.save()
        cx.rectangle(self.options.legend.position.left,
                     self.options.legend.position.top,
                     width, height)
        cx.set_source_rgba(1, 1, 1, self.options.legend.opacity)
        cx.fill_preserve()
        cx.set_line_width(self.options.legend.borderWidth)
        cx.set_source_rgb(*hex2rgb(self.options.legend.borderColor))
        cx.stroke()

        def drawKey(key, x, y, text_height):
            cx.rectangle(x, y, bullet, bullet)
            cx.set_source_rgb(*self.colorScheme[key])
            cx.fill_preserve()
            cx.set_source_rgb(0, 0, 0)
            cx.stroke()
            cx.move_to(x + bullet + padding,
                       y + bullet / 2.0 + text_height / 2.0)
            cx.show_text(key)

        cx.set_line_width(1)
        x = self.options.legend.position.left + padding
        y = self.options.legend.position.top + padding
        for key in keys:
            extents = cx.text_extents(key)
            drawKey(key, x, y, extents[3])
            y += max(extents[3], bullet) + padding

        cx.restore()


def uniqueIndices(arr):
    """Return a list with the indexes of the biggest element of arr"""
    return range(max([len(a) for a in arr]))


class Area(object):
    """Simple rectangle to hold an area coordinates and dimensions"""

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def __str__(self):
        msg = "<pycha.chart.Area@(%.2f, %.2f) %.2f x %.2f>"
        return  msg % (self.x, self.y, self.w, self.h)


class Option(dict):
    """Useful dict that allow attribute-like access to its keys"""

    def __getattr__(self, name):
        if name in self.keys():
            return self[name]
        else:
            raise AttributeError(name)

    def merge(self, other):
        """Recursive merge with other Option or dict object"""
        for key, value in other.items():
            if key in self:
                if isinstance(self[key], Option):
                    self[key].merge(other[key])
                else:
                    self[key] = other[key]


DEFAULT_OPTIONS = Option(
    axis=Option(
        lineWidth=1.0,
        lineColor='#0f0000',
        tickSize=3.0,
        labelColor='#666666',
        labelFont='Tahoma',
        labelFontSize=9,
        labelWidth=50.0,
        tickFont='Tahoma',
        tickFontSize=9,
        x=Option(
            hide=False,
            ticks=None,
            tickCount=10,
            tickPrecision=1,
            range=None,
            rotate=None,
            label=None,
            interval=0,
            showLines=False,
        ),
        y=Option(
            hide=False,
            ticks=None,
            tickCount=10,
            tickPrecision=1,
            range=None,
            rotate=None,
            label=None,
            interval=0,
            showLines=True,
        ),
    ),
    background=Option(
        hide=False,
        baseColor=None,
        chartColor='#f5f5f5',
        lineColor='#ffffff',
        lineWidth=1.5,
    ),
    legend=Option(
        opacity=0.8,
        borderColor='#000000',
        borderWidth=2,
        hide=False,
        position=Option(top=20, left=40, bottom=None, right=None),
    ),
    padding=Option(
        left=10,
        right=10,
        top=10,
        bottom=10,
    ),
    stroke=Option(
        color='#ffffff',
        hide=False,
        shadow=True,
        width=2
    ),
    yvals=Option(
        show=False,
        inside=False,
        fontSize=11,
        fontColor='#000000',
        skipSmallValues=True,
        snapToOrigin=False,
        renderer=None
    ),
    fillOpacity=1.0,
    shouldFill=True,
    barWidthFillFraction=0.75,
    pieRadius=0.4,
    colorScheme=Option(
        name='gradient',
        args=Option(
            initialColor=DEFAULT_COLOR,
            colors=None,
            ),
    ),
    title=None,
    titleColor='#000000',
    titleFont='Tahoma',
    titleFontSize=12,
    encoding='utf-8',
)
