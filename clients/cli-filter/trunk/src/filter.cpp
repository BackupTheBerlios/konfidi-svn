#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <string>

#include <mimetic/mimetic.h>
#include <gpgme.h>

using namespace std;
using namespace mimetic;

const char* header_sig = "X-PGP-Signature";
const char* header_sig_finger = "X-PGP-Fingerprint";
const char* header_trust = "X-Trust-Email-Value";
const char* header_this_app = "X-Dmail-Client";
const char* header_this_app_value = "cli-filter 0.1";


#define fail_if_err(err)                                        \
  do                                                            \
    {                                                           \
      if (err)                                                  \
        {                                                       \
          fprintf (stderr, "%s:%d: %s: %s (%d.%d)\n",           \
                   __FILE__, __LINE__, gpg_strsource (err),     \
                   gpg_strerror (err),                          \
                   gpg_err_source (err), gpg_err_code (err));   \
          exit (1);                                             \
        }                                                       \
    }                                                           \
  while (0)

int quit(string mbox_from, MimeEntity *message, int flag=0) {
    cout << mbox_from << *message;
    cout << endl << endl << endl;
    cout << message->body() << endl;
	clog << endl;
	exit(flag);
}

void process_args(int argc, char* argv[], bool & verbose) {
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

string slurp(istream &i) {
	// read the whole message
	string whole;
	getline(i, whole, '\0');
	return whole;
}

string read_possible_From_line(istream &i) {
	// possible "From " line in mbox format
	string mbox_from;
	getline(i, mbox_from);
	if (mbox_from.substr(0, 5) != "From ") {
		string::reverse_iterator it;
		for (it = mbox_from.rbegin(); it != mbox_from.rend(); it++) {
			i.putback(*it);
		}
		i.putback(*it);
		mbox_from = "";
	} else {
		mbox_from += "\r\n";
	}
	return mbox_from;
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

void clean_headers(MimeEntity * message) {
    delete_header(&message->header(), header_sig);
    delete_header(&message->header(), header_sig_finger);
    delete_header(&message->header(), header_trust);
}

string parse_email_text(MimeEntity * message, string whole, string mbox_from) {
    if (message->header().contentType().type() != "multipart" ||
    	message->header().contentType().subtype() != "signed") {
        cerr << "warning: email " + message->header().messageid().str() + " is not multipart/signed, it is: " << message->header().contentType().str() << endl;
        message->header().field(header_sig).value("none");
        quit(mbox_from, message);
    }
	if (message->body().parts().size() != 2) {
        cerr << "warning: email " + message->header().messageid().str() + " doesn't have 2 parts, it has " << message->body().parts().size() << endl;
        message->header().field(header_sig).value("none");
        quit(mbox_from, message);
	}
	
	string boundary = "--" + message->header().contentType().param("boundary");
	// start at 1st boundary
	int text_start = whole.find(boundary)+boundary.length()+1;
	// end at 2nd boundary
	int text_end = whole.find(boundary, text_start);
	string text = whole.substr(text_start, text_end-text_start-1);
	// lf -> crlf
	int p=-1;
	while (std::string::npos != (p=text.find("\n",p+2)))
		text.replace(p,1,"\r\n");
	
	return text;
}

string parse_email_sig(MimeEntity * message, string whole, string mbox_from) {
    MimeEntity last_part = *message->body().parts().back();
    if (last_part.header().contentType().type() != "application" ||
    	last_part.header().contentType().subtype() != "pgp-signature") {
    	cerr << "2nd part of message isn't application/pgp-signature, it is: " << last_part.header().contentType().str() << endl;
        message->header().field(header_sig).value("none");
        quit(mbox_from, message);
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

void validate_from_matches_signer(MimeEntity * message, string mbox_from, gpgme_ctx_t ctx, gpgme_verify_result_t result) {
	gpgme_error_t err;
    // TODO: this is blocking, probably want to change.
    gpgme_key_t key;
	err = gpgme_get_key(ctx, result->signatures->fpr, &key, 0);
	fail_if_err(err);
	
	
	bool found_email = false;
	string from_email = message->header().from().front().mailbox() + '@' + message->header().from().front().domain();
	gpgme_user_id_t uid = key->uids;
	while (uid) {
		if (from_email == uid->email) {
			found_email = true;
		}
		uid = uid->next;
	}
	if (!found_email) {
		cerr << "no PGP uid email matched the 'From: ' on " << message->header().messageid().str() << endl;
		message->header().field(header_sig).value("from mismatch");
		quit(mbox_from, message);
	}
}

void add_headers(MimeEntity * message, string mbox_from, gpgme_verify_result_t result) {
    if (result->signatures->status == GPG_ERR_NO_ERROR) {
        message->header().field(header_sig).value("valid");
    } else {
        message->header().field(header_sig).value((string)"invalid, " + gpg_strerror(result->signatures->status));
    }
    message->header().field(header_sig_finger).value(result->signatures->fpr);
}

int main(int argc, char* argv[]) {
	bool verbose = false;
	process_args(argc, argv, verbose);

	string whole = slurp(cin);
	cin.seekg(0, ios::beg); // reset stream to beginning

	string mbox_from = read_possible_From_line(cin);
	
	// load data
	// optimization
    ios_base::sync_with_stdio(false);
    // parse and load message
    MimeEntity message(cin);
    
    clean_headers(&message);
    message.header().field(header_this_app).value(header_this_app_value);
    

	string text = parse_email_text(&message, whole, mbox_from);
	string sig = parse_email_sig(&message, whole, mbox_from);
    
    
    if (verbose)
	    clog << "processing " << message.header().messageid().str() << endl;

	// set up context
	gpgme_error_t err;
    gpgme_ctx_t ctx;
    err = gpgme_new(&ctx);
    fail_if_err(err);
    
	gpgme_verify_result_t result = gpg_validate(ctx, text, sig);
    
    if (verbose)
	    clog << "did key " << result->signatures->fpr << endl;
    
	validate_from_matches_signer(&message, mbox_from, ctx, result);
	
	
	if (verbose) {
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
    
	add_headers(&message, mbox_from, result);

    quit(mbox_from, &message);
}
