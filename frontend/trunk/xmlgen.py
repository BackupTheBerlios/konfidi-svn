#  Copyright (C) 2005-2005 Dave Brondsema, Andrew Schamp
#  This file is part of Konfidi http://konfidi.org/
#  It is licensed under two alternative licenses (your choice):
#      1. Apache License, Version 2.0
#      2. GNU Lesser General Public License, Version 2.1
#
#
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#
# XML generation module
#

import string

class Element:

  def __init__(self, name, *cdata, **attrs):
    self.__name = name
    self.__children = []
    self.__cdata = cdata
    self.__attrs = attrs

  def __getattr__(self, name):
    if name[:2] == '__':
      raise AttributeError, name
    child = Element(name)
    self.__children.append(child)
    return Intermediate(self, child)

  def __call__(self, *cdata, **attrs):
    self.__cdata = self.__cdata + cdata
    self.__attrs.update(attrs)
    return self

  def __getitem__(self, items):
    if type(items) == type(()) or type(items) == type([]):
      self.__children = self.__children + list(items)
    else:
      self.__children.append(items)
    return self

  def __str__(self):
    s = '<' + self.__name
    for name, value in self.__attrs.items():
      s = s + ' ' + name + '="' + str(value) + '"'
    if self.__cdata or self.__children:
      s = s + ">"  + string.joinfields(self.__cdata, '')
      for child in self.__children:
        s = s + str(child)
      s = s + '</' + self.__name + '>'
    else:
      s = s + '/>'
    return s

class Factory:
  def __getattr__(self, name):
    if name[:2] == '__':
      raise AttributeError, name
    return Element(name)

class Intermediate:
  def __init__(self, parent, child):
    self.__parent = parent
    self.__child = child

  def __getattr__(self, name):
    inter = getattr(self.__child, name)
    return Intermediate(self.__parent, inter.__child)

  def __call__(self, *cdata, **attrs):
    apply(self.__child, cdata, attrs)
    return self

  def __getitem__(self, items):
    self.__child[items]
    return self

  def __str__(self):
    return str(self.__parent)


def test():
  f = Factory()
  l = f.ul[f.li('list 1'), f.li('list 2'), f.li('list 3')]
  l[f.li('list 4')]
  top = f.html[f.head.title.i('title'), f.body(bgcolor='#ffffff')[f.h1('heading'),f.p('text'),l]]
  print top
