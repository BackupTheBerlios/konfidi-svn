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
const char* header_sig_finger = "X-PGP-Signature-Fingerprint";
const char* header_trust = "X-Trust-Email-Value";


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
	return 0;
}

int main(int argc, char* argv[]) {

	bool verbose = false;
	if (argc == 1) {
		// no args
	} else if (argc == 2 && (string)argv[1] == "-v") {
		verbose = true;
	} else {
		cerr << "Invalid argument." << endl << endl;
		cerr << "Valid arguments: " << endl;
		cerr << "\t-v\t\tverbose" << endl;
		cerr << endl << "This program accepts a single RFC2822 message (optionally with an mbox-style 'From ' first line) on stdin" << endl;
		return 1;
	}

	// read the whole message
	string whole;
	getline(cin, whole, '\0');
	cin.seekg(0, ios::beg);


	// load data
	// possible "From " line in mbox format
	// TODO: is this really necessary?
	string mbox_from;
	getline(cin, mbox_from);
	if (mbox_from.substr(0, 5) != "From ") {
		string::reverse_iterator it;
		for (it = mbox_from.rbegin(); it != mbox_from.rend(); it++) {
			cin.putback(*it);
		}
		cin.putback(*it);
		mbox_from = "";
	} else {
		mbox_from += "\r\n";
	}
	// optimization
    ios_base::sync_with_stdio(false);
    // parse and load message
    MimeEntity message(cin);
    
    // check headers
    // TODO: search, iterate through headers and delete!
    if (message.header().hasField(header_sig))
    {
	    message.header().field(header_sig).value();
    }
    if (message.header().hasField(header_sig_finger))
    {
	    message.header().field(header_sig_finger).value();
    }
    if (message.header().hasField(header_trust))
    {
        cerr << "warning: malformed email " + message.header().messageid().str() + ": already has a " + header_trust + " header!" << endl;
    }
    
    // parse text & sig
    if (message.header().contentType().type() != "multipart" ||
    	message.header().contentType().subtype() != "signed") {
        cerr << "warning: email " + message.header().messageid().str() + " is not multipart/signed, it is: " << message.header().contentType().str() << endl;
        message.header().field(header_sig).value("none");
        return quit(mbox_from, &message);
    }
	if (message.body().parts().size() != 2) {
        cerr << "warning: email " + message.header().messageid().str() + " doesn't have 2 parts, it has " << message.body().parts().size() << endl;
        message.header().field(header_sig).value("none");
        return quit(mbox_from, &message);
	}
	
	string boundary = "--" + message.header().contentType().param("boundary");
	// start at 1st boundary
	int text_start = whole.find(boundary)+boundary.length()+1;
	// end at 2nd boundary
	int text_end = whole.find(boundary, text_start);
	string text = whole.substr(text_start, text_end-text_start-1);
	// lf -> crlf
	int p=-1;
	while (std::string::npos != (p=text.find("\n",p+2)))
		text.replace(p,1,"\r\n");

    MimeEntity last_part = *message.body().parts().back();
    if (last_part.header().contentType().type() != "application" ||
    	last_part.header().contentType().subtype() != "pgp-signature") {
    	cerr << "2nd part of message isn't application/pgp-signature, it is: " << last_part.header().contentType().str() << endl;
        message.header().field(header_sig).value("none");
        return quit(mbox_from, &message);
    }
	string sig = last_part.body();
    
    if (verbose)
	    clog << "processing " << message.header().messageid().str() << endl;
    
    // gpgme validation
    gpgme_error_t err;
    gpgme_ctx_t ctx;
    err = gpgme_new(&ctx);
    fail_if_err(err);
    
    // TODO: do a local lookup first?  how often to update those?
//    err = gpgme_set_keylist_mode(ctx, GPGME_KEYLIST_MODE_EXTERN);
//    fail_if_err(err);
    
    gpgme_data_t sig_data;
    err = gpgme_data_new_from_mem(&sig_data, sig.c_str(), sig.length(), 1);
    fail_if_err(err);
    gpgme_data_t text_data;
    err = gpgme_data_new_from_mem(&text_data, text.c_str(), text.length(), 1);
    fail_if_err(err);

    
    string sig_header = "";
    err = gpgme_op_verify(ctx, sig_data, text_data, NULL);
    fail_if_err(err);
    gpgme_verify_result_t result = gpgme_op_verify_result (ctx);
    if (verbose)
	    clog << "did key " << result->signatures->fpr << endl;
    
    // this is blocking, probably want to change.
    gpgme_key_t key;
	err = gpgme_get_key(ctx, result->signatures->fpr, &key, 0);
	fail_if_err(err);
	
	bool found_email = false;
	string from_email = message.header().from().front().mailbox() + '@' + message.header().from().front().domain();
	gpgme_user_id_t uid = key->uids;
	while (uid) {
		if (from_email == uid->email) {
			found_email = true;
		}
		uid = uid->next;
	}
	if (!found_email) {
		cerr << "no PGP uid email matched the 'From: ' on " << message.header().messageid().str() << endl;
		message.header().field(header_sig).value("from mismatch");
		return quit(mbox_from, &message);
	}
	
	
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
    
    
    if (result->signatures->status == GPG_ERR_NO_ERROR) {
        message.header().field(header_sig).value("valid");
    } else {
        message.header().field(header_sig).value((string)"invalid, " + gpg_strerror(result->signatures->status));
    }
    message.header().field(header_sig_finger).value(result->signatures->fpr);

    return quit(mbox_from, &message);
}
