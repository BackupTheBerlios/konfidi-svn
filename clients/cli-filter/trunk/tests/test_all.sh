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

PASS="    PASS"
FAIL="    FAIL"

ls *.txt | while read testcase
do
	testname=$(namename $testcase)
	checkfile=$testname.headers
	echo $testname:
	if [ -f $checkfile ]
	then
		# run app (ignore stderr)
		# sort output
		# get lines which are common to it and checkfile
		# bytewise comparison of that with the checkfile (ignore stderr)
		# if-stmt on result of that bytewise comparison
		if $APP $* < $testcase 2>/dev/null | sort | comm -1 -2 $checkfile - | cmp $checkfile - 2>/dev/null
		then
			checknotfile=$testname.notheaders
			if [ -f $checknotfile ]
			then
				# run app (ignore stderr)
				# sort output
				# get lines which are common to it and checknotfile
				# count characters
				# compare that to "0"
				if [ "0" -eq $($APP $* < $testcase 2>/dev/null | sort | comm -1 -2 $checknotfile - | wc -c) ]
				then
					echo $PASS
				else
					echo $FAIL
				fi
			else
				echo $PASS
			fi
		else
			echo $FAIL
		fi
	else
		echo "    no check file ($checkfile)"
	fi
done
