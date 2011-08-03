# Copyright(c) 2011 by Roberto Garcia Carvajal <roberpot@gmail.com>
#
# Based on PyCha sources by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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

import cairo

from math import pi, cos, sin

from pycha.chart import Chart
from pycha.color import hex2rgb
from pycha.utils import safe_unicode


class RadialChart(Chart):

    def __init__(self, surface=None, options={}):
        super(RadialChart, self).__init__(surface, options)
        self.points = []

    def _updateChart(self):
        """Evaluates measures for line charts"""
        self.points = []

        for i, (name, store) in enumerate(self.datasets):
            for item in store:
                xval, yval = item
                x = (xval - self.minxval) * self.xscale
                y = 1.0 - (yval - self.minyval) * self.yscale
                point = Point(x, y, xval, yval, name)

                if 0.0 <= point.x <= 1.0 and 0.0 <= point.y <= 1.0:
                    self.points.append(point)

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

    def _renderBackground(self, cx):
        """Renders the background area of the chart"""
        if self.options.background.hide:
            return

        cx.save()
        
        """ # Es necesario dibujar el contorno?
        cx.set_line_width(1.0)
        cx.save()
        cx.arc(self.area.x + self.area.w / 2,self.area.y + self.area.h / 2, self.area.h / 2, 0, 2*3.141592)
        cx.stroke()
        """
        
        if self.options.background.baseColor:
            cx.set_source_rgb(*hex2rgb(self.options.background.baseColor))
            cx.paint()

        if self.options.background.chartColor:
            cx.set_source_rgb(*hex2rgb(self.options.background.chartColor))
            cx.set_line_width(10.0)
            cx.arc(self.area.x + self.area.w / 2,self.area.y + self.area.h / 2, self.area.h / 2, 0, 2*3.141592)
            cx.fill()

        if self.options.background.lineColor:
            cx.set_source_rgb(*hex2rgb(self.options.background.lineColor))
            cx.set_line_width(self.options.axis.lineWidth)
            self._renderLines(cx)

        cx.restore()
        
    def _renderLine(self, cx, tick, horiz):
        """Aux function for _renderLines"""

        rad = (self.area.h/ 2) * (1 - tick[0])
        cx.arc(self.area.x + self.area.w / 2,self.area.y + self.area.h / 2, rad, 0, 2*3.141592)
        cx.stroke()
            
    def _renderXAxis(self, cx):
        """Draws the horizontal line representing the X axis"""
        
        count = len(self.xticks)
        
        centerx = self.area.x + self.area.w / 2
        centery = self.area.y + self.area.h / 2
        
        for i in range(0, count):
            offset1 = i * 2 * pi / count
            offset = pi / 2 - offset1
            
            rad = self.area.h / 2
            (r1, r2) = (0, rad + 5)
            
            x1 = centerx - cos(offset) * r1
            x2 = centerx - cos(offset) * r2
            y1 = centery - sin(offset) * r1
            y2 = centery - sin(offset) * r2
            
            cx.new_path()
            cx.move_to(x1, y1)
            cx.line_to(x2, y2)
            cx.close_path()
            cx.stroke()
            
    def _renderYTick(self, cx, tick, center):
        """Aux method for _renderAxis"""

        i = tick
        tick = self.yticks[i]
        
        count = len(self.yticks)

        if callable(tick):
            return

        x = center[0]
        y = center[1] - i * (self.area.h / 2) / count

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
            cx.rel_move_to(0.0, -labelHeight / 2.0)
            cx.show_text(label)

        return label

    def _renderYAxis(self, cx):
        """Draws the vertical line represeting the Y axis"""
        
        centerx = self.area.x + self.area.w / 2
        centery = self.area.y + self.area.h / 2
        
        offset = pi / 2
        
        r1 = self.area.h / 2
        
        x1 = centerx - cos(offset) * r1
        y1 = centery - sin(offset) * r1
        
        cx.new_path()
        cx.move_to(centerx, centery)
        cx.line_to(x1, y1)
        cx.close_path()
        cx.stroke()
        
    def _renderAxis(self, cx):
        """Renders axis"""
        if self.options.axis.x.hide and self.options.axis.y.hide:
            return

        cx.save()
        cx.set_source_rgb(*hex2rgb(self.options.axis.lineColor))
        cx.set_line_width(self.options.axis.lineWidth)
        
        centerx = self.area.x + self.area.w / 2
        centery = self.area.y + self.area.h / 2

        if not self.options.axis.y.hide:
            if self.yticks:
            
                count = len(self.yticks)
                
                for i in range(0, count):
                    tick = self.yticks[i]
                    self._renderYTick(cx, i, (centerx, centery))

            if self.options.axis.y.label:
                self._renderYAxisLabel(cx, self.options.axis.y.label)

            self._renderYAxis(cx)

        if not self.options.axis.x.hide:
            fontAscent = cx.font_extents()[0]
            if self.xticks:
            
                count = len(self.xticks)
                
                for i in range(0, count):
                    tick = self.xticks[i]
                    self._renderXTick(cx, i, fontAscent, (centerx, centery))

            if self.options.axis.x.label:
                self._renderXAxisLabel(cx, self.options.axis.x.label)

            self._renderXAxis(cx)

        cx.restore()
        
    def _renderXTick(self, cx, i, fontAscent, center):
        tick = self.xticks[i]
        if callable(tick):
            return

        count = len(self.xticks)
        #import ipdb
        #ipdb.set_trace()
        #print (cx, tick)


        """
        x = self.area.x + tick[0] * self.area.w
        y = self.area.y + self.area.h

        cx.new_path()
        cx.move_to(x, y)
        cx.line_to(x, y + self.options.axis.tickSize)
        cx.close_path()
        cx.stroke()
        """
        
        cx.select_font_face(self.options.axis.tickFont,
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        cx.set_font_size(self.options.axis.tickFontSize)

        label = safe_unicode(tick[1], self.options.encoding)
        extents = cx.text_extents(label)
        labelWidth = extents[2]
        labelHeight = extents[3]
        
        cx.move_to(center[0], center[1])

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
            
            offset1 = i * 2 * pi / count
            offset = pi / 2 - offset1
            
            rad = self.area.h / 2 + 10
            
            x = center[0] - cos(offset) * rad
            y = center[1] - sin(offset) * rad            

            cx.move_to(x, y)
            cx.rotate(offset - pi / 2)
            
            
            if sin(offset) < 0.0:
                cx.rotate(pi)
                cx.rel_move_to(0.0, 5.0)
            
            cx.rel_move_to(-labelWidth / 2.0, 0)
            """
            cx.move_to(x - labelWidth / 2.0,
                       y + self.options.axis.tickSize
                       + fontAscent + 4.0)
            """
            cx.show_text(label)
            if sin(offset) < 0.0:
                cx.rotate(-pi)
            
            cx.rotate(-(offset - pi / 2))
        return label
        
    def _renderChart(self, cx):
        """Renders a line chart"""
        # Dibujamos el circulo.
        def preparePath(storeName):
            cx.new_path()
            firstPoint = True
            lastX = None
            #if self.options.shouldFill:
                # Go to the (0,0) coordinate to start drawing the area
                #cx.move_to(self.area.x, self.area.y + self.area.h)
            #    offset = (1.0 - self.area.origin) * self.area.h
            #    cx.move_to(self.area.x, self.area.y + offset)
            
            count = len(self.points) / len(self.datasets)
            centerx = self.area.x + self.area.w / 2
            centery = self.area.y + self.area.h / 2
            
            firstPointCoord = None
            
            #print (self.area.x, self.area.y, self.area.w, self.area.h, count)
            for index, point in enumerate(self.points):
                if point.name == storeName:
                    offset1 = index * 2 * pi / count
                    offset = pi / 2 - offset1
                
                    rad = (self.area.h / 2) * (1 - point.y)
            
                    x = centerx - cos(offset) * rad
                    y = centery - sin(offset) * rad
                    
                    if firstPointCoord is None:
                        firstPointCoord = (x, y)
                    
                    if not self.options.shouldFill and firstPoint:
                        # starts the first point of the line
                        cx.move_to(x, y)
                        firstPoint = False
                        continue
                    cx.line_to(x, y)
                    # we remember the last X coordinate to close the area
                    # properly. See bug #4
                    lastX = point.x
            
            if not firstPointCoord is None:
                cx.line_to(firstPointCoord[0], firstPointCoord[1])

            if self.options.shouldFill:
                # Close the path to the start point
                y = (1.0 - self.area.origin) * self.area.h + self.area.y
                #cx.line_to(lastX * self.area.w + self.area.x, y)
                #cx.line_to(self.area.x, y)
                #cx.close_path()
            else:
                cx.set_source_rgb(*self.colorScheme[storeName])
                cx.stroke()


        cx.save()
        cx.set_line_width(self.options.stroke.width)
        if self.options.shouldFill:

            def drawLine(storeName):
                if self.options.stroke.shadow:
                    # draw shadow
                    cx.save()
                    cx.set_source_rgba(0, 0, 0, 0.15)
                    cx.translate(2, -2)
                    preparePath(storeName)
                    cx.fill()
                    cx.restore()

                # fill the line
                cx.set_source_rgb(*self.colorScheme[storeName])
                preparePath(storeName)
                cx.fill()

                if not self.options.stroke.hide:
                    # draw stroke
                    cx.set_source_rgb(*hex2rgb(self.options.stroke.color))
                    preparePath(storeName)
                    cx.stroke()

            # draw the lines
            for key in self._getDatasetsKeys():
                drawLine(key)
        else:
            for key in self._getDatasetsKeys():
                preparePath(key)
        cx.restore()
        
        

class Point(object):

    def __init__(self, x, y, xval, yval, name):
        self.x, self.y = x, y
        self.xval, self.yval = xval, yval
        self.name = name

    def __str__(self):
        return "<pycha.line.Point@(%.2f, %.2f)>" % (self.x, self.y)
