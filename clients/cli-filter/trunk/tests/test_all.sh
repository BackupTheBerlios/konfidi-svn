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

ls plain.txt | while read testcase
do
	$APP $* < $testcase 2>/dev/null | sort | comm -1 -2 sort $(namename $testcase).headers -
	
done