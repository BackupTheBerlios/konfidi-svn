
#ifndef _options_h
#define _options_h

#include <string>
using namespace std;

/** static class which aggregates commandline and file options **/
class Options
{
protected:
	Options();
public:
	static bool verbose;
	static string source_fingerprint;
	static string trust_server_url;
	static string trust_server_params;
	
	static void process_args(int argc, char* argv[]);
	static void load_config_file();
};

#endif
