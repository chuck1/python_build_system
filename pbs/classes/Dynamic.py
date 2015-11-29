from Library import *

class Dynamic(Library):
    def __init__(self, name, proj):
        super(Dynamic, self).__init__(name, proj)
 
    def get_build_dir(self):
        return os.path.join(self.root,"build","dynamic")
   
    def get_binary_file(self):
        #return os.path.join(self.get_build_dir(), "lib" + self.name + ".so")
        # instead put in project build dir
        return "lib" + self.name + ".so"

    def make_binary_links(self, d):
        f = self.get_binary_file()
        dst = os.path.join(d,f)
        os.symlink(f, dst+'.1')
        os.symlink(f, dst+'.1.0')
    
    def get_makefile_template(self):
        return "makefiles/Makefile_library_dynamic.in"

    def get_makefile_filename_out(self):
        return os.path.join(self.get_build_dir(), "Makefile")

    def get_lib_dir_arg(self):
        return "-Wl,-rpath," + self.get_build_dir()

    def register(self):
        self.proj.libraries[self.name + 'dynamic'] = self

    

