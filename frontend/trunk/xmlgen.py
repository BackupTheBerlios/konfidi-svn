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
