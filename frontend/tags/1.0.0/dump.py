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

import types

def dump(v):
    """Print a nicely formatted overview of any data structure"""
    if v is None:
        return "(None)\n"
    if type(v) is types.DictType:
        return __dumpDict(v)
    elif hasattr(v, '__iter__') and hasattr(v, 'items'):
        return __dumpDict(v)
    elif type(v) is types.TupleType:
        return __dumpTuple(v)
    elif type(v) is types.ListType:
        return __dumpTuple(v)
    elif type(v) is types.StringType:
        return v + '\n'
    elif type(v) is types.IntType:
        return '%i' % v + '\n'
    elif type(v) is types.LongType:
        return '%i' % v + '\n'
    elif hasattr(v, '__class__'):
        return __dumpObj(v)
    else:
        return '%s' % v + ' ' + '%s' % type(v) + '\n'

def __dumpTuple(tup):
    return (len(tup) * '%s ') % tuple(tup) + '\n'

def __dumpDict(di, format="%-25s %s"):
    ret = ""
    for (key, val) in di.items():
        ret += format % (str(key)+':', val) + '\n'
    return ret

def __dumpObj(obj, maxlen=77, lindent=24, maxspew=600):
    """Print a nicely formatted overview of an object.

    The output lines will be wrapped at maxlen, with lindent of space
    for names of attributes.  A maximum of maxspew characters will be
    printed for each attribute value.

    You can hand dumpObj any data type -- a module, class, instance,
    new class.

    Note that in reformatting for compactness the routine trashes any
    formatting in the docstrings it prints.

    Example:
       >>> class Foo(object):
               a = 30
               def bar(self, b):
                   "A silly method"
                   return a*b
       ... ... ... ... 
       >>> foo = Foo()
       >>> dumpObj(foo)
       Instance of class 'Foo' as defined in module __main__ with id 136863308
       Documentation string:   None
       Built-in Methods:       __delattr__, __getattribute__, __hash__, __init__
                               __new__, __reduce__, __repr__, __setattr__,       
                               __str__
       Methods:
         bar                   "A silly method"
       Attributes:
         __dict__              {}
         __weakref__           None
         a                     30
    """
    
    import types

    ret = ""

    # Formatting parameters.
    ltab    = 2    # initial tab in front of level 2 text

    # There seem to be a couple of other types; gather templates of them
    MethodWrapperType = type(object().__hash__)

    #
    # Gather all the attributes of the object
    #
    objclass  = None
    objdoc    = None
    objmodule = '<None defined>'
    
    methods   = []
    builtins  = []
    classes   = []
    attrs     = []
    for slot in dir(obj):
        attr = getattr(obj, slot)
        if   slot == '__class__':
            objclass = attr.__name__
        elif slot == '__doc__':
            objdoc = attr
        elif slot == '__module__':
            objmodule = attr
        elif (isinstance(attr, types.BuiltinMethodType) or 
              isinstance(attr, MethodWrapperType)):
            builtins.append( slot )
        elif (isinstance(attr, types.MethodType) or
              isinstance(attr, types.FunctionType)):
            methods.append( (slot, attr) )
        elif isinstance(attr, types.TypeType):
            classes.append( (slot, attr) )
        else:
            attrs.append( (slot, attr) )

    #
    # Organize them
    #
    methods.sort()
    builtins.sort()
    classes.sort()
    attrs.sort()

    #
    # Print a readable summary of those attributes
    #
    normalwidths = [lindent, maxlen - lindent]
    tabbedwidths = [ltab, lindent-ltab, maxlen - lindent - ltab]

    def truncstring(s, maxlen):
        if len(s) > maxlen:
            return s[0:maxlen] + ' ...(%d more chars)...' % (len(s) - maxlen)
        else:
            return s

    # Summary of introspection attributes
    if objclass == '':
        objclass = type(obj).__name__
    intro = "Instance of class '%s' as defined in module %s with id %d" % \
            (objclass, objmodule, id(obj))
    ret += '\n'.join(prettyPrint(intro, maxlen))

    # Object's Docstring
    if objdoc is None:
        objdoc = str(objdoc)
    else:
        objdoc = ('"""' + objdoc.strip()  + '"""')
    ret += "\n"
    ret += prettyPrintCols( ('Documentation string:',
                            truncstring(objdoc, maxspew)),
                          normalwidths, ' ')

    # Built-in methods
    if builtins:
        bi_str   = delchars(str(builtins), "[']") or str(None)
        ret += "\n"
        ret += prettyPrintCols( ('Built-in Methods:',
                                truncstring(bi_str, maxspew)),
                              normalwidths, ', ')
        
    # Classes
    if classes:
        ret += "\n"
        ret += 'Classes:'
    for (classname, classtype) in classes:
        classdoc = getattr(classtype, '__doc__', None) or '<No documentation>'
        ret += prettyPrintCols( ('',
                                classname,
                                truncstring(classdoc, maxspew)),
                              tabbedwidths, ' ')

    # User methods
    if methods:
        ret += "\n"
        ret += 'Methods:'
    for (methodname, method) in methods:
        methoddoc = getattr(method, '__doc__', None) or '<No documentation>'
        ret += prettyPrintCols( ('',
                                methodname,
                                truncstring(methoddoc, maxspew)),
                              tabbedwidths, ' ')

    # Attributes
    if attrs:
        ret += "\n"
        ret += 'Attributes:'
    for (attr, val) in attrs:
        ret += prettyPrintCols( ('',
                                attr,
                                truncstring(str(val), maxspew)),
                              tabbedwidths, ' ')

    return ret + '\n'

def prettyPrintCols(strings, widths, split=' '):
    """Pretty prints text in colums, with each string breaking at
    split according to prettyPrint.  margins gives the corresponding
    right breaking point."""

    assert len(strings) == len(widths)

    strings = map(nukenewlines, strings)

    # pretty print each column
    cols = [''] * len(strings)
    for i in range(len(strings)):
        cols[i] = prettyPrint(strings[i], widths[i], split)


    # prepare a format line
    format = ''.join(["%%-%ds" % width for width in widths[0:-1]]) + "%s"

    def formatline(*cols):
        return format % tuple(map(lambda s: (s or ''), cols))

    # generate the formatted text
    return '\n'.join(map(formatline, *cols))

def prettyPrint(string, maxlen=75, split=' '):
    """Pretty prints the given string to break at an occurrence of
    split where necessary to avoid lines longer than maxlen.

    This will overflow the line if no convenient occurrence of split
    is found"""

    # Tack on the splitting character to guarantee a final match
    string += split
    
    lines   = []
    oldeol  = 0
    eol     = 0
    while not (eol == -1 or eol == len(string)-1):
        eol = string.rfind(split, oldeol, oldeol+maxlen+len(split))
        lines.append(string[oldeol:eol])
        oldeol = eol + len(split)

    return lines

def nukenewlines(string):
    """Strip newlines and any trailing/following whitespace; rejoin
    with a single space where the newlines were.
    
    Bug: This routine will completely butcher any whitespace-formatted
    text."""
    
    if not string: return ''
    lines = string.splitlines()
    return ' '.join( [line.strip() for line in lines] )
    
def delchars(str, chars):
    """Returns a string for which all occurrences of characters in
    chars have been removed."""

    # Translate demands a mapping string of 256 characters;
    # whip up a string that will leave all characters unmolested.
    identity = ''.join([chr(x) for x in range(256)])

    return str.translate(identity, chars)