
#ifndef _options_h
#define _options_h

#include <string>
using namespace std;

#include <gpgme.h>

/** static class which aggregates commandline and file options **/
class Options
{
private:
	static string conf_file;
protected:
	Options();
public:
	static bool verbose;
	static string source_fingerprint;
	static string trust_server_url;
	static string trust_server_params;
	
	/** parse commandline arguments */
	static void process_args(int argc, char* argv[]);
	/** load from the configuration file */
	static void load_config_file();
	/** If possible, determine source_fingerprint from GPG private keyring.  Return success */
	static bool guess_source_fingerprint(gpgme_ctx_t);
	/** make sure we have all required options */
	static bool safety_check();
};

#endif
