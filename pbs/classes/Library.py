import jinja2
import os
import stat

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
        self.libs = []

	# having issue linking
        #self.libs.append(":" + self.get_binary_file())
	self.libs.append(self.name)


        self.lib_dirs.append(self.get_lib_dir_arg())

    def register(self):
        libraries[self.name] = self

    def preprocess(self, filename_in, filename_out):
        print "preprocess",filename_in,filename_out

        with open(filename_in, 'r') as f:
            temp = jinja2.Template(f.read())
        
        # making special macros

        r = os.path.relpath(
                filename_in,
                os.path.join(self.root, 'include'))
        
        s = r.replace('/','_')
        s = s.replace('.','_')
        s = s.upper()
        
        c = {}
        
        include_block_open  = "#ifndef {0}\n#define {0}".format(s)
        include_block_close = "#endif"

        c['include_block_open']  = include_block_open
        c['include_block_close'] = include_block_close
        
        lst = []
        h,filename = os.path.split(r)
        while True:
            h,t = os.path.split(h)
            #rint 'h',repr(h),'t', repr(t)
            if t == '':
                break
            lst.insert(0,t)

        #rint "lst",lst

        lst2 = ["namespace {} {{".format(l) for l in lst]

        namespace_open  = "\n".join(lst2)
        namespace_close = "}"*len(lst)

        c['namespace_open']  = namespace_open
        c['namespace_close'] = namespace_close
       
        c['header_open']  = include_block_open  + "\n" + namespace_open
        c['header_close'] = namespace_close + "\n" + include_block_close

        # ns and class names

        ns_name = "::".join(lst)
        
        filename2,_ = os.path.splitext(filename)
        class_name,_ = os.path.splitext(filename2)
        
        full_name = ns_name + "::" + class_name
        
        #rint "file ",filename
        #rint "class",class_name
        #rint "full ",full_name

        typedef_verb = "typedef gal::verb::Verbosity<{}> VERB;".format(full_name)

        c['type_this'] = full_name

        c['typedef_verb'] = typedef_verb
        
        c['setup_verb'] = "\n".join([
                typedef_verb,
                "using VERB::init_verb;",
                "using VERB::printv;"])
        
        # render and write
    
        out = self.render(temp, c)
        
        lst = [
                "/*",
                " * DO NOT EDIT THIS FILE",
                " *",
                " * {}".format(filename_in),
                " */",
                ]

        preamble = "\n".join(lst)
        
        out = preamble + "\n" + out
        
        try:
            os.chmod(filename_out, stat.S_IRUSR | stat.S_IWUSR )
        except: pass

        try:

            with open(filename_out, 'w') as f:
                f.write(out)
        
            os.chmod(filename_out, stat.S_IRUSR)
        except Exception as e:
            print e


        st = os.stat(filename_out)
        print "mode", st.st_mode

    def render(self, temp, c):

	c['root_dir']            = self.root
        c['build_dir']           = self.get_build_dir()
        c['src_dir']             = self.src_dir
        c['master_config_dir ']  = self.proj.root_dir
        c['name']                = self.name
   
        #rint "context"
        #rint "\n".join(["  {:32}{}".format(k,repr(v)) for k,v in c.items()])

        out = temp.render(c)

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



