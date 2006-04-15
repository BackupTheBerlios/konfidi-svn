#!/bin/bash
#  Copyright (C) 2006-2006 Dave Brondsema, Andrew Schamp
#  This file is part of Konfidi http://konfidi.org/
#  It is licensed under two alternative licenses (your choice):
#      1. Apache License, Version 2.0
#      2. GNU Lesser General Public License, Version 2.1
#
#
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

subproject=$1
version=$2
dest=$3

branchpath=trunk

if [ "$subproject" == "" ] || [ "$version" == "" ]; then
    echo "Usage: $0 SUBPROJECTDIR VERSION [DEST]"
    echo "Example:  $0 ../foafserver 1.0.0 dist"
    echo 
    echo "SUBPROJECTDIR:   an SVN working copy having 'trunk' and 'tags' subfolders"
    echo "VERSION:         a version number"
    echo "DEST:            a folder to hold the generated distributables"
    echo "                 (default '.')"
    echo
    echo "When run, this will tag a release version, build a tar.bz2 file, and sign it"
    exit
fi

projectname=`basename $subproject`

if [ "$dest" == "" ]; then
    dest=.
fi

url=`svn info $subproject | awk '/^URL: / {print $2}'` || exit $?
if [ "$url" == "" ]; then
    echo "$subproject does not appear to be a SVN working copy" >&2
    exit 1
fi

svnexportdir=$dest/$projectname-$version
mkdir -p $dest || exit $?
echo "Running: svn export $url/$branchpath $svnexportdir -q"
svn export $url/$branchpath $svnexportdir -q || exit $?


distr=$dest/$projectname-$version-src.tar.bz2

echo "Making: $distr"
tar -cjf $distr $svnexportdir || exit $?

echo "Deleting: $svnexportdir"
rm -rf $svnexportdir || exit $?

echo "Signing: $distr"
gpg --armor --detach-sign $distr || exit $?

echo "You should now run:"
echo svn cp $url/$branchpath $url/tags/$version -m \"release $version\"
