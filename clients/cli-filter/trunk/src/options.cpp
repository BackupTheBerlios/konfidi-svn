#include "options.h"

#include <iostream>
#include <fstream>

using namespace std;

bool Options::verbose = false;
string Options::source_fingerprint = "EAB0FABEDEA81AD4086902FE56F0526F9BB3CE70";
string Options::trust_server_url = "http://brondsema.gotdns.com/~ams5/frontend/trunk/query";
string Options::trust_server_params = "strategy=Prototype&subject=email&trustoutput=short&";

void Options::process_args(int argc, char* argv[]) {
	if (argc == 1) {
		// no args
	} else if (argc == 2 && (string)argv[1] == "-v") {
		verbose = true;
	} else {
		cerr << "Invalid argument." << endl << endl;
		cerr << "Valid arguments: " << endl;
		cerr << "\t-v\t\tverbose" << endl;
		cerr << endl << "This program accepts a single RFC2822 message (optionally with an mbox-style 'From ' first line) on stdin" << endl;
		exit(1);
	}
}

