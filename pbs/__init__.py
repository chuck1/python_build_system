import stat
import os
import pymake
import subprocess
import jinja2
import crayons

import pbs.rules
import pbs.rules.doc
from pbs.util import *

from pbs.shared.binary import CSharedLibraryPython

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

class _All(pymake.Rule):
    def __init__(self, project):
        self.project = project
        super().__init__(pymake.ReqFile('all'))
    
    async def build_requirements(self, mc, func):
        for p in self.project.parts:
            yield func(pymake.ReqFile(p.name + '-all'))

    async def build(self, mc, _, f_in):
        await self.project.build(mc, None, None)

class _Doc(pymake.Rule):
    def __init__(self, project):
        self.project = project
        super().__init__(pymake.ReqFile('doc'))
    
    async def build_requirements(self, mc, func):
        for p in self.project.parts:
            if isinstance(p, Library):
                yield func(pymake.ReqFile(p.name + '-doc'))

    async def build(self, mc, _, f_in):
        await self.project.build(mc, None, None)

class Project(object):
    def __init__(self):
        self.parts = list()

    def execfile(self, filename):
        with open(filename) as f:
            s = f.read()
        try:
            exec(s, {'self': self, '__file__': filename, '__dir__': os.path.dirname(filename)})
        except Exception as e:
            print("error running {}: {}".format(repr(filename), repr(e)))
            raise

    def rules(self):
        """
        generator of rules
        """
        yield _All(self)
        yield _Doc(self)

        for p in self.parts:
            for r in p.rules():
                yield r

    async def build(self, mc, f_out, f_in):
        print('Project build out:', f_out, 'in:', f_in)

    def find_part(self, name):
        for p in self.parts:
            if p.name == name:
                return p
        raise Exception('part not found: '+name)

class CHeaderTemplateFile(pymake.Rule):
    def __init__(self, library_project, filename):
        self.library_project = library_project
        self.file_in  = filename

        filename_rel = os.path.relpath(filename, library_project.include_dir)

        h,_ = os.path.splitext(filename_rel)
       
        f_out = os.path.join(self.library_project.process_include_dir, h+'.hpp')

        super().__init__(pymake.ReqFile(f_out))

    async def build_requirements(self, makefile, func):
        yield func(pymake.ReqFile(self.file_in))
        yield func(pymake.ReqFile(self.library_project.config_file))

    def get_context(self):
        c = dict()

        r = os.path.relpath(self.file_in, self.library_project.include_dir)
        s = r.replace('/','_').replace('.','_').upper()

        include_block_open  = "#ifndef {0}\n#define {0}".format(s)
        include_block_close = "#endif"

        c['include_block_open']  = include_block_open
        c['include_block_close'] = include_block_close

        c['logs_level'] = s + "_LOGGER_LEVEL"
        c['logs_mode'] = s + "_LOGGER_MODE"

        lst = filename_to_list(r)

        lst2 = ["namespace {} {{".format(l) for l in lst]

        namespace_open  = "\n".join(lst2)
        namespace_close = "}"*len(lst)

        c['namespace_open']  = namespace_open
        c['namespace_close'] = namespace_close
       
        c['header_open']  = include_block_open  + "\n" + namespace_open
        c['header_close'] = namespace_close + "\n" + include_block_close

        return c

    async def build(self, mc, f_out, f_in):
        #print("HeaderProcessedFile", self.f_out, self.file_in)

        #ith open(self.file_in, 'r') as f:
        #   temp = jinja2.Template(f.read())

        env = jinja2.environment.Environment()
        template_dirs = [os.path.join(BASE_DIR,'templates'), self.library_project.config_dir, '/', '.']
        #print('template_dirs',template_dirs)
        env.loader = jinja2.FileSystemLoader(template_dirs)
        
        temp = env.get_template(self.file_in)

        # making special macros

        r = os.path.relpath(self.file_in, self.library_project.include_dir)
        
        c = self.get_context()

        # ns and class names
        
        h,filename = os.path.split(r)

        lst = filename_to_list(r)

        ns_name = "::".join(lst)
        
        filename2,_ = os.path.splitext(filename)
        class_name,_ = os.path.splitext(filename2)
        
        full_name = ns_name + "::" + class_name
        
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
            os.chmod(self.req.fn, stat.S_IRUSR | stat.S_IWUSR )
        except Exception as e:
            print("error in chmod", e)

        pymake.makedirs(os.path.dirname(self.req.fn))

        try:
            with open(self.req.fn, 'w') as f:
                f.write(out)
        except Exception as e:
            print("error in write", e)
            raise

        try:
            os.chmod(self.req.fn, stat.S_IRUSR)
        except Exception as e:
            print("error in chmod", e)
            raise

        st = os.stat(self.req.fn)

