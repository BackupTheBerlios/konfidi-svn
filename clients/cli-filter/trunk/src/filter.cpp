
#include <gpgme.h>


#include <iostream>
#include <fstream>
#include <vector>
#include <mimetic/mimetic.h>

using namespace std;
using namespace mimetic;


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


int main(int argc, char* argv[]) {

    ios_base::sync_with_stdio(false);        // optimization
    MimeEntity message(cin);           // parse and load message
    
    if (message.header().hasField("X-Trust-Email"))
    {
        cerr << "warning: malformed email " + message.header().messageid().str() + ": already has a X-Trust-Email header!" << endl;
    }
    
    if (message.header().contentType() 1= "multipart/signed") {
        cerr << "warning: email " + message.header().messageid().str() + " is not multipart/signed, it is: " << message.header().contentType().str() << endl;
        exit(3);
    }
	if (message.body().parts().size() != 2) {
        cerr << "warning: email " + message.header().messageid().str() + " doesn't have 2 parts, it has " << message.body().parts().size() << endl;
        exit(3);
	}
	string text = message.body().parts().front()->body();
    MimeEntity last_part = *message.body().parts().back();
    if (last_part.header().contentType().type() != "application" ||
    	last_part.header().contentType().subtype() != "pgp-signature") {
    	cerr << "2nd part of message isn't application/pgp-signature, it is: " << last_part.header().contentType().str() << endl;
        exit(2);
    }
	string sig = last_part.body();
    
    
    gpgme_error_t err;
    gpgme_ctx_t ctx;
    err = gpgme_new(&ctx);
    fail_if_err(err);
    cout << "did ctx" << endl;
    
    gpgme_data_t sig_data;
    err = gpgme_data_new_from_mem(&sig_data, sig.c_str(), sig.length(), 1);
    fail_if_err(err);
    gpgme_data_t text_data;
    err = gpgme_data_new_from_mem(&text_data, text.c_str(), text.length(), 1);
    fail_if_err(err);
    cout << "did data" << endl;

    
    string sig_header = "";
    err = gpgme_op_verify(ctx, sig_data, text_data, NULL);
    fail_if_err(err);
    cout << "did ver" << endl;
    
    if (err == GPG_ERR_NO_ERROR) {
        message.header().field("X-PGP-Signature").value("valid");
    } else {
        message.header().field("X-PGP-Signature").value("invalid, " + err);
    }
    gpgme_verify_result_t result = gpgme_op_verify_result (ctx);
    cout << "did res" << endl;
    gpgme_key_t r_key;
    gpgme_get_key(ctx, result->signatures->fpr, &r_key, 0);
    cout << "did key " << result->signatures->fpr << endl;
    
    
    string ourheaders = "X-Trust-Email: **";
    //cout << headers << "\n" << sig_header + "\n" + ourheaders << body << flush;
    
    return 0;
}
