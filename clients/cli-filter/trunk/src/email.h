
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
	/** optional leading 'From ' line */
	string mbox_from;
	/** literal text of the whole message */
	string exact_text;
	/** class used for parsing, but not writing */
	MimeEntity *message;
	
	void printOn(ostream*);
};

#endif
