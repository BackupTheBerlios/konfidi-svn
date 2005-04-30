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

#include "email.h"

#include <sstream>
using namespace std;


Email::Email(string content) {
	exact_text = content;
	
	set_possible_From_line();
	
	istringstream text_stream(exact_text);
    message = new MimeEntity(text_stream);
}

void Email::set_possible_From_line() {
	if (exact_text.substr(0, 5) == "From ") {
		int mbox_from_end = exact_text.find("\n")+1;
		mbox_from = exact_text.substr(0, mbox_from_end);
	}
}

void Email::printOn(ostream* out) {
	*out << mbox_from;
	
	Header::const_iterator hbit = message->header().begin(), heit = message->header().end();
	for(; hbit != heit; ++hbit)
		*out << *hbit << endl;
	
	int body_start = exact_text.find("\n\n")+1;
	*out << exact_text.substr(body_start);
}
