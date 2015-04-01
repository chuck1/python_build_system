
from pbs.Library import *

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
        self.inc_dirs.append(os.path.join(self.build_dir, "process", "inc"))
    def get_build_dir(self):
        return os.path.join(self.root,"build")

    def get_makefile_filename_out(self):
        return os.path.join(self.get_build_dir(), "Makefile")

    def make(self):
        #print "library"

        projects.append(self)

        inc_str       = " ".join(list("-I" + s for s in self.get_include_dirs_required()))
        lib_short_str = " ".join(list(self.get_libraries_short_required()))
        lib_long_str  = " ".join(list(self.get_libraries_long_required()))
        lib_link_str  = " ".join(list("-l" + s for s in self.get_libraries_required()))

        lib_dir_str   = " ".join(list(self.get_library_dirs_required()))

        define_str = " ".join(list("-D" + d for d in global_defines))
       
        print "defines " + define_str
        
        with open(os.path.join(compiler_dir, "makefiles", "Makefile_executable.in")) as f:
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
                lib_dir_str = lib_dir_str,
                compiler_dir = compiler_dir
                )

        mkdir(self.build_dir)
        makefile = os.path.join(self.build_dir, "Makefile")
        makefiles.append(makefile)
        with open(makefile,'w') as f:
            f.write(out)

