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
