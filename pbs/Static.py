from Library import *

class Static(Library):
    def __init__(self, name):
        super(Static, self).__init__(name)
    
    def get_build_dir(self):
        return os.path.join(self.root,"build","static")

    def get_binary_file(self):
        return os.path.join(self.get_build_dir(), "lib" + self.name + ".a")

    def get_makefile_template(self):
        return "makefiles/Makefile_library_static.in"

    def get_makefile_filename_out(self):
        return os.path.join(self.get_build_dir(), "Makefile")

    def get_lib_dir_arg(self):
        return "-L" + self.get_build_dir()

    def register(self):
        libraries[self.name + 'static'] = self


