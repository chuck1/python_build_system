#!/usr/bin/env python

import jinja2
import argparse
import os
import inspect
import myos

import pbs.classes.Static

#from pbs.Library import *
#from pbs.Static import *
#from pbs.Dynamic import *
#from pbs.Executable import *

#compiler_folder = os.path.dirname(__file__)

#global master_config_dir

class Project(object):
    def __init__(self, config_dir, args):
        self.config_dir = config_dir
        self.args = args
    
        self.compiler_dir = "/home/chuck/git/python_build_system"
        self.compiler_file = os.path.join(self.compiler_dir, "compiler.py")

        self.projects = []
        self.makefiles = []
        self.libraries = {}
        self.defines = []
        self.config_files = []
        
    def add_define(self, s):
        #print s
        self.defines.append(s)

    def include(self, foldername):
        st = inspect.stack()
        s = st[1]
        caller = os.path.abspath(s[1])
        base = os.path.dirname(caller)
    
        filename = os.path.join(base,foldername,"config.py")
    
        self.config_files.append(filename)
    
        execfile(filename)
    
    def do(self):

	main_config = os.path.join(self.args.root, "config.py")
        
        execfile(main_config, {'self': self})
	
	config_files.append(main_config)
	
	make_lines         = "\n".join(list("\t@$(MAKE) -f " + m + " --no-print-directory" for m in makefiles))
	clean_lines        = "\n".join(list("\t@$(MAKE) -f " + m + " clean --no-print-directory" for m in makefiles))
	depend_lines       = "\n".join(list("\t@$(MAKE) -f " + m + " depend --no-print-directory" for m in makefiles))
	depend_clean_lines = "\n".join(list("\t@$(MAKE) -f " + m + " dependclean --no-print-directory" for m in makefiles))
	precompiler_lines  = "\n".join(list("\t@$(MAKE) -f " + m + " precompiler --no-print-directory" for m in makefiles))
	
	for p in projects:
	    pass
	
	phonies = []
	
	targets = ""
	#print "projects"
	for p in projects:
	    #print p.name
	
	    reqs = " ".join(r.l.name for r in p.reqs)
	    reqs_pre = " ".join(r.l.name+"_PRE" for r in p.reqs)
	
	    if isinstance(p,Executable):
	        targets += p.name + "_PRE: " + reqs_pre + "\n"
	    else:
	        targets += p.name + "_PRE: " + reqs + " " + reqs_pre + "\n"
	    
	    for r in p.reqs:
	        if not r.l.name in phonies:
	            phonies.append(r.l.name)
	    
	    targets += "\t@$(MAKE) -f {} --no-print-directory\n".format(
                    p.get_makefile_filename_out())
	
	
	    targets += "\n"
	
	for p in projects:
	    #print p.name
	    targets += p.name + ": " + p.name + "_PRE " + " ".join(t for t in p.tests) + "\n"
	    for test in p.tests:
	        targets += "\t./"+test+"\n"
	    targets += "\n"
	
	for p in projects:
	    if not p.name in phonies:
	        phonies.append(p.name)
	
	tmp1 = list(".PHONY: " + ph for ph in phonies)
        tmp2 =list(".PHONY: " + ph + "_PRE" for ph in phonies)
	phony_lines = "\n".join(tmp1 + tmp2)
	
	all2 = "all2: " + " ".join(p.name for p in projects)
	
	config_file_str = " ".join(config_files)
	makefiles_str = " ".join(makefiles)
	
	if self.args.p:
	    l = libraries[self.args.p[0]]
	
	    l.preprocess(self.args.p[1], self.args.p[2])
	
	else:
	    f_in = os.path.join(
                    compiler_dir,
                    "makefiles",
                    "Makefile_master.in")
	
	    with open(f_in, 'r') as f:
	        temp = jinja2.Template(f.read())
	    
	    out = temp.render(
	            makefiles_str       = makefiles_str,
	            compiler_file       = compiler_file,
	            make_lines          = make_lines,
	            clean_lines         = clean_lines,
	            depend_lines        = depend_lines,
	            depend_clean_lines  = depend_clean_lines,
	            config_file_str     = config_file_str,
	            targets             = targets,
	            all2                = all2,
	            phony_lines         = phony_lines,
	            precompiler_lines   = precompiler_lines
	            )
	    
	    with open("Makefile",'w') as f:
	        f.write(out)
	

def gen_func(args):
    project = Project(os.path.abspath(args.root), args)
    
    project.do()


