import stat
import os
import pymake
import subprocess
import jinja2

import crayons

import pbs2.rules
import pbs2.rules.doc

"""
the shared library binary file
"""
class CSharedLibraryPython(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
 
        super(CSharedLibraryPython, self).__init__(self.library_project.binary_file())
        
    def f_in(self, makefile):
        yield pymake.ReqFile(__file__)

        for d in self.library_project.deps:
            yield pymake.ReqFile(d.binary_file())

        for s in self.library_project.files_object():
            yield pymake.ReqFile(s)

        for s in self.library_project.files_header_processed():
            yield pymake.ReqFile(s)

    def build(self, mc, _, f_in):
        print(crayons.green('Build CStaticLibrary ' + self.library_project.name, bold = True))

        #libhello.so: hello.cpp hello.h
        #g++ hello.cpp -shared -o libhello.so -fPIC -std=c++0x ${inc_paths} ${libs}

        f_out = self.f_out

        pymake.makedirs(os.path.dirname(f_out))

        #inc_paths = -I/usr/include/python3.5

        #libs = ['-lboost_python-py35','-lpython3.5m']
        libs = ['-lboost_python-py27','-lpython2.7']


        args_library_dir = ['-L' + d.build_dir for d in self.library_project.deps]
        
        args_link = ['-l' + d.name for d in self.library_project.deps]
        
        # whole archive
        args_link_whole = ["-Wl,-whole-archive"] + args_link + ["-Wl,-no-whole-archive"]

        objs = list(self.library_project.files_object())

        cmd = ['g++'] + objs + ['-shared', '-o', f_out, '-fPIC', '-std=c++0x'] + args_library_dir + args_link_whole + libs
        
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
the actual library file
"""
class CStaticLibrary(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
 
        super(CStaticLibrary, self).__init__(self.library_project.binary_file())
        
    def f_in(self, makefile):
        #print('object files')
        for s in self.library_project.files_object():
            #print(s)
            yield pymake.ReqFile(s)

        for s in self.library_project.files_header_processed():
            yield pymake.ReqFile(s)

    def build(self, mc, _, f_in):
        print('build CStaticLibrary', self.library_project.name)

        pymake.makedirs(os.path.dirname(self.f_out))

        cmd = ['ar', 'rcs', self.f_out] + list(self.library_project.files_object())
        
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
    args = []

    def __init__(self, library_project):
        self.library_project = library_project
 
        super(CExecutable, self).__init__(self.library_project.binary_file())
        
    def f_in(self, makefile):
        yield pymake.ReqFile(self.library_project.config_file)

        for f in self.library_project.files_object():
            yield pymake.ReqFile(f)

        for f in self.library_project.files_header_processed():
            yield pymake.ReqFile(f)

        for d in self.library_project.deps:
            yield pymake.ReqFile(d.binary_file())

    def build(self, mc, _, f_in):
        pymake.makedirs(os.path.dirname(self.f_out))

        args = ['-g','-pg','-std=c++11'] + self.library_project.args
        
        print(crayons.red("Build executable " + self.library_project.name, bold = True))
        print("    args: {}".format(" ".join(args)))


        args_link = ['-l' + d.name for d in self.library_project.deps]

        args_library_dir = ['-L' + d.build_dir for d in self.library_project.deps]

        cmd = ['g++'] + args + ['-o', self.f_out] + list(self.library_project.files_object()) + args_library_dir + args_link + self.library_project.args
        
        #print(" ".join(cmd))

        r = subprocess.call(cmd)

        if r != 0:
            print(crayons.red(" ".join(cmd), bold = True))
    
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

        # custom args
        self.args = []

        super(CProject, self).__init__(self.name+'-all')

        #print('files header unprocessed',list(self.files_header_unprocessed()))
        #print('files header processed  ',list(self.files_header_processed()))

    def get_c_source_args(self):
        yield '-fPIC'
        yield '-Wall'
        yield '-Werror'
        yield from self.args

    def f_in(self, makefile):
        yield pymake.ReqFile(self.binary_file())
        yield from self.files_header_processed()

    def build(self, mc, f_out, f_in):
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
            yield pbs2.rules.CSourceFile(self, s)
    
    def rules_files_header_processed(self):
        for s in self.files_header_unprocessed():
            yield CHeaderTemplateFile(self, s)

class LibraryPython(CProject):
    def __init__(self, project, name, config_file):
        super(LibraryPython, self).__init__(project, name, config_file)
       
        #self.l_include_dirs.append("/usr/include/python3.5")
        self.l_include_dirs.append("/usr/include/python2.7")

    def get_c_source_args(self):
        yield from super(LibraryPython, self).get_c_source_args()
        #yield '-fPIC'

    def f_in(self, makefile):
        yield from super(LibraryPython, self).f_in(makefile)
        
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
        
        self.rule_doxygen = pbs2.rules.doc.Doxygen(self)
        
        self.doc_out_dir = os.path.join(self.build_dir, "html")

    def f_in(self, makefile):
        yield from super(Library, self).f_in(makefile)
        
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

        yield from self.rules_files_header_processed()




