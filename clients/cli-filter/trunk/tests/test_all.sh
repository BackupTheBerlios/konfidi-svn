#!/bin/bash

# any arguments (e.g. -v) get passed on to APP

APP=../dmail-cli-filter

function namename()
{
  local name=${1##*/}
  local name0="${name%.*}"
  echo "${name0:-$name}"
}

ls already_has_headers.txt | while read testcase
do
	$APP $* < $testcase | comm $(namename $testcase).headers -
	
done