#!/bin/bash


subproject=$1
version=$2
dest=$3

if [ "$subproject" == "" ] || [ "$version" == "" ]; then
    echo "Usage: $0 SUBPROJECT VERSION [DEST]"
    echo "Example:  $0 ../foafserver 1.0.0 dist"
    echo 
    echo "SUBPROJECT:   a folder having 'trunk' and 'tags' subfolders"
    echo "VERSION:      a version number"
    echo "DEST:         a folder to hold the generated distributables"
    echo "              (default '.')"
    echo
    echo "When run, this will tag a release version, build a tar.bz2 file, and sign it"
    exit
fi


if [ "$dest" == "" ]; then
    dest=.
fi

echo "Tagging $subproject/trunk as $version"
pushd $subproject >/dev/null || exit $?
svn cp trunk tags/$version || exit $?
popd >/dev/null || exit $?

projectname=`basename $subproject`
distr=$dest/$projectname-$version-src.tar.bz2

echo "Making $distr"
tar -cjpf $distr $subproject/tags/$version --exclude '.svn' || exit $?

echo "Signing $distr"
gpg --armor --detach-sign $distr || exit $?

echo "You need to commit the tagged version"