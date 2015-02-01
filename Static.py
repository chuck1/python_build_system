from Library import *

class Static(Library):
    def __init__(self, name):
        super(Static, self).__init__(name)
    
    def get_binary_file(self):
        return os.path.join(self.build_dir, "lib" + self.name + ".a")

    def get_makefile_template(self):
        return "Makefile_library_static.in"

    def get_lib_dir_arg(self):
        return "-L" + self.build_dir


