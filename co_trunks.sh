#!/bin/bash

#
# To run this (without even checking it out!) execute:
#
# mkdir dmail; cd dmail # this is an umbrella dir for all the dmail apps
# svn cat http://brondsema.gotdns.com/svn/dmail/co_trunks.sh | bash
#

# You can override BASE and TBT like this:
# svn cat http://brondsema.gotdns.com/svn/dmail/co_trunks.sh | TBT=tags/1.0-beta bash

if [ ! "$BASE" ]
then
	BASE=https://brondsema.gotdns.com/svn/dmail
fi
if [ ! "$TBT" ]
then
	TBT=trunk
fi

####
####

svn co $BASE/tests
for app in clients/cli-filter foafserver frontend tests trustserver
do
	svn co $BASE/$app/$TBT $app
done
