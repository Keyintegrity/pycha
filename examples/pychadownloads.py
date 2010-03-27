# Copyright (c) 2007-2008 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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

import pycha.stackedbar


def barChart(output):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 300)

    downloads = (('0.1.0', 193),
                 ('0.2.0', 567),
                 ('0.3.0', 835),
                 ('0.4.0', 161), ('0.4.1', 689), ('0.4.2', 234),
                 ('0.5.0', 913), ('0.5.1', 163), ('0.5.2', 1474))
    dataSet = (
        ('main release', [(0, 193), (1, 567), (2, 835), (3, 161), (4, 913)]),
        ('1st bug fix',  [(0, 0),   (1, 0),   (2, 0),   (3, 689), (4, 163)]),
        ('2nd bug fix',  [(0, 0),   (1, 0),   (2, 0),   (3, 234), (4, 1474)]),
        )

    options = {
        'axis': {
            'x': {
                'ticks': [dict(v=0, label='0.1 (Oct 07)'),
                          dict(v=1, label='0.2 (Oct 07)'),
                          dict(v=2, label='0.3 (Mar 08)'),
                          dict(v=3, label='0.4 (Oct 08)'),
                          dict(v=4, label='0.5 (Mar 09)')],
                'label': 'Releases',
            },
            'y': {
                'label': 'Downloads',
            }
        },
        'background': {
            'chartColor': '#ffeeff',
            'baseColor': '#ffffff',
            'lineColor': '#444444'
        },
        'colorScheme': {
            'name': 'gradient',
            'args': {
                'initialColor': 'green',
            },
        },
        'padding': {
            'left': 75,
            'bottom': 55,
        },
        'legend': {
            'position': {
                'top': 20,
                'left': 80,
            }
        },
        'title': 'Pycha Downloads'
    }
    chart = pycha.stackedbar.StackedVerticalBarChart(surface, options)

    chart.addDataset(dataSet)
    chart.render()

    surface.write_to_png(output)

if __name__ == '__main__':
    barChart('pychadownloads.png')
