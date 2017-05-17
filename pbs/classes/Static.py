from Library import *

class Static(Library):
    def __init__(self, name, proj):
        super(Static, self).__init__(name, proj)
    
    def get_build_dir(self):
        return os.path.join(self.root,"build","static")

    def get_binary_file(self):
        return os.path.join(self.get_build_dir(), "lib" + self.name + ".a")

    def get_binary_path(self):
        return os.path.join(
                self.proj.get_build_dir(),
                self.get_binary_file()
                )

    def get_makefile_template(self):
        return "makefiles/Makefile_library_static.in"

    def get_makefile_filename_out(self):
        return os.path.join(self.get_build_dir(), "Makefile")

    def get_lib_dir_arg(self):
        return "-L" + self.get_build_dir()

    def register(self):
        self.proj.libraries[self.name + 'static'] = self

    def get_make_targets(self):
        
        cargs = self.get_cargs()

        def do_binary(proj, target, deps):
            pbs.tools.make.call(['ar', 'rcs', target] + deps)

        reqs = list(r.l.name for r in self.reqs)

        yield pbs.tools.make.Target(
            self.name,
            [self.get_binary_path()],#, "precompile_{}".format(self.name)] + reqs,
            None
            )
        
        yield pbs.tools.make.Target(
            self.get_binary_path(),
            list(self.get_o_files()),
            do_binary
            )

