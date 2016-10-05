#!/bin/bash

dir=`basename $PWD`
url=`charm push . trusty/$dir | grep url | cut -f2 -d' '`
echo "pushed url: $url"

charm publish $url
charm grant $url everyone
