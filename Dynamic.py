from Library import *

class Dynamic(Library):
    def __init__(self, name):
        super(Dynamic, self).__init__(name)
    
    def get_binary_file(self):
        return os.path.join(self.build_dir, "lib" + self.name + ".so")

    def get_makefile_template(self):
        return "Makefile_library_dynamic.in"

    def get_lib_dir_arg(self):
        return "-Wl,-rpath," + self.build_dir



