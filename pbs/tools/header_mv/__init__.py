#!/usr/bin/env python

import os
import argparse
import re
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('src', help='target file source')
parser.add_argument('dst', help='target file destination')
parser.add_argument('--prefix', help='prefix of target file (portion of the absolute path that is omitted in the include directive)')
parser.add_argument('-n', help='dry run', action='store_true')
parser.add_argument('-v', help='verbose', action='store_true')
args = parser.parse_args()

# replace instances of 'src' with 'dst' in file 'filename'
def replace(filename, src, dst):

        #print "file:",filename
        #print "src: ",repr(src)
        #print "dst: ",repr(dst)

        changed = False
        
	with open(filename, 'r') as f:

		wlines = []		
		rlines = f.readlines()
		
		i = 1
		
		for rline in rlines:
			m = re.search(src, rline)
			if m:
				#head += tail[:m.start(0)]
				#head += dst
				#tail = tail[m.end(0):]
				
                                wline = rline[:m.start(0)] + dst + rline[m.end(0):]
				
				if args.v:
                                    if not changed:
                                        print filename
                                    
        			    print "{0} : {1} > {2}".format(i, repr(rline), repr(wline))

                                changed = True
			else:
				wline = rline			
	
                        i += 1

			wlines.append(wline)
        
        if changed:
            if not args.n:
                with open(filename, 'w') as f:
		    f.writelines(wlines)

# list all file with extensions 'exts' under folder 'where'
def list_header_files(where = '.', exts = ['.hpp', '.hh', '.h', '.cpp', '.cc', '.c']):
    for dirpath, dirnames, filenames in os.walk(where):
        for filename in filenames:
	    root, ext = os.path.splitext(filename)
            if ext in exts:
                #yield os.path.join(dirpath, filename)
                yield dirpath, filename


def move_file(src, dst):
	for dirpath, filename in list_header_files():
            fullname = os.path.join(dirpath, filename)
	    if args.prefix:
    	        replace(
		        fullname,
		        os.path.relpath(src, args.prefix),
		        os.path.relpath(dst, args.prefix))
            else:
	        replace(fullname, src, dst)
	
	if args.v:
		print "move {0} > {1}".format(src, dst)
	
        # move the file
	if not args.n:
		shutil.move(src, dst)

def move_dir(src, dst):

    #print src, dst
    
    for dispath,filename in list_header_files(src):
        #print filename
        #print os.path.join(src,filename), os.path.join(dst,filename)
        move_file(
                os.path.join(src,filename),
                os.path.join(dst,filename))
	


#print list(list_header_files())



if os.path.isfile(args.src):
	move_file(args.src, args.dst)


if os.path.isdir(args.src):
	move_dir(args.src, args.dst)







