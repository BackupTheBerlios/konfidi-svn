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
	clog << endl;
	return 0;
}

int main(int argc, char* argv[]) {

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
	string text = message.body().parts().front()->body();
    MimeEntity last_part = *message.body().parts().back();
    if (last_part.header().contentType().type() != "application" ||
    	last_part.header().contentType().subtype() != "pgp-signature") {
    	cerr << "2nd part of message isn't application/pgp-signature, it is: " << last_part.header().contentType().str() << endl;
        message.header().field(header_sig).value("none");
        return quit(mbox_from, &message);
    }
	string sig = last_part.body();
    
    clog << "processing " << message.header().messageid().str() << endl;
    
    // gpgme validation
    gpgme_error_t err;
    gpgme_ctx_t ctx;
    err = gpgme_new(&ctx);
    fail_if_err(err);
    
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
    gpgme_key_t key;
    // this is blocking, probably want to change.
    gpgme_get_key(ctx, result->signatures->fpr, &key, 0);
    clog << "did key " << result->signatures->fpr << endl;
//    gpgme_key_sig_t key_sig;
//    cout << "key: " << key_sig->keyid << " " << key_sig->name << endl;
    clog << "valid: " << (result->signatures->summary & GPGME_SIGSUM_VALID) << endl;
    clog << "GREEN: " << (result->signatures->summary & GPGME_SIGSUM_GREEN) << endl;
    clog << "RED: " << (result->signatures->summary & GPGME_SIGSUM_RED) << endl;
    clog << "BAD: " << (result->signatures->status & GPG_ERR_BAD_SIGNATURE) << endl;
    clog << "GPG_ERR_NO_PUBKEY: " << (result->signatures->status & GPG_ERR_NO_PUBKEY) << endl;
    
    
    if (result->signatures->summary & GPGME_SIGSUM_VALID) {
        message.header().field(header_sig).value("valid");
    } else {
        message.header().field(header_sig).value((string)"invalid, " + gpg_strerror(result->signatures->status));
    }
    message.header().field(header_sig_finger).value(result->signatures->fpr);

    return quit(mbox_from, &message);
}
