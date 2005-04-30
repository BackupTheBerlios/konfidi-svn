/*
Copyright (C) 2005-2005 Dave Brondsema, Andrew Schamp
This file is part of Konfidi http://konfidi.org/

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/

#ifndef _email_h
#define _email_h

#include <string>
#include <iostream>
using namespace std;

#include <mimetic/mimetic.h>
using namespace mimetic;

class Email
{
public:
	Email(string);
	/** optional leading 'From ' line */
	string mbox_from;
	/** literal text of the whole message */
	string exact_text;
	/** class used for parsing, but not writing */
	MimeEntity *message;
	
	void printOn(ostream*);
	
protected:
	/** possible "From " line in mbox format */
	void set_possible_From_line();
};

#endif
