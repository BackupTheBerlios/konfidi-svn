
#include <gpgme.h>


#include <iostream>
#include <fstream>
#include <vector>

using namespace std;


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


/** from http://oopweb.com/CPP/Documents/CPPHOWTO/Volume/C++Programming-HOWTO-7.html */
void Tokenize(const string& str,
                      vector<string>& tokens,
                      const string& delimiters = " ")
{
    // Skip delimiters at beginning.
    string::size_type lastPos = str.find_first_not_of(delimiters, 0);
    // Find first "non-delimiter".
    string::size_type pos     = str.find_first_of(delimiters, lastPos);

    while (string::npos != pos || string::npos != lastPos)
    {
        // Found a token, add it to the vector.
        tokens.push_back(str.substr(lastPos, pos - lastPos));
        // Skip delimiters.  Note the "not_of"
        lastPos = str.find_first_not_of(delimiters, pos);
        // Find next "non-delimiter"
        pos = str.find_first_of(delimiters, lastPos);
    }
}

int main(int argc, char* argv[]) {
    // slurp stdin
    char c;
    string stdin;
    while((c=cin.get())!=EOF) {
        stdin += c;
    }
    
    string headers;
    string body;
    unsigned int headers_end = stdin.find("\n\n");
    if (headers_end == string::npos) {
        cerr << "malformed email: no \\n\\n found" << endl;
        exit(1);
    }
    headers = stdin.substr(0, headers_end);
    body = stdin.substr(headers_end);
    
    
    //vector<string> parts;
    //Tokenize(s, tokens, "\n");
    
    if (headers.find("X-Trust-Email:") != string::npos) {
        cerr << "malformed email: already has a X-Trust-Email header!" << endl;
        exit(1);
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
        sig_header = "X-PGP-Signature: valid";
    } else {
        sig_header = "X-PGP-Signature: invalid: " + err;
    }
    gpgme_verify_result_t result = gpgme_op_verify_result (ctx);
    cout << "did res" << endl;
    gpgme_key_t r_key;
    gpgme_get_key(ctx, result->signatures->fpr, &r_key, 0);
    cout << "did key" << endl;
    
    
    string ourheaders = "X-Trust-Email: **";
    cout << headers << "\n" << sig_header + "\n" + ourheaders << body << flush;
    
    return 0;
}
