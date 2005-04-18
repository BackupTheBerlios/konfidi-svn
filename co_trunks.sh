#!/bin/bash

#
# To run this (without even checking it out!) execute:
#
# mkdir konfidi; cd konfidi # this is an umbrella dir for all the konfidi apps
# svn cat svn+ssh://svn.berlios.de/svnroot/repos/konfidi/co_trunks.sh | bash
#

# You can override BASE and TBT like this:
# svn cat svn+ssh://svn.berlios.de/svnroot/repos/konfidi/co_trunks.sh | TBT=tags/1.0-beta bash

if [ ! "$BASE" ]
then
        BASE=svn+ssh://svn.berlios.de/svnroot/repos/konfidi
fi
if [ ! "$TBT" ]
then
        TBT=trunk
fi

####
####

svn co $BASE/paper
svn co $BASE/presentation
svn co $BASE/clients/simple clients/simple
for app in clients/cli-filter foafserver frontend tests trustserver schema
do
        svn co $BASE/$app/$TBT $app
done
