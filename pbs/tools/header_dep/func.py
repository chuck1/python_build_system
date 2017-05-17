#pbs.tools.header_dep.fune!/usr/bin/env python

import pickle
import re
import os
import glob
import sys
import subprocess
import argparse
import logging

import pbs.tools.header_dep.func2

# find include lines
pat = '# \d+ "([-\.\w\/]+\.(cpp|c|h|hpp))"( \d)?( \d)?( \d)?'

class Pre3(object):
    def __init__(self, root, name):
        self.name = name
        self.dep = []
        self.files = []
        self.filetype = []
        self.i = 0
        self.root = root

    def index_of(self, fn, flags = []):
        try:
    	    i0 = self.files.index(fn)
    	    #print "header file found",h
        except:
	    self.files.append(fn)
	    self.filetype.append(flags)
        
	    i0 = len(self.files)-1
        return i0

    def save(self, filename_out):
        with open(filename_out, 'wb') as f:
            pickle.dump(self, f)

def load_pre3(filename):
     with open(filename, 'rb') as f:
        pre3 = pickle.load(f)
        return pre3


def process(fileto, flags, proj):
    """
    where the header dep magic happens

    descend/ascend into/from included files

    alters to object 'proj'
    """
    #global i
    logging.debug("process: in file {0}".format(proj.files[proj.i]))
    logging.debug("process: fileto  {0}".format(fileto))
    logging.debug("process: flags   {0}".format(flags))
    #print fileto[:4],fileto[:4]=="/usr"
    if fileto[:4]=="/usr":
	flag = 3
	#pass
    
    fileto = re.sub(proj.root,'',fileto)
    
    if 1 in flags or 3 in flags:
        h = proj.index_of(fileto, flags)

	if proj.i==h: #if i[-1]==h:
	    logging.debug("skip(already in)                 \"{0}\"".format(fileto))
	else:
	    if 3 in proj.filetype[proj.i]: #elif filetype[i[-1]]==3:
		    #print "skip(currently in system header) \"{0}\"".format(fileto)
                    logging.debug("issys {0}".format(proj.files[proj.i]))
            elif pbs.tools.header_dep.func2.issys(proj.files[proj.i]):
                    logging.debug("issys {0}".format(proj.files[proj.i]))
	    else:	
                    logging.debug("create dep")
	            newdep = [proj.i,h] #newdep = [i[-1],h]
		    if not newdep in proj.dep:
			proj.dep.append(newdep)
	
    	    logging.debug("descend   from \"{0:40}\":{1:10} to \"{2:40}\":{3}".format(
		  	    proj.files[proj.i],
			    proj.filetype[proj.i],
			    fileto,
			    flags))

	    proj.i = h #i.append(h)

    elif 2 in flags or fileto[-4:] == '.cpp': #ascend
	j = proj.index_of(fileto)

	logging.debug("ascending from \"{0:40}\":{1:10} to \"{2:40}\":{3}".format(
			proj.files[proj.i],
			proj.filetype[proj.i],
			proj.files[j],
			proj.filetype[j]))

	proj.i = j





def precom(filename):
    cmd = ['gcc', '-E', '-I.', filename]
    print "cmd=",cmd
	
    print "stdout=", filename + '.pre'

    with open(filename + '.pre', 'w') as f:
        subprocess.call(cmd, stdout=f)

    
    cmd = ['./pre_to_pre2.py', filename + '.pre']
    print cmd
    subprocess.call(cmd)

    cmd = ['./pre2_to_pre3.py', filename + '.pre2']
    print cmd
    subprocess.call(cmd)
    
def get_c_files(args):
    cfiles = list(myos.glob(".*\.c$", args.d))
    ccfiles = list(myos.glob(".*\.cpp$", args.d))
    cfiles += ccfiles
    return cfiles





class Item(object):
    def __init__(self, name, flags):
        self.name = name
        self.flags = flags

class Pre2(object):
    def __init__(self):
        self.items = []

def pre_to_pre2(filename_in, filename_out):
    """
    extract include lines
    """

    with open(filename_in, 'r') as f:
        lines = f.readlines()
   
    lines2 = []
    
    p = Pre2()
    
    for line in lines:
        m = re.search(pat, line)
	if m:
            name = m.group(1)
            #print name
            
            g = list(m.groups())[2:]
	    
            flags = list(int(a) for a in g if a)

            lines2.append(line)
            
            p.items.append(Item(name, flags))

    with open(filename_out, 'wb') as f:
        #f.write("".join(lines2))
        pickle.dump(p, f)

def combine_projects(project_files, proj):
    
    for p_filename in project_files:

        print "combine", p_filename

        p = load_pre3(p_filename)
        
        for f,ft in zip(p.files, p.filetype):
            if not f in proj.files:
                proj.files.append(f)
                proj.filetype.append(ft)
        
        for d in p.dep:

            d1 = [
                    proj.index_of(p.files[d[0]]),
                    proj.index_of(p.files[d[1]])]

            if not d1 in proj.dep:
                proj.dep.append(d1)




def pre2_to_pre3(filename_in, filename_out):

    pre3 = Pre3(__file__, filename_in)
    
    pre2_to_pre3_sub(filename_in, pre3)

    #pbs.tools.header_dep.func.save_proj(proj)
    pre3.save(filename_out)


def pre2_to_pre3_sub(pre_file, proj):

    filename = pre_file[:-5]

    i = proj.index_of(filename)

    with open(pre_file, 'r') as f:
        #lines = f.readlines()
        p = pickle.load(f)

    #pat = '# \d+ "([-\w\/]+\.(cpp|c|h|hpp))"( \d)?( \d)?( \d)?'

    #for line in lines:
    for item in p.items:
        fileto = item.name
        flags = item.flags

        if not pbs.tools.header_dep.func2.issys(fileto):
            pass

        process(fileto, flags, proj)



