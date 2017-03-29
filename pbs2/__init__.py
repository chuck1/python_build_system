import stat
import os
import pymake
import subprocess
import jinja2

import pbs2.os0
import pbs2.rules

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def filename_to_list(s):
    lst = []
    h,filename = os.path.split(s)
    while True:
        h,t = os.path.split(h)
        #rint 'h',repr(h),'t', repr(t)
        if t == '':
            break
        lst.insert(0,t)
    return lst

class Project(object):
    def __init__(self):
        self.parts = list()
    def execfile(self, filename):
        """
        execute a python script
        """
        exec(open(filename).read(), {'self': self, '__file__': filename, '__dir__': os.path.dirname(filename)})
    def rules(self):
        """
        generator of rules
        """
        yield pymake.RuleStatic(['all'], [p.name + '-all' for p in self.parts], self.build)

        for p in self.parts:
            for r in p.rules():
                yield r

    def build(self, f_out, f_in):
        print('Project build out:', f_out, 'in:', f_in)
        return 0

    def find_part(self, name):
        for p in self.parts:
            if p.name == name:
                return p
        raise Exception('part not found: '+name)

class CHeaderTemplateFile(pymake.Rule):
    def __init__(self, library_project, filename):
        self.library_project = library_project

        filename = os.path.relpath(filename, library_project.include_dir)

        h,_ = os.path.splitext(filename)
        
        self.file_in  = os.path.join(self.library_project.include_dir, filename)
        self.file_out = os.path.join(self.library_project.process_include_dir, h+'.hpp')

        
        super(CHeaderTemplateFile, self).__init__(self.f_out, self.f_in, self.build)

    def f_in(self):
        yield self.file_in

    def f_out(self):
        yield self.file_out

    def get_context(self):
        c = dict()

        r = os.path.relpath(self.file_in, self.library_project.include_dir)
        s = r.replace('/','_').replace('.','_').upper()

        include_block_open  = "#ifndef {0}\n#define {0}".format(s)
        include_block_close = "#endif"

        c['include_block_open']  = include_block_open
        c['include_block_close'] = include_block_close

        c['logs_compile_level'] = s + "_LOGGER_COMPILE_LEVEL"

        lst = filename_to_list(r)

        lst2 = ["namespace {} {{".format(l) for l in lst]

        namespace_open  = "\n".join(lst2)
        namespace_close = "}"*len(lst)

        c['namespace_open']  = namespace_open
        c['namespace_close'] = namespace_close
       
        c['header_open']  = include_block_open  + "\n" + namespace_open
        c['header_close'] = namespace_close + "\n" + include_block_close

        return c


    def build(self, f_out, f_in):
        print("CHeaderProcessedFile", self.file_out, self.file_in)

        #ith open(self.file_in, 'r') as f:
        #   temp = jinja2.Template(f.read())

        env = jinja2.environment.Environment()
        template_dirs = [os.path.join(BASE_DIR,'templates'), self.library_project.config_dir, '/', '.']
        #print('template_dirs',template_dirs)
        env.loader = jinja2.FileSystemLoader(template_dirs)
        
        temp = env.get_template(self.file_in)

        # making special macros

        r = os.path.relpath(self.file_in, self.library_project.include_dir)
        #s = r.replace('/','_').replace('.','_').upper()
        
        c = self.get_context()
        

        #rint "lst",lst

        #lst2 = ["namespace {} {{".format(l) for l in lst]

        #namespace_open  = "\n".join(lst2)
        #namespace_close = "}"*len(lst)

        #c['namespace_open']  = namespace_open
        #c['namespace_close'] = namespace_close
       
        #c['header_open']  = include_block_open  + "\n" + namespace_open
        #c['header_close'] = namespace_close + "\n" + include_block_close

        # ns and class names
        
        h,filename = os.path.split(r)

        lst = filename_to_list(r)

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
    
        preamble = "/*\n * DO NOT EDIT THIS FILE\n *\n * {}\n */\n".format(self.file_in)

        out = preamble + "\n" + temp.render(c)
        
        try:
            os.chmod(self.file_out, stat.S_IRUSR | stat.S_IWUSR )
        except: pass

        pbs2.os0.makedirs(self.file_out)

        try:
            with open(self.file_out, 'w') as f:
                f.write(out)
        
            os.chmod(self.file_out, stat.S_IRUSR)
        except Exception as e:
            print(e)

        st = os.stat(self.file_out)

        return 0

