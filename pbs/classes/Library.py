import jinja2
import myos
import os

import pbs.func
import pbs.classes.Base

class Library(pbs.classes.Base.Base):
    def __init__(self, name, proj):
        super(Library, self).__init__(name, proj)
        
        self.register()

        self.config_file = pbs.func.get_caller()

        
        self.inc_dir = os.path.join(self.root, "include")
        self.src_dir = os.path.join(self.root, "src")

        self.gch_inc_dir = os.path.join(self.get_build_dir(), "gch", "include")

        #self.build_dir = os.path.join(self.root,"build")
            
        self.inc_dirs.append(self.inc_dir)
        self.inc_dirs.append(os.path.join(self.get_build_dir(), "process", "include"))

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
		root_dir		= self.root,
                build_dir         = self.get_build_dir(),
                src_dir           = self.src_dir,
                master_config_dir = self.proj.root_dir,
                name              = self.name,
                )

        return out

    def make(self):

        pbs.func.mkdir(os.path.dirname(self.get_makefile_filename_out()))

        self.proj.projects[self.name] = self

        self.proj.makefiles.append(self.get_makefile_filename_out())

        f_in = os.path.join(
                self.proj.compiler_dir,
                self.get_makefile_template())

        self.render2(f_in, self.get_makefile_filename_out())

        self.generate_doxyfile()



