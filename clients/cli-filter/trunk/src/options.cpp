#include "options.h"

#include <iostream>
#include <fstream>
#include <cstdlib>
using namespace std;

// for getting user home dir; POSIX
#include <sys/types.h>
#include <pwd.h>

bool Options::verbose = false;
string Options::source_fingerprint;
string Options::trust_server_url;
string Options::trust_server_params;
string Options::conf_file = ".dmail/cli-filter.conf";

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

void Options::load_config_file() {
    string home;
    
    //TODO: not linux-specific
    uid_t uid;
    struct passwd *info = getpwent();
	uid = geteuid();
	while(info != NULL) {
	    if(info->pw_uid == uid) {
	    	home = info->pw_dir;
			break;
		}
        info = getpwent();
    }
    if (!home.size()) {
    	cerr << "could not determine user home dir" << endl;
    	return;
    }
    
    string full_file = home + "/" + conf_file;
    ifstream file(full_file.c_str(), ios::in);
    if (!file) {
    	if (verbose)
    		clog << "no configuration file found at: " << full_file << endl;
    	return;	
    }
    string word;
    while (file >> word) {
    	if (word == "trust_server_url") {
    		file >> trust_server_url;
    		if (verbose)
    			clog << "read trust_server_url: " << trust_server_url << endl;
    	} else if (word == "trust_server_params") {
    		file >> trust_server_params;
    		if (verbose)
    			clog << "read trust_server_params: " << trust_server_params << endl;
    	} else if (word == "source_fingerprint") {
    		file >> source_fingerprint;
    		if (verbose)
    			clog << "read source_fingerprint: " << source_fingerprint << endl;
    	} else {
    		if (verbose)
    			clog << "skipping config entry: " << word << endl;
    	}
    }
}

bool Options::guess_source_fingerprint(gpgme_ctx_t ctx) {
	gpgme_error_t err;
	gpgme_key_t key;
	int count=0;
	string fpr;
	// list all private keys
	err = gpgme_op_keylist_start(ctx, NULL, 1);
	while (!err)
	{
		err = gpgme_op_keylist_next (ctx, &key);
		if (err)
			break;
		gpgme_subkey_t subkey = key->subkeys;
		while(subkey) {
			if (subkey->fpr && !subkey->revoked && !subkey->expired && !subkey->disabled && !subkey->invalid) {
				count++;
				fpr = subkey->fpr;
			}
			subkey = subkey->next;
		}
	}
	
	if (count==1) {
		Options::source_fingerprint = fpr;
		return true;
	}
	return false;
}

bool Options::safety_check() {
	// TODO: check that source_fingerprint is long hex
	// TODO: maybe check params
	if (!source_fingerprint.size()) {
		cerr << "You must specify a source_fingerprint in the config file" << endl;
		return false;
	} else if (!trust_server_url.size()) {
		cerr << "You must specify a trust_server_url in the config file" << endl;
		return false;
	} else if (!trust_server_params.size()) {
		cerr << "You must specify a trust_server_params in the config file" << endl;
		return false;
	} else {
		return true;
	}
}
