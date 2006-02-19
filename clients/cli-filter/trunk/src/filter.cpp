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

#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <string>

#include <mimetic/mimetic.h>
#include <gpgme.h>
#include <curl/curl.h>

#include "options.h"
#include "email.h"

using namespace std;
using namespace mimetic;

const char* header_sig = "X-PGP-Signature";
const char* header_sig_finger = "X-PGP-Fingerprint";
const char* header_trust_num = "X-Konfidi-Email-Rating";
const char* header_trust_level = "X-Konfidi-Email-Level";
const char* header_this_app = "X-Konfidi-Client";
const char* header_this_app_value = "cli-filter 0.1";

#define fail_if_err(err)                                        \
  do                                                            \
    {                                                           \
      if (err)                                                  \
        {                                                       \
          fprintf (stderr, "%s:%d: %s: %s (%d.%d) [%d]\n",           \
                   __FILE__, __LINE__, gpg_strsource (err),     \
                   gpg_strerror (err),                          \
                   gpg_err_source (err), gpg_err_code (err),    \
                   err);   \
          exit (1);                                             \
        }                                                       \
    }                                                           \
  while (0)

// TODO: handle this better
// TODO: release gpg context
int quit(Email * email, int flag=0) {
	email->printOn(&cout);
	clog << endl;
	exit(flag);
}

string slurp(istream &i) {
	// read the whole message
	string whole;
	getline(i, whole, '\0');
	return whole;
}

void delete_header(Header * header, string field_name) {
    // header is a child of std::deque<Field>
	deque<Field>::iterator it;
	it = find_if(header->begin(), header->end(),
			Header::find_by_name(field_name));
	if (it != header->end()) {
		header->erase(it);
	}
}

void clean_headers(Email * email) {
    delete_header(& email->message->header(), header_sig);
    delete_header(& email->message->header(), header_sig_finger);
    delete_header(& email->message->header(), header_trust_num);
    delete_header(& email->message->header(), header_trust_level);
}

string parse_email_text(Email * email) {
    if (email->message->header().contentType().type() != "multipart" ||
    	email->message->header().contentType().subtype() != "signed") {
        cerr << "warning: email " + email->message->header().messageid().str() + " is not multipart/signed, it is: " << email->message->header().contentType().str() << endl;
        email->message->header().field(header_sig).value("none");
        quit(email);
    }
	if (email->message->body().parts().size() != 2) {
        cerr << "warning: email " + email->message->header().messageid().str() + " doesn't have 2 parts, it has " << email->message->body().parts().size() << endl;
        email->message->header().field(header_sig).value("none");
        quit(email);
	}
	
	string boundary = "--" + email->message->header().contentType().param("boundary");
	// start at 1st boundary
	int text_start = email->exact_text.find(boundary)+boundary.length()+1;
	// end at 2nd boundary
	int text_end = email->exact_text.find(boundary, text_start);
	string text = email->exact_text.substr(text_start, text_end-text_start-1);
	// lf -> crlf
	int p=-1;
	while (std::string::npos != (p=text.find("\n",p+2)))
		text.replace(p,1,"\r\n");
	
	return text;
}

string parse_email_sig(Email * email) {
    MimeEntity last_part = *email->message->body().parts().back();
    if (last_part.header().contentType().type() != "application" ||
    	last_part.header().contentType().subtype() != "pgp-signature") {
    	cerr << "2nd part of message isn't application/pgp-signature, it is: " << last_part.header().contentType().str() << endl;
        email->message->header().field(header_sig).value("none");
        quit(email);
    }
	return last_part.body();
}

gpgme_verify_result_t gpg_validate(gpgme_ctx_t ctx, string text, string sig) {
	gpgme_error_t err;
    
    gpgme_data_t sig_data;
    err = gpgme_data_new_from_mem(&sig_data, sig.c_str(), sig.length(), 1);
    fail_if_err(err);
    gpgme_data_t text_data;
    err = gpgme_data_new_from_mem(&text_data, text.c_str(), text.length(), 1);
    fail_if_err(err);

    err = gpgme_op_verify(ctx, sig_data, text_data, NULL);
    fail_if_err(err);
    return gpgme_op_verify_result (ctx);
}

