
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


void printMimeStructure(MimeEntity* pMe, int tabcount = 0)
{
	Header& h = pMe->header();                   // get header object
	for(int c = tabcount; c > 0; --c)            // indent nested entities
		cout << "    ";                      //
	cout << h.contentType() << endl;             // prints Content-Type
	MimeEntityList& parts = pMe->body().parts(); // list of sub entities obj
	// cycle on sub entities list and print info of every item
	MimeEntityList::iterator mbit = parts.begin(), meit = parts.end();
	for(; mbit != meit; ++mbit)
		printMimeStructure(*mbit, 1 + tabcount);
}

int main(int argc, char* argv[]) {

    ios_base::sync_with_stdio(false);        // optimization
    MimeEntity message(cin);           // parse and load message
    
    //printMimeStructure(&message);
    
    cout << message.header().from() << endl;
    cout << message.header().field("User-Agent") << endl;
    cout << message.header().messageid().str() << endl;
    if (message.header().hasField("X-Trust-Email"))
    {
        cerr << "warning: malformed email " + message.header().messageid().str() + ": already has a X-Trust-Email header!" << endl;
    }
    
    MimeEntity last_part = *message.body().parts().back();
    cout << last_part.header().contentType().type() << last_part.header().contentType().subtype() << endl;
    ContentType type_pgpsig("application", "pgp-signature");
    if (last_part.header().contentType() == type_pgpsig) {
        cout << "equals!" << endl;
    }
    
    /*gpgme_error_t gpgme_op_verify (gpgme_ctx_t CTX,
           gpgme_data_t SIG, gpgme_data_t SIGNED_TEXT,
           gpgme_data_t PLAIN)
    */
    
    gpgme_error_t err;
    gpgme_ctx_t ctx;
    err = gpgme_new(&ctx);
    fail_if_err(err);
    cout << "did ctx" << endl;
    
    string sig_buffer("sig_buffersig_buffersig_buffersig_buffersig_buffersig_buffersig_buffersig_buffersig_buffer");
    string text_buffer("text_buffertext_buffertext_buffertext_buffertext_buffertext_buffer");
    
    gpgme_data_t sig;
    err = gpgme_data_new_from_mem(&sig, sig_buffer.c_str(), sig_buffer.length(), 1);
    fail_if_err(err);
    gpgme_data_t text;
    err = gpgme_data_new_from_mem(&text, text_buffer.c_str(), text_buffer.length(), 1);
    fail_if_err(err);
    cout << "did data" << endl;

    
    string sig_header = "";
    err = gpgme_op_verify(ctx, sig, text, NULL);
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
    cout << "did key" << endl;
    
    
    string ourheaders = "X-Trust-Email: **";
    //cout << headers << "\n" << sig_header + "\n" + ourheaders << body << flush;
    
    return 0;
}
