#!/usr/bin/env python

import jinja2
import argparse
import os, shutil
import inspect
import tarfile
import myos

import pbs.classes.Static
import pbs.settings

#from pbs.Library import *
#from pbs.Static import *
#from pbs.Dynamic import *
#from pbs.Executable import *

#compiler_folder = os.path.dirname(__file__)

#global master_config_dir

class Project(object):
    def __init__(self, root_dir, args):
        self.root_dir = root_dir
        self.args = args
    
        self.compiler_dir = pbs.settings.PBS_DIR
        self.compiler_file = os.path.join(self.compiler_dir, "pbs/gen.py")

        self.projects = {}
        self.makefiles = []
        self.libraries = {}
        self.defines = []
        self.config_files = []
        
        self.build_dir = os.getcwd()

    def get_root_dir(self):
        return self.root_dir
    def get_build_dir(self):
        return self.build_dir

    def get_source_files(self):
        """
        return list of all source files for all projects
        """
        files = []
        for n,p in self.projects.items():
            files += p.get_c_files()
            files += p.get_c_in_files()

        return files
    def get_header_files(self):
        """
        return list of all header files for all projects
        """
        files = []
        for n,p in self.projects.items():
            files += p.get_h_files()
            files += p.get_h_in_files()

        return files


    def save_config(self):
        with open('config.txt', 'w') as f:
            f.write("root,{}".format(self.root_dir))

    def add_define(self, s):
        self.defines.append(s)

    def include(self, foldername):
        st = inspect.stack()
        s = st[1]
        caller = os.path.abspath(s[1])
        base = os.path.dirname(caller)
    
        filename = os.path.join(base,foldername,"config.py")
    
        self.config_files.append(filename)
    
        execfile(filename)
  
        
    def make_targets(self, target):
        s = "\t@$(MAKE) -f {{}} {} --no-print-directory".format(target)
        ret = "\n".join(list(s.format(m) for m in self.makefiles))
        return ret
   
    def list_variable(self, name, var):
        s = "{}  =\n".format(name)

        s += "\n".join("{}  += {}".format(name, v) for v in var)

        return s

    def write_info_file(self):
        pbs.func.mkdir(os.path.join(self.build_dir, "files"))
        
        
        self.render(
                os.path.join(self.compiler_dir, "makefiles", "vars.make"),
                os.path.join(self.build_dir, "files", "vars.make"))

    def render(self, f_in, f_out):

        var_make_files = self.list_variable("make_files", self.makefiles)
        var_conf_files = self.list_variable("conf_files", self.config_files)
        var_projects   = self.list_variable("projects", (p.name for p in self.projects.values()))

       	make_lines          = self.make_targets("")
	clean_lines         = self.make_targets("clean")
	clean_pre_lines     = self.make_targets("clean_pre")
	depend_lines        = self.make_targets("depend")
	depend_clean_lines  = self.make_targets("dependclean")
	precompiler_lines   = self.make_targets("precompiler")
       	help_lines          = self.make_targets("help")
       	doc_lines           = self.make_targets("doc")
        
        inc_dirs            = " ".join(p.inc_dir for n,p in self.libraries.items())
        
	config_file_str     = " ".join(self.config_files)
	makefiles_str       = " ".join(self.makefiles)

        targets, phonies = self.get_targets_and_phonies()

        tmp1 = list(".PHONY: " + ph for ph in phonies)
        tmp2 = list(".PHONY: " + ph + "_PRE" for ph in phonies)
	phony_lines = "\n".join(tmp1 + tmp2)
        
        with open(f_in, 'r') as f:
	    temp = jinja2.Template(f.read())
	    
	out = temp.render(
                    build_dir           = self.build_dir,
	            config_file_str     = config_file_str,
	            compiler_file       = self.compiler_file,
	            clean_lines         = clean_lines,
	            clean_pre_lines     = clean_pre_lines,
	            depend_lines        = depend_lines,
	            depend_clean_lines  = depend_clean_lines,
	            doc_lines           = doc_lines,
	            help_lines          = help_lines,
                    inc_dirs            = inc_dirs,
	            makefiles_str       = makefiles_str,
	            make_lines          = make_lines,
	            phony_lines         = phony_lines,
	            precompiler_lines   = precompiler_lines,
                    root_dir            = self.root_dir,
	            targets             = targets,
                    var_make_files      = var_make_files,
                    var_conf_files      = var_conf_files,
                    var_projects        = var_projects,
	            )
	    
	with open(f_out,'w') as f:
	    f.write(out)

    def get_targets_and_phonies(self):
	targets = ""
	phonies = []

	for p in self.projects.values():
	    if not p.name in phonies:
	        phonies.append(p.name)

	for p in self.projects.values():
	
	    reqs = " ".join(r.l.name for r in p.reqs)
	    reqs_pre = " ".join(r.l.name+"_PRE" for r in p.reqs)
	
	    if isinstance(p, pbs.classes.Executable.Executable):
	        targets += p.name + "_PRE: " + reqs_pre + "\n"
	    else:
	        targets += p.name + "_PRE: " + reqs + " " + reqs_pre + "\n"
	    
	    for r in p.reqs:
	        if not r.l.name in phonies:
	            phonies.append(r.l.name)
	    
	    targets += "\t@$(MAKE) -f {} --no-print-directory\n".format(
                    p.get_makefile_filename_out())
	
	    targets += "\n"

        for p in self.projects.values():
	    targets += p.name + ": " + p.name + "_PRE " + " ".join(t for t in p.tests) + "\n"
	    for test in p.tests:
	        targets += "\t./"+test+"\n"
	    targets += "\n"

        return targets, phonies

    def execute(self):
	main_config = os.path.join(self.root_dir, "config.py")

        # run the main config file
        execfile(main_config, {'self': self})

        self.config_files.append(main_config)

    def do(self):
       
        self.execute()
	
        try:
    	    if self.args.p:
	        l = self.libraries[self.args.p[0]]
	        l.preprocess(self.args.p[1], self.args.p[2])
	
	    else:
	        f_in = os.path.join(
                    self.compiler_dir,
                    "makefiles",
                    "Makefile_master.in")
	    
                self.render(f_in, "Makefile")

                self.write_info_file()

                self.render(
                    os.path.join(self.compiler_dir, "Doxyfile_all"),
                    os.path.join(self.build_dir, "Doxyfile"))
        except:
            pass
    
    def clean(self):
        print "clean"
        for n,p in self.projects.items():
            print n
            p.clean()
    def get_build_sequence(self):
        pass

    def bundle(self):
        
        try:
            shutil.rmtree('bundle')
        except OSError:
            pass

        os.mkdir('bundle')

        for n,p in self.projects.items():
            src = p.get_binary_file()
            h,t = os.path.split(src)
            dst = os.path.join('bundle', t)
    
            print "copy",src," -> ",dst

            shutil.copy(src, dst)

            p.make_binary_links('bundle')
        
        # copy script folder
        src = os.path.join(self.get_root_dir(), 'scripts', 'install')
        dst = os.path.join(self.get_build_dir(), 'bundle', 'script')
        shutil.copytree(src, dst)

        # copy share folder
        src = os.path.join(self.get_root_dir(), 'share')
        dst = os.path.join(self.get_build_dir(), 'bundle', 'share')
        shutil.copytree(src, dst)
        

        # compress
        print "open"
        tar = tarfile.open('bundle.tar.gz', 'w:gz')
        print "add"
        tar.add("bundle")
        print "close"
        tar.close()
        print "done"