void validate_from_matches_signer(Email * email, gpgme_ctx_t ctx, gpgme_verify_result_t result) {
	gpgme_error_t err;
    gpgme_key_t key;
    // need a new context otherwise 'result' stuff gets reset
    gpgme_ctx_t ctx2;
    err = gpgme_new(&ctx2);
    fail_if_err(err);
    
	err = gpgme_op_keylist_start(ctx2, result->signatures->fpr, 0);
	fail_if_err(err);
	err = gpgme_op_keylist_next (ctx2, &key);
	if (gpg_err_code(err) == GPG_ERR_EOF) {
		cerr << "Couldn't not find public key for: " << result->signatures->fpr
			<< "  Perhaps you need to set 'keyserver-options auto-key-retrieve' in ~/.gnupg/gpg.conf" << endl;
		email->message->header().field(header_sig).value("public key not available");
		quit(email);
	} else {
		fail_if_err(err);
	}
	err = gpgme_op_keylist_end(ctx2);
	fail_if_err(err);
	gpgme_release(ctx2);
	
	bool found_email = false;
	string from_email = email->message->header().from().front().mailbox() + '@' + email->message->header().from().front().domain();
	gpgme_user_id_t uid = key->uids;
	while (uid) {
		if (from_email == uid->email) {
			found_email = true;
		}
		uid = uid->next;
	}
	if (!found_email) {
		cerr << "no PGP uid email matched the 'From: ' on " << email->message->header().messageid().str() << endl;
		email->message->header().field(header_sig).value("from mismatch");
		quit(email);
	}
}

void add_gpg_headers(Email * email, gpgme_verify_result_t result) {
    if (result->signatures->status == GPG_ERR_NO_ERROR) {
        email->message->header().field(header_sig).value("valid");
    } else {
        email->message->header().field(header_sig).value((string)"invalid, " + gpg_strerror(result->signatures->status));
    }
    email->message->header().field(header_sig_finger).value(result->signatures->fpr);
}

string rating_to_starlevel(double rating) {
	rating *= 10;
	rating += 0.5;
	string stars = "";
	for (int i = 1; i <= 10 && i < rating; i++) {
		stars += "*";
	}
	return stars;
}

size_t curl_handle_data(void *buffer, size_t size, size_t nmemb, void *userp) {
	if (Options::verbose)
		clog << (char*)buffer << endl;
	istringstream buffer_stream((char*)buffer);
	double value;
	buffer_stream >> value;
	
//	if (Options::verbose)
//		clog << "streamed double value: " << value << endl;
	
	ostringstream value_stream;
	value_stream << value;
	
	Email * email = (Email *) userp;
	email->message->header().field(header_trust_num).value(value_stream.str());
	email->message->header().field(header_trust_level).value(rating_to_starlevel(value));
	// TODO: not sure what we're supposed to return
	return nmemb;
}

void add_trust_headers(Email * email, string to) {
	CURLcode res;
	CURL *handle = curl_easy_init();
	if(handle) {
		string source_sink = "source=" + Options::source_fingerprint + "&" + "sink=" + to + "&";
		string url = Options::trust_server_url + "?" + Options::trust_server_params + source_sink;
		if (Options::verbose)
			clog << "fetching " << url << endl;
		curl_easy_setopt(handle, CURLOPT_URL, url.c_str());
		curl_easy_setopt(handle, CURLOPT_WRITEFUNCTION, curl_handle_data);
		curl_easy_setopt(handle, CURLOPT_WRITEDATA, email);
		char error_buffer[CURL_ERROR_SIZE];
		curl_easy_setopt(handle, CURLOPT_ERRORBUFFER, error_buffer);
		curl_easy_setopt(handle, CURLOPT_FAILONERROR, 1);
		res = curl_easy_perform(handle);
		if (res != 0) {
			cerr << "Error with trustserver: " << error_buffer << endl;
		}
		curl_easy_cleanup(handle);
	} else { 
		cerr << "couldn't init curl" << endl;
	}
}

