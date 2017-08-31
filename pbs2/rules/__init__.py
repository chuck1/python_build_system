import subprocess
import pymake
import os
import re
import termcolor

class CSourceFileDeps(pymake.Rule):
    def __init__(self, library_project, filename):

        self.library_project = library_project

        h,_ = os.path.splitext(os.path.relpath(filename, library_project.source_dir))
        
        self.file_source = filename

        self.file_deps = os.path.join(library_project.object_dir, h+'.dep')

        super(CSourceFileDeps, self).__init__(self.file_deps)

    def f_in(self, makefile):
        yield pymake.ReqFile(self.file_source)

    def build(self, mc, _, f_in):
        print('CSourceFileDeps', self.file_deps)

        include_args = ['-I' + d for d in self.library_project.include_dirs()]

        args = ['-std=c++11']
        cmd = ['g++'] + args + ['-MM','-MF',self.file_deps,self.file_source] + include_args

        pymake.makedirs(os.path.dirname(self.file_deps))

        ret = subprocess.call(cmd)

        #self.read_file()

        #return 1
        return ret

    def read_file(self):
        #print('read_file')
        pat = re.compile('^(\\w+\\.o: )(.*) \\\\\n')

        with open(self.file_deps, 'r') as f:
            s = f.read()
        
        m = pat.match(s)
        #print(len(m.groups()))
        #print(repr(m.group(1)))
        #print(repr(m.group(2)))
        #print(m.end(0))

        

        if not m:
            #vert_graph_all.o: \\\n /home/crymal/git/graph/source/graph/iterator/vert_graph_all.cpp \\\n
            #print(repr(s))

            pat = re.compile('^\\w+\\.o: \\\\\n.*')
           
            m = pat.match(s)

            if not m:
                #print(repr(s))
                # 'Symbol.o: /home/crymal/git/esolv/source/esolv/symbol/Symbol.cpp\n'

                pat = re.compile('^\\w+\\.o:.*\n$')

                m = pat.match(s)
                
                if not m:
                    raise RuntimeError()

                return
        
        
        pat = re.compile('^\\s*(.*) \\\\\n')

        s = s[m.end(0):]
        m = pat.match(s)

        while m:
            #print(repr(m.group(1)))
            yield m.group(1)
       
            #print(m.end(0))

            s = s[m.end(0):]

            m = pat.match(s)

        

class CSourceFile(pymake.Rule):
    def __init__(self, library_project, filename):

        self.library_project = library_project

        h,_ = os.path.splitext(os.path.relpath(filename, library_project.source_dir))
        
        self.file_source = filename

        self.file_object = os.path.join(library_project.object_dir, h+'.o')

        self.rule_deps = CSourceFileDeps(library_project, filename)

        super(CSourceFile, self).__init__(self.file_object)

    def f_in(self, mc):
        yield pymake.ReqFile(self.file_source)
        yield self.rule_deps
        
        # depends file depends on the source file
        self.rule_deps.make(mc)

        #print("depends")
        for f in self.rule_deps.read_file():
            #print("    {}".format(f))
            yield pymake.ReqFile(f)

        # should be covered by depends
        #for f in self.library_project.files_header_processed():
        #    yield pymake.ReqFile(f)

        for f in self.library_project.deps:
            yield f

        #yield from [d.binary_file() for d in self.library_project.deps]

    def build(self, mc, _, f_in):
        pymake.makedirs(os.path.dirname(self.f_out))

        include_args = ['-I' + d for d in self.library_project.include_dirs()]
        define_args = ['-D' + d for d in self.library_project.defines()]
        
        args = ['-g','-pg','-c','-std=c++11'] + list(a for a in self.library_project.get_c_source_args() if a is not None)

        cmd = ['g++'] + args + [self.file_source, '-o', self.file_object] + include_args + define_args
        
        print(termcolor.colored("CSourceFile {}".format(self.file_object), 'yellow', attrs=['bold']))
        #print(" ".join(cmd))

        ret = subprocess.call(cmd)

        if ret:
            print('include args:')
            for s in include_args:
                print(s)
            print('files header processed')
            for f in self.library_project.files_header_processed():
                print(f)
        
        return ret






