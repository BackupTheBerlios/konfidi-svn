#include "email.h"

void Email::printOn(ostream* out) {
	*out << mbox_from << *message;
}
