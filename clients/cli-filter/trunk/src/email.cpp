#include "email.h"

void Email::printOn(ostream* out) {
	*out << mbox_from;
	
	Header::const_iterator hbit = message->header().begin(), heit = message->header().end();
	for(; hbit != heit; ++hbit)
		*out << *hbit << endl;
	
	int body_start = exact_text.find("\n\n")+2;
	*out << exact_text.substr(body_start);
}
