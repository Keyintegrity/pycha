# Copyright(c) 2007-2010 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#              2009-2010 by Yaco S.L. <lgs@yaco.es>
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

def clamp(minValue, maxValue, value):
    """Make sure value is between minValue and maxValue"""
    if value < minValue:
        return minValue
    if value > maxValue:
        return maxValue
    return value


def safe_unicode(string_like_object, encoding=None):
    """Return a unicode value from the argument"""
    assert(isinstance(string_like_object, basestring))
    if isinstance(string_like_object, unicode):
        return string_like_object
    elif isinstance(string_like_object, str):
        if encoding is None:
            return unicode(string_like_object)
        else:
            return unicode(string_like_object, encoding)
