import jinja2
import myos

from func import *

class Config(object):
    master_config_dir = None

compiler_dir = "/home/chuck/git/chuck1/python_build_system"
compiler_file = os.path.join(compiler_dir, "compiler.py")

makefiles = []
config_files = []

libraries = {}
global_defines = []

class Base(object):
    def __init__(self):
        self.reqs = []
    
        # specific for this project
        self.inc_dirs = []
        self.lib_dirs = []
        self.libs = []

        self.root = get_caller_dir(4)
   
    def require(self, o, lib_type = 'static'):
        if isinstance(o, list):
            for l in o:
                self.require1(l, lib_type)
        else:
            self.require1(o, lib_type)

    def require1(self, name, lib_type):
        print "require " + name
        # look for .pmake_config file in ~/usr/lib/pmake
        filename = os.path.join("/home/chuck/usr/lib/pmake", name + ".py")
        try:
            l = libraries[name + lib_type]
        except:
            #print libraries
            execfile(filename)
            l = libraries[name + lib_type]
        
        self.reqs.append(l) 

        # get info from required library

        
    #def require_library(self, l):
    #    self.inc_dirs.append(l.inc_dir)
    
    def get_libraries_required(self):
        libs = []
        for r in self.reqs:
            libs += r.libs
        return libs

    def get_libraries_short_required(self):
        libs = []
        for r in self.reqs:
            for l in r.libs:
                if l[0] != ":":
                    libs.append(l)
        return libs

    def get_libraries_long_required(self):
        libs = []
        for r in self.reqs:
            for l in r.libs:
                if l[0] == ":":
                    libs.append(l[1:])
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

        self.register()

        self.config_file = get_caller()

        #print name
        #print self.config_file
        
        self.inc_dir = os.path.join(self.root,"include")
        self.src_dir = os.path.join(self.root,"src")

        #self.build_dir = os.path.join(self.root,"build")
            
        self.inc_dirs.append(self.inc_dir)
        self.inc_dirs.append(os.path.join(self.get_build_dir(), "process", "inc"))

        # append long library name to libs
        # using long name allows build dependency
        self.libs.append(":" + self.get_binary_file())

        self.lib_dirs.append(self.get_lib_dir_arg())

    def register(self):
        libraries[self.name] = self

    def preprocess(self, filename_in, filename_out):
        print "preprocess",filename_in,filename_out

        with open(filename_in, 'r') as f:
            temp = jinja2.Template(f.read())
        
        out = self.render(temp)
        
        with open(filename_out, 'w') as f:
            f.write(out)

    def render(self, temp):
        
        out = temp.render(
                build_dir         = self.get_build_dir(),
                src_dir           = self.src_dir,
                master_config_dir = Config.master_config_dir,
                name              = self.name,
                )

        return out

    def render2(self, fn_in, fn_out):
        #print "library"
        
        inc_str = " ".join(list("-I" + s for s in (self.get_include_dirs_required() + self.inc_dirs)))
    
        define_str = " ".join(list("-D" + d for d in global_defines))

        # only for dynamic
        lib_short_str = " ".join(list(self.get_libraries_short_required()))
        lib_long_str  = " ".join(list(self.get_libraries_long_required()))
        lib_link_str  = " ".join(list("-l" + s for s in self.get_libraries_required()))
        lib_dir_str   = " ".join(list(self.get_library_dirs_required()))

        #print "defines " + define_str
        
        with open(fn_in, 'r') as f:
            temp = jinja2.Template(f.read())
        
        out = temp.render(
                inc_str           = inc_str,
                define_str        = define_str,
                inc_dir           = self.inc_dir,
                src_dir           = self.src_dir,
                binary_file       = self.get_binary_file(),
                build_dir         = self.get_build_dir(),
                master_config_dir = Config.master_config_dir,
                compiler_dir      = compiler_dir,
                lib_long_str      = lib_long_str,
                lib_link_str      = lib_link_str,
                lib_dir_str       = lib_dir_str,
                project_name      = self.name,
                makefile          = self.get_makefile_filename_out()
                )
    
        with open(fn_out,'w') as f:
            f.write(out)
       

    def make(self):
        #print "library"

        mkdir(os.path.dirname(self.get_makefile_filename_out()))

        makefiles.append(self.get_makefile_filename_out())

        self.render2(
                os.path.join(compiler_dir, self.get_makefile_template()),
                self.get_makefile_filename_out())



