import jinja2
import myos

from func import *

class Config(object):
    master_config_dir = None

compiler_dir = "/home/chuck/git/chuck1/python_build_system"
compiler_file = os.path.join(compiler_dir, "compiler.py")

projects = []
makefiles = []
config_files = []

libraries = {}
global_defines = []

class Req(object):
    def __init__(self, l, whole):
        self.l = l
        self.whole = whole

class Base(object):
    def __init__(self):
        self.reqs = []
    
        # specific for this project
        self.inc_dirs = []
        self.lib_dirs = []
        self.libs = []

        self.tests = []

        self.root = get_caller_dir(4)
   
    def require(self, o, lib_type = 'static', whole = False):
        if isinstance(o, list):
            for l in o:
                self.require1(l, lib_type, whole)
        else:
            self.require1(o, lib_type, whole)

    def require1(self, name, lib_type, whole):
        print "require " + name
        # look for .pmake_config file in ~/usr/lib/pmake
        filename = os.path.join("/home/chuck/usr/lib/pmake", name + ".py")
        try:
            l = libraries[name + lib_type]
        except:
            #print libraries
            execfile(filename)
            l = libraries[name + lib_type]
        
        self.reqs.append(Req(l, whole)) 

        # get info from required library

        
    #def require_library(self, l):
    #    self.inc_dirs.append(l.inc_dir)
    
    
    def get_libraries_required(self, whole = False):
        libs = []
        for r in self.reqs:
            if(r.whole == whole):
                libs += r.l.libs
        return libs

    def get_libraries_short_required(self):
        libs = []
        for r in self.reqs:
            for l in r.l.libs:
                if l[0] != ":":
                    libs.append(l)
        return libs

    def get_libraries_long_required(self):
        libs = []
        for r in self.reqs:
            for l in r.l.libs:
                if l[0] == ":":
                    libs.append(l[1:])
        return libs
        
    def get_library_dirs_required(self):
        lib_dirs = []
        for r in self.reqs:
            lib_dirs += r.l.lib_dirs
        return lib_dirs

    def get_include_dirs_required(self):
        inc_dirs = []
        for r in self.reqs:
            inc_dirs += r.l.inc_dirs
        return inc_dirs


