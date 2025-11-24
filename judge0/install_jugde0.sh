#!/bin/bash
#Judge0 uses isolate as it's sandbox.
#API usage: https://medium.com/dsckiit/make-your-own-online-compiler-in-react-%EF%B8%8F-b06bc29dd202
wget https://github.com/judge0/judge0/releases/download/v1.13.0-extra/judge0-v1.13.0-extra.zip
unzip judge0-v1.13.0-extra.zip
mv judge0-v1.13.0-extra/* .
rm -r judge0-v1.13.0-extra
rm judge0-v1.13.0-extra.zip
