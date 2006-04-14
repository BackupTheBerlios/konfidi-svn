#!/bin/bash


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
tar -cjpf $distr $svnexportdir || exit $?

echo "Deleting: $svnexportdir"
rm -rf $svnexportdir

echo "Signing: $distr"
gpg --armor --detach-sign $distr || exit $?

echo "You should now run:"
echo svn cp $url/$branchpath $url/tags/$version -m \"release $version\" || exit $?
