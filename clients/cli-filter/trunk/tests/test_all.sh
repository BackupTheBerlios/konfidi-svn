#!/bin/bash

# any arguments (e.g. -v) get passed on to APP

# *.headers must be sorted (use 'sort' command)

APP=../dmail-cli-filter

function namename()
{
  local name=${1##*/}
  local name0="${name%.*}"
  echo "${name0:-$name}"
}

ls *.txt | while read testcase
do
	testname=$(namename $testcase)
	checkfile=$testname.headers
	echo $testname:
	if [ -f $checkfile ]
	then
		if $APP $* < $testcase 2>/dev/null | sort | comm -1 -2 $checkfile - | cmp $checkfile - 2>/dev/null
		then
		  echo "    PASS"
		else
		  echo "    FAIL"
		fi
	else
		echo "    no check file ($checkfile)"
	fi
done