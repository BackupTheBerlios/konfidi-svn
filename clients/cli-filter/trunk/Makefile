#  Copyright (C) 2005-2005 Dave Brondsema, Andrew Schamp
#  This file is part of Konfidi http://konfidi.org/
#  
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


#
# To make a static executable, run:
#               STATIC=-static make clean all
#  All dependencies will have to have built static libraries.  Do so by adding --enable-static to ./configure

EXE = konfidi-cli-filter

SRC = src

# get all the .cpp files in this directory
SRCS = $(shell ls $(SRC)/*.cpp)
# assume we must create a .o for each of them
OBJS = $(SRCS:.cpp=.o)

CFLAGS = -Wall `gpgme-config --cflags` `curl-config --cflags`
LFLAGS = $(STATIC) `gpgme-config --libs` -lmimetic `curl-config --libs`


all: $(EXE)

$(EXE): $(OBJS)
	g++ -o $(EXE) $(OBJS) $(LFLAGS)

%.o: %.cpp
	g++ -o $@ -c $(CFLAGS) $^

clean:
	rm -f $(EXE) $(OBJS) *.*~ *~ *.bak core