int main(int argc, char* argv[]) {
	gpgme_error_t err;
    gpgme_ctx_t ctx;
    
	Options::process_args(argc, argv);
    if (Options::version) {
        cout << header_this_app_value << endl;
        return 0;
    }
    
    // create a context solely for guessing source fingerprint
    // must guess source fingerprint before loading config file, so that the file has priority
    err = gpgme_new(&ctx);
    fail_if_err(err);
    Options::guess_source_fingerprint(ctx);
    gpgme_release(ctx);
    
	Options::load_config_file();
	if (!Options::safety_check()) {
		return 5;
	}
    
    
    // set pgp exe configuration, if we have options for it
    // must be done before creating our main context
    if (Options::openpgp_exe.size()) {
        err = gpgme_set_engine_info(GPGME_PROTOCOL_OpenPGP, Options::openpgp_exe.c_str(), (Options::openpgp_homedir.size() ? Options::openpgp_homedir.c_str() : NULL));
        fail_if_err(err);
    }
    
    // our main context
    err = gpgme_new(&ctx);
    fail_if_err(err);
    
    if (Options::verbose) {
        gpgme_engine_info_t info;
        gpgme_error_t err;
        err = gpgme_get_engine_info (&info);
        if (!err)
        {
            clog << "Current protocol: " << gpgme_get_protocol_name(gpgme_get_protocol(ctx)) << endl;
            while (info) {
                if (info->file_name) {
                    clog << "Engine " << info->file_name;
                    if (!info->version)
                        clog << " not installed properly (no version detected).";
                    else
                        clog << " version " << info->version << " installed.";
                    clog << " At least version " << (info->req_version ? info->req_version : "(null)") << " required."
                    << " Protocol: " << gpgme_get_protocol_name(info->protocol)
                    << ". Home dir: " << (info->home_dir ? info->home_dir : "(default)") << endl;
                }
                else {
                    clog << "Unknown problem with engine for protocol " << gpgme_get_protocol_name(info->protocol) << endl;
                }
                info = info->next;
            }
        }
    }
        
    
	Email* email = new Email(slurp(cin));

    clean_headers(email);
    email->message->header().field(header_this_app).value(header_this_app_value);
    

	string text = parse_email_text(email);
	string sig = parse_email_sig(email);
    
    
    if (Options::verbose)
	    clog << "processing " << email->message->header().messageid().str() << endl;

	gpgme_verify_result_t result = gpg_validate(ctx, text, sig);
    
    if (Options::verbose)
	    clog << "did key " << result->signatures->fpr << endl;
    
	validate_from_matches_signer(email, ctx, result);
	
	if (Options::verbose) {
	    clog << "valid: " << (result->signatures->summary & GPGME_SIGSUM_VALID) << endl;
	    clog << "GREEN: " << (result->signatures->summary & GPGME_SIGSUM_GREEN) << endl;
	    clog << "RED: " << (result->signatures->summary & GPGME_SIGSUM_RED) << endl;
	    clog << "rev key: " << (result->signatures->summary & GPGME_SIGSUM_KEY_REVOKED) << endl;
	    clog << "exp key: " << (result->signatures->summary & GPGME_SIGSUM_KEY_EXPIRED) << endl;
	    clog << "exp sig: " << (result->signatures->summary & GPGME_SIGSUM_SIG_EXPIRED) << endl;
	    clog << "no key: " << (result->signatures->summary & GPGME_SIGSUM_KEY_MISSING) << endl;
	    clog << "old crl: " << (result->signatures->summary & GPGME_SIGSUM_CRL_TOO_OLD) << endl;
	    clog << "no crl: " << (result->signatures->summary & GPGME_SIGSUM_CRL_MISSING) << endl;
	    clog << "bad policy: " << (result->signatures->summary & GPGME_SIGSUM_BAD_POLICY) << endl;
	    clog << "syserr: " << (result->signatures->summary & GPGME_SIGSUM_SYS_ERROR) << endl;
	    
	    clog << "no err: " << (result->signatures->status & GPG_ERR_NO_ERROR) << endl;
	    clog << "exp sig: " << (result->signatures->status & GPG_ERR_SIG_EXPIRED) << endl;
	    clog << "exp key: " << (result->signatures->status & GPG_ERR_KEY_EXPIRED) << endl;
	    clog << "rev cert: " << (result->signatures->status & GPG_ERR_CERT_REVOKED) << endl;
	    clog << "general err: " << (result->signatures->status & GPG_ERR_GENERAL) << endl;
	    clog << "BAD: " << (result->signatures->status & GPG_ERR_BAD_SIGNATURE) << endl;
	    clog << "no pubkey: " << (result->signatures->status & GPG_ERR_NO_PUBKEY) << endl;
	    
	    clog << "timestamp: " << result->signatures->timestamp << endl;
	    clog << "expires: " << result->signatures->exp_timestamp << endl;
	    clog << "reason: " << gpgme_strerror(result->signatures->validity_reason) << endl;
	    clog << "next ptr: " << result->signatures->next << endl;
	}
    
	add_gpg_headers(email, result);
	add_trust_headers(email, result->signatures->fpr);

	gpgme_release(ctx);
    quit(email);
}
