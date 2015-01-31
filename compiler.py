#!/usr/bin/env python

import jinja2
import argparse
import os
import inspect
import myos

#compiler_folder = os.path.dirname(__file__)
compiler_folder = "/home/chuck/git/chuck1/python/projects/compiler"
compiler_file = os.path.join(compiler_folder, "compiler.py")

makefiles = []
config_files = []

def get_caller():
    #print inspect.getfile(inspect.currentframe())
    #print __file__
    st = inspect.stack()
    s = st[2]
    #print s[1]
    caller = os.path.abspath(s[1])
    #print caller
    return caller

def get_caller_dir():
    #print inspect.getfile(inspect.currentframe())
    #print __file__
    st = inspect.stack()
    s = st[2]
    #print s[1]
    caller = os.path.abspath(s[1])
    dirname = os.path.dirname(caller)
    return dirname


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


libraries = {}

def mkdir(d):
    try:
        os.makedirs(d)
    except:
        pass

global_defines = []

def add_global_define(s):
    print s
    global_defines.append(s)

class Base(object):
    def __init__(self):
        self.reqs = []
    
        # specific for this project
        self.inc_dirs = []
        self.lib_dirs = []
        self.libs = []
   
    def require(self, o):
        if isinstance(o, list):
            for l in o:
                self.require1(l)
        else:
            self.require1(o)

    def require1(self, name):
        print "require " + name
        # look for .pmake_config file in ~/usr/lib/pmake
        filename = os.path.join("/home/chuck/usr/lib/pmake", name + ".py")
        try:
            l = libraries[name]
        except:
            #print libraries
            execfile(filename)
            l = libraries[name]

        self.reqs.append(l) 

        # get info from required library

        
    #def require_library(self, l):
    #    self.inc_dirs.append(l.inc_dir)
    
    def get_libraries_required(self):
        libs = []
        for r in self.reqs:
            libs += r.libs
        return libs
        
    def get_library_dirs_required(self):
        lib_dirs = []
        for r in self.reqs:
            lib_dirs += r.lib_dirs
        return lib_dirs

    def get_include_dirs_required(self):
        inc_dirs = []
        for r in self.reqs:
            inc_dirs += r.inc_dirs
        return inc_dirs


class Library(Base):
    def __init__(self, name):
        super(Library, self).__init__()

        self.name = name
        
        libraries[name] = self
        
        self.config_file = get_caller()

        #print name
        #print self.config_file
        
        self.root = get_caller_dir()
        
        self.inc_dir = os.path.join(self.root,"include")
        self.src_dir = os.path.join(self.root,"src")

        self.build_dir = os.path.join(self.root,"build")
            
        self.inc_dirs.append(self.inc_dir)
        self.inc_dirs.append(os.path.join(self.build_dir, "processed", "include"))

        self.libs.append(self.name)
        self.lib_dirs.append(self.build_dir)

        self.binary_file = os.path.join(self.build_dir, "lib" + self.name + ".a")

        headers_in = list(myos.glob(".*\\.hpp\\.in", self.inc_dir))
        
        self.process(headers_in)

    def register(self):
        libraries[self.name] = self

    def header_in_to_processed(self, i):
        ir = os.path.relpath(i, self.inc_dir)
        print ir
        
        file_out_rel,_ = os.path.splitext(ir)

        print file_out_rel
       
        file_out = os.path.join(self.build_dir, "processed", "include", file_out_rel)

        return file_out

    def process(self, filenames):
        for filename in filenames:

            o = self.header_in_to_processed(filename)

            with open(filename, 'r') as f:
                temp = jinja2.Template(f.read())

            out = self.render(temp)

            mkdir(os.path.dirname(o))

            with open(o, 'w') as f:
                f.write(out)

    def render(self, temp):
        
        out = temp.render(
            src_dir = self.src_dir,
            build_dir = self.build_dir
            )

        return out


    def make(self):
        #print "library"
        
        inc_str = " ".join(list("-I" + s for s in (self.get_include_dirs_required() + self.inc_dirs)))
    
        define_str = " ".join(list("-D" + d for d in global_defines))
        
        print "defines " + define_str
        
        with open(os.path.join(compiler_folder, "Makefile.in")) as f:
            temp = jinja2.Template(f.read())
        
        out = temp.render(
                inc_str=inc_str,
                define_str = define_str,
                src_dir=self.src_dir,
                binary_file = self.binary_file,
                build_dir=self.build_dir
                )
    
        mkdir(self.build_dir)
        
        makefile = os.path.join(self.build_dir, "Makefile")
        
        makefiles.append(makefile)
    
        with open(makefile,'w') as f:
            f.write(out)
    
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
        self.inc_dirs.append(os.path.join(self.build_dir, "processed", "include"))

    def make(self):
        #print "library"
        
        inc_str     = " ".join(list("-I" + s for s in self.get_include_dirs_required()))
        lib_str     = " ".join(list("-l" + s for s in self.get_libraries_required()))
        lib_dir_str = " ".join(list("-L" + s for s in self.get_library_dirs_required()))

        define_str = " ".join(list("-D" + d for d in global_defines))
       
        print "defines " + define_str
        
        with open(os.path.join(compiler_folder, "Makefile_executable.in")) as f:
            temp = jinja2.Template(f.read())
        
        out = temp.render(
                inc_str=inc_str,
                define_str = define_str,
                src_dir=self.src_dir,
                build_dir=self.build_dir,
                binary_file = self.binary_file,
                lib_str = lib_str,
                lib_dir_str = lib_dir_str
                )
    
        mkdir(self.build_dir)
        
        makefile = os.path.join(self.build_dir, "Makefile")
        
        makefiles.append(makefile)
    
        with open(makefile,'w') as f:
            f.write(out)



parser = argparse.ArgumentParser()
parser.add_argument('root')
args = parser.parse_args()

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

config_file_str = " ".join(config_files)
makefiles_str = " ".join(makefiles)

with open(os.path.join(compiler_folder, "Makefile_master.in"),'r') as f:
    temp = jinja2.Template(f.read())


out = temp.render(
        makefiles_str = makefiles_str,
        compiler_file = compiler_file,
        make_lines = make_lines,
        clean_lines = clean_lines,
        depend_lines = depend_lines,
        config_file_str = config_file_str
        )

with open("Makefile",'w') as f:
    f.write(out)

        


