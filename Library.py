import jinja2
import myos

from func import *

master_config_dir = None

compiler_folder = "/home/chuck/git/chuck1/python_build_system"
compiler_file = os.path.join(compiler_folder, "compiler.py")

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
        
        libraries[name] = self
        
        self.config_file = get_caller()

        #print name
        #print self.config_file
        

        self.root = get_caller_dir()
        
        self.inc_dir = os.path.join(self.root,"include")
        self.src_dir = os.path.join(self.root,"src")

        self.build_dir = os.path.join(self.root,"build")
            
        self.inc_dirs.append(self.inc_dir)
        self.inc_dirs.append(os.path.join(self.build_dir, "processed", "inc"))


        self.binary_file = os.path.join(self.build_dir, "lib" + self.name + ".a")

        # append long library name to libs
        # long name allows build dependency
        self.libs.append(":" + self.binary_file)
        self.lib_dirs.append(self.build_dir)

        # preprocessing
        headers_in = list(myos.glob(".*\\.hpp\\.in", self.inc_dir))
        
        self.process(headers_in)

    def register(self):
        libraries[self.name] = self

    def header_in_to_processed(self, i):
        ir = os.path.relpath(i, self.inc_dir)
        print ir
        
        file_out_rel,_ = os.path.splitext(ir)

        print file_out_rel
       
        file_out = os.path.join(self.build_dir, "processed", "inc", file_out_rel)

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
                name = self.name,
                src_dir = self.src_dir,
                build_dir = self.build_dir
                )

        return out


    def make(self):
        #print "library"
        
        inc_str = " ".join(list("-I" + s for s in (self.get_include_dirs_required() + self.inc_dirs)))
    
        define_str = " ".join(list("-D" + d for d in global_defines))
        
        print "defines " + define_str
        
        with open(os.path.join(compiler_folder, "Makefile_library_static.in")) as f:
            temp = jinja2.Template(f.read())
        
        out = temp.render(
                inc_str=inc_str,
                define_str = define_str,
                inc_dir = self.inc_dir,
                src_dir = self.src_dir,
                binary_file = self.binary_file,
                build_dir=self.build_dir,
                master_config_dir = master_config_dir
                )
    
        mkdir(self.build_dir)
        
        makefile = os.path.join(self.build_dir, "Makefile")
        
        makefiles.append(makefile)
    
        with open(makefile,'w') as f:
            f.write(out)

