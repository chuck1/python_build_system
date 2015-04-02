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

        #print name
        #print self.config_file
        
        self.inc_dir = os.path.join(self.root,"include")
        self.src_dir = os.path.join(self.root,"src")

        #self.build_dir = os.path.join(self.root,"build")
            
        self.inc_dirs.append(self.inc_dir)
        self.inc_dirs.append(
                os.path.join(self.get_build_dir(), "process", "include"))

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
                build_dir         = self.get_build_dir(),
                src_dir           = self.src_dir,
                master_config_dir = self.proj.config_dir,
                name              = self.name,
                )

        return out

    def render2(self, fn_in, fn_out):
        #print "library"

        inc0 = self.get_include_dirs_required() + self.inc_dirs

        l0 = list("-I" + s for s in inc0)
        
        inc_str = " ".join(l0)
    
        define_str = " ".join(list("-D" + d for d in self.proj.defines))

        # only for dynamic
        lib_short_str = " ".join(
                list(self.get_libraries_short_required()))
        lib_long_str  = " ".join(
                list(self.get_libraries_long_required()))
        lib_link_str  = " ".join(
                list("-l" + s for s in self.get_libraries_required()))

        lib_link_str_whole  = " ".join(
                list("-l" + s for s in self.get_libraries_required(True)))
        lib_link_str_no_whole  = " ".join(
                list("-l" + s for s in self.get_libraries_required(False)))

        lib_dir_str   = " ".join(list(self.get_library_dirs_required()))

        #print "defines " + define_str
        
        with open(fn_in, 'r') as f:
            temp = jinja2.Template(f.read())
        
        out = temp.render(
                inc_str           = inc_str,
                define_str        = define_str,
                inc_dir           = self.inc_dir,
                src_dir           = self.src_dir,
                binary_file       = self.get_binary_file(),
                build_dir         = self.get_build_dir(),
                master_config_dir = self.proj.config_dir,
                compiler_dir      = self.proj.compiler_dir,
                lib_long_str      = lib_long_str,
                lib_link_str_whole      = lib_link_str_whole,
                lib_link_str_no_whole   = lib_link_str_no_whole,
                lib_link_str      = lib_link_str,
                lib_dir_str       = lib_dir_str,
                project_name      = self.name,
                makefile          = self.get_makefile_filename_out()
                )
    
        with open(fn_out,'w') as f:
            f.write(out)
       

    def make(self):
        #print "library"

        pbs.func.mkdir(os.path.dirname(self.get_makefile_filename_out()))

        self.proj.projects.append(self)

        self.proj.makefiles.append(self.get_makefile_filename_out())

        f_in = os.path.join(
                self.proj.compiler_dir,
                self.get_makefile_template())

        self.render2(f_in, self.get_makefile_filename_out())



