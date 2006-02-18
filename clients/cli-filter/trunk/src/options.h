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
	static bool version;
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
