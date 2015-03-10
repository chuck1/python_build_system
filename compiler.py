#!/usr/bin/env python

import jinja2
import argparse
import os
import inspect
import myos


from pbs.Library import *
from pbs.Static import *
from pbs.Dynamic import *
from pbs.Executable import *

#compiler_folder = os.path.dirname(__file__)

global master_config_dir

def include(foldername):
    #print inspect.getfile(inspect.currentframe())
    #print __file__
    st = inspect.stack()
    s = st[1]
    #print s[1]
    caller = os.path.abspath(s[1])
    #print foldername
    base = os.path.dirname(caller)

    filename = os.path.join(base,foldername,"config.py")

    config_files.append(filename)

    #print get_caller()

    #print filename

    execfile(filename)

    #print inspect.getfile(s)




def add_global_define(s):
    print s
    global_defines.append(s)
    


parser = argparse.ArgumentParser()
parser.add_argument('root')
parser.add_argument('-p', nargs=3)
args = parser.parse_args()


Config.master_config_dir = os.path.abspath(args.root)
#print "master_config_dir",master_config_dir

main_config = os.path.join(args.root, "config.py")

execfile(main_config)

#print makefiles

config_files.append(main_config)

#for l in libraries.values():
#    config_files.append(l.config_file)

#print config_files


make_lines         = "\n".join(list("\t@$(MAKE) -f " + m + " --no-print-directory" for m in makefiles))
clean_lines        = "\n".join(list("\t@$(MAKE) -f " + m + " clean --no-print-directory" for m in makefiles))
depend_lines       = "\n".join(list("\t@$(MAKE) -f " + m + " depend --no-print-directory" for m in makefiles))
depend_clean_lines = "\n".join(list("\t@$(MAKE) -f " + m + " dependclean --no-print-directory" for m in makefiles))


phonies = []

targets = ""
#print "projects"
for p in projects:
    #print p.name
    targets += p.name + ": " + " ".join(r.l.name for r in p.reqs) + "\n"
    
    for r in p.reqs:
        if not r.l.name in phonies:
            phonies.append(r.l.name)
    
    targets += "\t@$(MAKE) -f " + p.get_makefile_filename_out() + " --no-print-directory\n\n"

for p in projects:
    if not p.name in phonies:
        phonies.append(p.name)


phony_lines = "\n".join(".PHONY: " + ph for ph in phonies)

all2 = "all2: " + " ".join(p.name for p in projects)

config_file_str = " ".join(config_files)
makefiles_str = " ".join(makefiles)

if args.p:
    l = libraries[args.p[0]]

    l.preprocess(args.p[1], args.p[2])
    
else:
    with open(os.path.join(compiler_dir, "makefiles", "Makefile_master.in"),'r') as f:
        temp = jinja2.Template(f.read())
    
    out = temp.render(
            makefiles_str = makefiles_str,
            compiler_file = compiler_file,
            make_lines = make_lines,
            clean_lines = clean_lines,
            depend_lines = depend_lines,
            depend_clean_lines = depend_clean_lines,
            config_file_str = config_file_str,
            targets            = targets,
            all2               = all2,
            phony_lines        = phony_lines,
            )
    
    with open("Makefile",'w') as f:
        f.write(out)

        


