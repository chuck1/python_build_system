import os
import jinja2

import pbs.classes.Base
import pbs.func

class Executable(pbs.classes.Base.Base):
    def __init__(self, name, proj):
        super(Executable, self).__init__(name, proj)

        #rint "executable " + name

        self.config_file = pbs.func.get_caller()

        #rint name
        #rint self.config_file
        
        self.root = pbs.func.get_caller_dir()
        
        self.inc_dir = os.path.join(self.root,"include")
        self.src_dir = os.path.join(self.root,"src")

        self.gch_inc_dir = os.path.join(self.get_build_dir(), "gch", "include")

        self.inc_dirs.append(self.inc_dir)
        self.inc_dirs.append(os.path.join(self.get_build_dir(), "process", "inc"))

    def package(self):

        print "package:",self.name
       
        for r in self.reqs:
            print r.l, r.whole

    def get_make_targets(self):

        cargs = self.get_cargs()

        def do_binary(proj, target, deps):
            cmd = []
            cmd += ['g++'] + deps
            cmd += ['-o', target]
            cmd += cargs
            cmd += self.get_link_list()

            pbs.tools.make.call(cmd)

        yield pbs.tools.make.Target(
            self.name,
            [self.get_binary_path()],#, "precompile_{}".format(self.name)],
            None
            )
        
        yield pbs.tools.make.Target(
            self.get_binary_path(),
            list(self.get_o_files()),
            do_binary
            )

    def get_binary_file(self):
        return self.name

    def get_binary_path(self):
        return os.path.join(
                self.proj.get_build_dir(),
                self.get_binary_file()
                )

    def get_build_dir(self):
        return os.path.join(self.root,"build")

    def get_makefile_filename_out(self):
        return os.path.join(self.get_build_dir(), "Makefile")
    def get_link_list(self):
        return list("-l" + s for s in self.get_libraries_required())
    def get_link_str(self):
        return " ".join(self.get_link_list())
    def make(self):
        #rint "library"

        self.proj.projects[self.name] = self

        inc_str       = " ".join(list("-I" + s for s in self.get_include_dirs_required()))
        lib_short_str = " ".join(list(self.get_libraries_short_required()))
        lib_long_str  = " ".join(list(self.get_libraries_long_required()))
        lib_link_str  = self.get_link_str()
        lib_dir_str   = " ".join(list(self.get_library_dirs_required()))
        define_str    = " ".join(list("-D" + d for d in self.proj.defines))
       
        #rint "defines " + define_str
        
        with open(os.path.join(self.proj.compiler_dir, "makefiles", "Makefile_executable.in")) as f:
            temp = jinja2.Template(f.read())
        
        out = temp.render(
                root_dir = self.root,
                inc_str = inc_str,
                define_str = define_str,
                inc_dir = self.inc_dir,
                src_dir = self.src_dir,
                build_dir =     self.get_build_dir(),
                binary_path =   self.get_binary_path(),
                lib_long_str = lib_long_str,
                lib_link_str = lib_link_str,
                lib_dir_str = lib_dir_str,
                compiler_dir = self.proj.compiler_dir
                )

        pbs.func.mkdir(self.get_build_dir())
        makefile = os.path.join(self.get_build_dir(), "Makefile")
        self.proj.makefiles.append(makefile)
        with open(makefile,'w') as f:
            f.write(out)

        self.generate_doxyfile()

