from Library import *

class Dynamic(Library):
    def __init__(self, name, proj):
        super(Dynamic, self).__init__(name, proj)
 
    def get_build_dir(self):
        return os.path.join(self.root,"build","dynamic")
   
    def get_binary_file(self):
        #return os.path.join(self.get_build_dir(), "lib" + self.name + ".so")
        return "lib" + self.name + ".so"

    def get_makefile_template(self):
        return "makefiles/Makefile_library_dynamic.in"

    def get_makefile_filename_out(self):
        return os.path.join(self.get_build_dir(), "Makefile")

    def get_lib_dir_arg(self):
        return "-Wl,-rpath," + self.get_build_dir()

    def register(self):
        self.proj.libraries[self.name + 'dynamic'] = self

    

