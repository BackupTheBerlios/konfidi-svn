
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
	string mbox_from;
	string exact_text;
	MimeEntity *message;
	
	void printOn(ostream*);
};

#endif
