#!/bin/bash

# You can override BASE and TBT like this:
# TBT=tags/1.0-beta ./co_trunks.sh

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