"""
the actual library file
"""
class CStaticLibrary(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
 
        super(CStaticLibrary, self).__init__(self.f_out, self.f_in, self.build)
        
    def f_out(self):
        return [self.library_project.binary_file()]

    def f_in(self):
        for s in self.library_project.files_object():
            yield s

        for s in self.library_project.files_header_processed():
            yield s

    def build(self, f_out, f_in):
        f_out = f_out[0]
        pbs2.os0.makedirs(f_out)

        cmd = ['ar', 'rcs', f_out] + list(self.library_project.files_object())
        
        print(" ".join(cmd))

        return subprocess.call(cmd)

    def rules(self):
        """
        generator of rules
        """
        yield self

        for s in self.library_project.rules_source_files():
            yield s

"""
the actual executable file
"""
class CExecutable(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
 
        super(CExecutable, self).__init__(self.f_out, self.f_in, self.build)
        
    def f_out(self):
        yield self.library_project.binary_file()

    def f_in(self):
        yield from self.library_project.files_object()
        yield from self.library_project.files_header_processed()

        yield from [d.binary_file() for d in self.library_project.deps]

    def build(self, f_out, f_in):
        f_out = f_out[0]
        pbs2.os0.makedirs(f_out)
        
        args = ['-g', '-std=c++11']

        args_link = ['-l' + d.name for d in self.library_project.deps]

        args_library_dir = ['-L' + d.build_dir for d in self.library_project.deps]

        cmd = ['g++'] + args + ['-o', f_out] + list(self.library_project.files_object()) + args_library_dir + args_link
        
        print(" ".join(cmd))

        return subprocess.call(cmd)

    def rules(self):
        """
        generator of rules
        """
        yield self

        for s in self.library_project.rules_source_files():
            yield s

"""
cpp library project

how to add include dirs

    l.l_include_dirs.append('directoy')

how to add defines

    l.l_defines.append('A=1')

"""
class CProject(pymake.Rule):
    def __init__(self, project, name, config_file):
        #print( name, config_file)
        self.project = project
        self.name = name
        #print('config_file',config_file)
        self.config_dir = os.path.dirname(config_file)
        self.source_dir = os.path.join(self.config_dir, 'source')
        
        self.build_dir = os.path.join(self.config_dir, 'build')
        self.object_dir = os.path.join(self.build_dir, 'object')
        self.process_dir = os.path.join(self.build_dir, 'process')
       
        self.include_dir = os.path.join(self.config_dir, 'include')
        self.process_include_dir = os.path.join(self.process_dir, 'include')


        self.deps = list()
        self.l_defines = list()
        self.l_include_dirs = list()

        super(CProject, self).__init__(self.f_out, self.f_in, self.build)

        #print('files header unprocessed',list(self.files_header_unprocessed()))
        #print('files header processed  ',list(self.files_header_processed()))

    def f_out(self):
        yield self.name+'-all'
    
    def f_in(self):
        yield self.binary_file()
        yield from self.files_header_processed()

    def build(self, f_out, f_in):
        #print('Library build out:', f_out, 'in:', f_in)
        print('CProject build name:', self.name, 'out:', f_out)
        return 0

    def include_dirs(self):
        yield self.include_dir
        yield self.process_include_dir
        yield from self.l_include_dirs
        
        for d in self.deps:
            yield from d.include_dirs()

    def defines(self):
        yield from self.l_defines

    def add_dep(self, name):
        """
        add an object to the list of dependencies, referenced by a string containing the name of the dependency
        dependencies are things like other c libraries that this library requires
        """
        
        self.deps.append(self.project.find_part(name))

    def source_files(self):
        for root, dirs, files in os.walk(self.source_dir):
            for f in files:
                _,ext = os.path.splitext(f)
                if ext == '.cpp':
                    #yield os.path.relpath(os.path.join(root,f), self.source_dir)
                    yield os.path.join(root,f)

    def files_object(self):
        for f in self.source_files():
            h,_ = os.path.splitext(os.path.relpath(f, self.source_dir))
            yield os.path.join(self.object_dir, h+'.o')

    def files_header_unprocessed(self):
        for root, dirs, files in os.walk(self.include_dir):
            for f in files:
                _,ext = os.path.splitext(f)
                if ext == '.hpp_in':
                    yield os.path.join(root,f)

    def files_header_processed(self):
        for f in self.files_header_unprocessed():
            h,_ = os.path.splitext(os.path.relpath(f, self.include_dir))
            yield os.path.join(self.process_include_dir, h+'.hpp')

    def rules_source_files(self):
        for s in self.source_files():
            yield pbs2.rules.CSourceFile(self, s)
    
    def rules_files_header_processed(self):
        for s in self.files_header_unprocessed():
            yield CHeaderTemplateFile(self, s)


class Library(CProject):

    def __init__(self, project, name, config_file):
        super(Library, self).__init__(project, name, config_file)

    def binary_file(self):
        return os.path.join(self.build_dir, 'lib' + self.name + '.a')
   
    def rules(self):
        """
        generator of rules
        """
        
        yield self

        l = CStaticLibrary(self)

        yield from l.rules()

        yield from self.rules_files_header_processed()

class Executable(CProject):

    def __init__(self, project, name, config_file):
        super(Executable, self).__init__(project, name, config_file)
 
    def binary_file(self):
        return os.path.join(self.build_dir, self.name)
   
    def rules(self):
        """
        generator of rules
        """
        
        yield self

        l = CExecutable(self)

        yield from l.rules()

        yield from self.rules_files_header_processed()




