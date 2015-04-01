#!/usr/bin/env python

import pickle
import re
import os
import glob
import myos
import sys
import subprocess
import argparse
import networkx as nx
import logging

pat = '# \d+ "([-\.\w\/]+\.(cpp|c|h|hpp))"( \d)?( \d)?( \d)?'


class Project(object):
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

def save_proj(proj):
    with open(proj.name + '.pre_proj', 'w') as f:
        pickle.dump(proj, f)

def load_proj(filename):
     with open(filename, 'r') as f:
        proj = pickle.load(f)
        return proj


def process(fileto, flags, proj):
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
            elif issys(proj.files[proj.i]):
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






def make_graph(proj, args, ):

    depflat = [d for subl in proj.dep for d in subl]
    filesclean = []
    filesp = []
    for file in proj.files:
        filesp.append(prefixed(file,args))
	file = re.sub('\.','',file)
	file = re.sub('\/','',file)
	file = re.sub('-','',file)
        #print file
        filesclean.append(file)
    
    G=nx.DiGraph()

    nodes = {}

    with open('header_dep.dot','w') as f:
	f.write('digraph {\n\trankdir=RL\n')

        # create all nodes first
	for filename,fnp,fileclean,i in zip(proj.files,filesp,filesclean,range(len(proj.files))):

            if not args.s and issys(filename):
                continue

	    if i in depflat:
                # if prefix specified, use it to shorten names
                if args.p:
                    if not filename[0:5] == '/usr/':
                        filename = os.path.relpath(filename, args.p)
		
                f.write("\t{0} [label=\"{1}\"]\n".format(
		    fileclean,
		    filename))

                #print "create node:", filename
                n = Node(fnp)
                G.add_node(n)
                nodes[filename] = n
        
        # create all edges
	for d in proj.dep:
                #print "create edge"
		f0 = filesp[d[0]]
		f1 = filesp[d[1]]
      
                try:
                    n0 = nodes[f0]
                    n1 = nodes[f1]
                except:
                    pass
                else:
                    #print f0
                    #print f1
                    f.write("\t{0} -> {1}\n".format(
	    		    filesclean[d[0]],
	    		    filesclean[d[1]]))

       
                    logging.debug("{0}--->{1}".format(n0, n1))

                    G.add_edge(n0,n1)

	f.write('}\n')

    return G


def issys(s):
    return s[0:5] == "/usr/"

def prefixed(fn, args):
    if args.p:
        if not fn[0:5] == '/usr/':
            fn = os.path.relpath(fn, args.p)
    return fn

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


class Node(object):
    def __init__(self, filename):
        self.filename = filename
    def __str__(self):
        return self.filename



def is_header(filename):
    return filename[-4:] == ".hpp"

def after_include(filename):
    #print filename
    lst = []
    h,t = os.path.split(filename)
    while t:
        #print "h",h
        #print "t",t
        if t == 'include':
            #print repr(t),"== 'include'"
            break
        else:
            lst.insert(0, t)

        h,t = os.path.split(h)

    return os.path.join(*lst)

class Item(object):
    def __init__(self, name, flags):
        self.name = name
        self.flags = flags

class Pre2(object):
    def __init__(self):
        self.items = []

def pre_to_pre2(filename):
    

    with open(filename, 'r') as f:
        lines = f.readlines()
   
    lines2 = []

    p = Pre2()
    
    for line in lines:
        m = re.search(pat, line)
	if m:
            name = m.group(1)
            #print name
            
            g = list(m.groups())
	    g = g[2:]
	    flags = []
            flags = list(int(a) for a in g if a)
	    #for a in g:
	    #    if a:
	    #        flags.append(int(a))
            
            lines2.append(line)
            
            p.items.append(Item(name, flags))

    with open(filename + "2", 'w') as f:
        #f.write("".join(lines2))
        pickle.dump(p, f)

def pre2_to_pre3(pre_file, proj):

    filename = pre_file[:-5]
        
    i = proj.index_of(filename)
        
    with open(pre_file, 'r') as f:
	#lines = f.readlines()
        p = pickle.load(f)
	
    pat = '# \d+ "([-\w\/]+\.(cpp|c|h|hpp))"( \d)?( \d)?( \d)?'
        
    #for line in lines:
    for item in p.items:
            fileto = item.name
            flags = item.flags
			
            if not issys(fileto):
                pass
                
	    process(fileto, flags, proj)

def print_degree(g, l = False, ff = None, out = sys.stdout):
    c = 0
    d = g.out_degree()

    if not d:
        return 0
    
    s = sorted(d.items(), cmp = lambda x,y: cmp(x[1],y[1]))
    s = filter(lambda x: ff(x[0].filename), s)
    if not s:
        return 0
    m = min(i[1] for i in s)
    #print "min", m
    for i in s:
        if l:
            if i[1] == m:
                c += 1
                out.write(after_include(i[0].filename) + "\n")
                #print i[1], after_include(i[0].filename)
            else:
                return c
        else:
            print i[0]
            #print i[0]
    return c

def remove_zero(g):
    
    
    d = g.out_degree()

    s = sorted(d.items(), cmp = lambda x,y: cmp(x[1],y[1]))
    m = min(i[1] for i in s)

    for i in sorted(d.items(), cmp = lambda x,y: cmp(x[1],y[1])):
        if i[1] == m:
            g.remove_node(i[0])


def graph_analysis(G, out = sys.stdout):
    i = 0
    while True:
        c = print_degree(G, True, ff=is_header, out=out)
        if c == 0:
            break
        remove_zero(G)
        i += 1


def combine_projects(project_files, proj):
    
    for p_filename in project_files:

        print "combine", p_filename

        p = load_proj(p_filename)
        
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





