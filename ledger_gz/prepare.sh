#!/bin/bash
# create storagedir for storing gz files
# and copy leveldb index for parsing (since leveldb cannot be used concurrently on multiple processors, let's just make three copies of it, and let each processor use one copy) 
mkdir storagedir
for dir in {index,index2,index3}; do
	cp -r ~/.bitcoin/blocks/index $dir;
done