"""
the actual library file
"""
class CStaticLibrary(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
 
        super().__init__(pymake.ReqFile(self.library_project.binary_file()))
        
    async def build_requirements(self, makefile, func):
        #print('object files')
        for s in self.library_project.files_object():
            #print(s)
            yield func(pymake.ReqFile(s))

        for s in self.library_project.files_header_processed():
            yield func(pymake.ReqFile(s))

    async def build(self, mc, _, f_in):
        print('build CStaticLibrary', self.library_project.name)

        pymake.makedirs(os.path.dirname(self.req.fn))

        cmd = ['ar', 'rcs', self.req.fn] + list(self.library_project.files_object())
        
        #print(" ".join(cmd))

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

add extra build args like so:

    e.args.append("-an_arg")

"""
class CExecutable(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
        self.p = library_project
 
        super().__init__(pymake.ReqFile(self.library_project.binary_file()))
       
        self.args = Arguments()

    async def build_requirements(self, makecall, func):
        yield func(pymake.ReqFile(self.library_project.config_file))

        for f in self.library_project.files_object():
            yield func(pymake.ReqFile(f))

        for f in self.library_project.files_header_processed():
            yield func(pymake.ReqFile(f))

        for d in self.library_project.deps:
            yield func(pymake.ReqFile(d.binary_file()))

    def get_args_link(self):
        args_link = ['-l' + d.name for d in self.library_project.deps]
        for d in self.p.deps:
            for l in d.args.libraries:
                args_link.append('-l' + l)
        return args_link

    async def build(self, mc, _, f_in):
        pymake.makedirs(os.path.dirname(self.req.fn))

        args = ['-g','-pg','-std=c++11'] + self.p.args.args
        
        print(crayons.red("Build executable " + self.library_project.name, bold = True))
        print("    args: {}".format(" ".join(args)))

        args_link = self.get_args_link()

        args_library_dir = ['-L' + d.build_dir for d in self.library_project.deps]

        cmd = ['g++'] + args + ['-o', self.req.fn]
        cmd += list(self.library_project.files_object()) + args_library_dir
        cmd += args_link + args_link + self.p.args.args
        
        #print(" ".join(cmd))

        r = subprocess.call(cmd)

        print('ret:', r)

        if r != 0:
            print(crayons.red(" ".join(cmd)))
            raise Exception(crayons.red(" ".join(cmd), bold = True))
    
        return r

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
        self.config_file = config_file
        self.config_dir = os.path.dirname(os.path.abspath(config_file))
        self.source_dir = os.path.join(self.config_dir, 'source')
        
        self.build_dir = os.path.join(self.config_dir, 'build')
        self.object_dir = os.path.join(self.build_dir, 'object')
        self.process_dir = os.path.join(self.build_dir, 'process')
       
        self.include_dir = os.path.join(self.config_dir, 'include')
        self.process_include_dir = os.path.join(self.process_dir, 'include')

        self.deps = list()
        self.l_defines = list()
        self.l_include_dirs = list()
        
        self._test = False

        # custom args
        self.args = Arguments()

        super(CProject, self).__init__(pymake.ReqFile(self.name+'-all'))

        #print('files header unprocessed',list(self.files_header_unprocessed()))
        #print('files header processed  ',list(self.files_header_processed()))

    def get_c_source_args(self):
        yield '-fPIC'
        yield '-Wall'
        yield '-Werror'
        yield from self.args.args

    async def build_requirements(self, makefile, func):
        yield func(pymake.ReqFile(__file__))
        yield func(pymake.ReqFile(self.binary_file()))
        for f in self.files_header_processed():
            yield func(f)

        print(self, 'test =', self._test)
        if self._test:
            yield func(pymake.ReqFile(os.path.join(self.build_dir, 'test.txt')))

    async def build(self, mc, _, f_in):
        print('CProject build name:', self.name, 'out:', self.req.fn)
        return 0

    def include_dirs(self):
        yield self.include_dir
        yield self.process_include_dir
        yield from self.l_include_dirs
        
        for d in self.deps:
            yield from d.include_dirs()

    def defines(self):
        for d in self.deps:
           yield from d.defines()

        yield from self.l_defines

    def add_dep(self, name):
        """
        add an object to the list of dependencies, referenced by a string containing the name of the dependency
        dependencies are things like other c libraries that this library requires
        """
        
        self.deps.append(self.project.find_part(name))

    def source_files(self):
        #print('source files. walking', self.source_dir)
        for root, dirs, files in os.walk(self.source_dir):
            #print(root, dirs, files)
            for f in files:
                _,ext = os.path.splitext(f)
                if ext == '.cpp':
                    #print(f)
                    #yield os.path.relpath(os.path.join(root,f), self.source_dir)
                    yield os.path.join(root,f)

    def files_object(self):
        for f in self.source_files():
            h,_ = os.path.splitext(os.path.relpath(f, self.source_dir))
            yield os.path.join(self.object_dir, h+'.o')

    def files_header(self):
        for root, dirs, files in os.walk(self.include_dir):
            for f in files:
                _,ext = os.path.splitext(f)
                if ext == '.hpp':
                    yield os.path.join(root,f)

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
            yield pbs.rules.CSourceFile(self, s)
    
    def rules_files_header_processed(self):
        for s in self.files_header_unprocessed():
            yield CHeaderTemplateFile(self, s)

class LibraryPython(CProject):
    def __init__(self, project, name, config_file):
        super(LibraryPython, self).__init__(project, name, config_file)
       
        self.l_include_dirs.append("/usr/include/python3.6")
        #self.l_include_dirs.append("/usr/include/python2.7")

    def get_c_source_args(self):
        yield from super(LibraryPython, self).get_c_source_args()
        #yield '-fPIC'

    async def build_requirements(self, makefile, func):
        async for _ in super(LibraryPython, self).build_requirements(makefile, func):
            yield _
        
    def binary_file(self):
        return os.path.join(self.build_dir, 'lib' + self.name + '.so')
        
    def rules(self):
        """
        generator of rules
        """
        
        yield self

        l = CSharedLibraryPython(self)

        yield from l.rules()

        yield from self.rules_files_header_processed()

class Library(CProject):

    def __init__(self, project, name, config_file):
        super(Library, self).__init__(project, name, config_file)
        
        self.rule_doxygen = pbs.rules.doc.Doxygen(self)
        
        self.doc_out_dir = os.path.join(self.build_dir, "html")

    async def build_requirements(self, makefile, func):
        async for _ in super().build_requirements(makefile, func):
            yield _
        
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

        yield from self.rule_doxygen.rules()

class TestExecutable(pymake.Rule):
    def __init__(self, ex):
        self.ex = ex
 
        f_out = os.path.join(self.ex.p.build_dir, "test.txt")

        super(TestExecutable, self).__init__(pymake.ReqFile(f_out))
    
    async def build_requirements(self, mc, func):
        yield func(self.ex)

    async def build(self, mc, _, f_in):
        print(crayons.green('test {}'.format(self.ex.p.name), bold = True))

        cmd = [self.ex.p.binary_file()]

        r = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        
        if True: #r.returncode != 0:
            print(r.stdout.decode())
            print(r.stderr.decode())
        
        if(r.returncode == 0):
            with open(self.f_out, "w") as f:
                f.write(r.stdout.decode())
                f.write(r.stderr.decode())

        return r.returncode

class Executable(CProject):
    args = []

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

        #yield from self.rules_files_header_processed()
        
        yield TestExecutable(l)

        yield from self.rules_files_header_processed()









