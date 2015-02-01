#!/usr/bin/env python

import jinja2
import argparse
import os
import inspect
import myos

from Library import *

#compiler_folder = os.path.dirname(__file__)



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

    
class Executable(Base):
    def __init__(self, name):
        super(Executable, self).__init__()

        print "executable " + name

        self.name = name
        
        self.config_file = get_caller()

        #print name
        #print self.config_file
        
        self.root = get_caller_dir()
        
        self.inc_dir = os.path.join(self.root,"include")
        self.src_dir = os.path.join(self.root,"src")

        self.build_dir = os.path.join(self.root,"build")
       
        self.binary_file = name

        self.inc_dirs.append(self.inc_dir)
        self.inc_dirs.append(os.path.join(self.build_dir, "processed", "inc"))

    def make(self):
        #print "library"
        
        inc_str       = " ".join(list("-I" + s for s in self.get_include_dirs_required()))
        lib_short_str = " ".join(list(self.get_libraries_short_required()))
        lib_long_str  = " ".join(list(self.get_libraries_long_required()))
        lib_link_str  = " ".join(list("-l" + s for s in self.get_libraries_required()))
        lib_dir_str   = " ".join(list("-L" + s for s in self.get_library_dirs_required()))

        define_str = " ".join(list("-D" + d for d in global_defines))
       
        print "defines " + define_str
        
        with open(os.path.join(compiler_folder, "Makefile_executable.in")) as f:
            temp = jinja2.Template(f.read())
        
        out = temp.render(
                inc_str = inc_str,
                define_str = define_str,
                inc_dir = self.inc_dir,
                src_dir = self.src_dir,
                build_dir=self.build_dir,
                binary_file = self.binary_file,
                lib_long_str = lib_long_str,
                lib_link_str = lib_link_str,
                lib_dir_str = lib_dir_str
                )
    
        mkdir(self.build_dir)
        
        makefile = os.path.join(self.build_dir, "Makefile")
        
        makefiles.append(makefile)
    
        with open(makefile,'w') as f:
            f.write(out)



parser = argparse.ArgumentParser()
parser.add_argument('root')
parser.add_argument('-p', nargs=3)
args = parser.parse_args()


master_config_dir = os.path.abspath(args.root)

main_config = os.path.join(args.root, "config.py")

execfile(main_config)

#print makefiles

config_files.append(main_config)

#for l in libraries.values():
#    config_files.append(l.config_file)

#print config_files


make_lines   = "\n".join(list("\t@$(MAKE) -f " + m + " --no-print-directory" for m in makefiles))
clean_lines  = "\n".join(list("\t@$(MAKE) -f " + m + " clean --no-print-directory" for m in makefiles))
depend_lines = "\n".join(list("\t@$(MAKE) -f " + m + " depend --no-print-directory" for m in makefiles))
depend_clean_lines = "\n".join(list("\t@$(MAKE) -f " + m + " dependclean --no-print-directory" for m in makefiles))

config_file_str = " ".join(config_files)
makefiles_str = " ".join(makefiles)

if args.p:
    l = libraries[p[0]]

    l.preprocess(p[1], p[2])
    
else:
    with open(os.path.join(compiler_folder, "Makefile_master.in"),'r') as f:
        temp = jinja2.Template(f.read())
    
    out = temp.render(
            makefiles_str = makefiles_str,
            compiler_file = compiler_file,
            make_lines = make_lines,
            clean_lines = clean_lines,
            depend_lines = depend_lines,
            depend_clean_lines = depend_clean_lines,
            config_file_str = config_file_str
            )
    
    with open("Makefile",'w') as f:
        f.write(out)

        


