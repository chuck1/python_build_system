import subprocess
import os
import re

import pymake
import crayons
import pbs.exception

class CSourceFileDeps(pymake.Rule):
    def __init__(self, library_project, filename):

        self.library_project = library_project

        h,_ = os.path.splitext(os.path.relpath(filename, library_project.source_dir))
        
        self.file_source = filename

        self.file_deps = os.path.join(library_project.object_dir, h+'.dep')

        super().__init__(pymake.ReqFile(self.file_deps))

    async def build_requirements(self, mc, func):
        yield func(pymake.ReqFile(self.file_source))
        
        # processed header files must be generated before deps command can run properly
        for f in self.library_project.files_header_processed():
            #yield pymake.ReqFile(f)
            #mc.make(f)

            # however, this is making compiling slow because EVERY header gets processed

            yield func(pymake.ReqFile(f))

    async def build(self, mc, _, f_in):
        print(crayons.yellow('CSourceFileDeps {}'.format(self.file_deps), bold = True))

        include_args = ['-I' + d for d in self.library_project.include_dirs()]

        args = ['-std=c++11']
        cmd = ['g++'] + args + ['-MM','-MF',self.file_deps,self.file_source] + include_args

        pymake.makedirs(os.path.dirname(self.file_deps))

        ret = subprocess.call(cmd)

        #print(' '.join(cmd))

        #self.read_file()

        return ret

    def read_file(self):
        #print('read_file')
        pat = re.compile('^(\\w+\\.o: )(.*) \\\\\n')

        with open(self.file_deps, 'r') as f:
            s = f.read()
        
        m = pat.match(s)

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
            yield m.group(1)
       
            s = s[m.end(0):]

            m = pat.match(s)

class CSourceFile(pymake.Rule):
    def __init__(self, library_project, filename):

        self.library_project = library_project

        h,_ = os.path.splitext(os.path.relpath(filename, library_project.source_dir))
        
        self.file_source = filename

        self.file_object = os.path.join(library_project.object_dir, h+'.o')

        self.rule_deps = CSourceFileDeps(library_project, filename)

        super().__init__(pymake.ReqFile(self.file_object))

    async def build_requirements(self, mc, func):
        yield func(pymake.ReqFile(__file__))
        yield func(pymake.ReqFile(self.library_project.config_file))
        yield func(pymake.ReqFile(self.file_source))
        
        yield func(self.rule_deps)
        
        #print("depends for {}".format(self.file_source))
        for f in self.rule_deps.read_file():
            #print("    {}".format(f))
            yield func(pymake.ReqFile(f))

        for f in self.library_project.deps:
            yield func(f)

        #yield from [d.binary_file() for d in self.library_project.deps]

    async def build(self, mc, _, f_in):
        pymake.makedirs(os.path.dirname(self.req.fn))

        include_args = ['-I' + d for d in self.library_project.include_dirs()]
        define_args = ['-D' + d for d in self.library_project.defines()]
        
        args = ['-g', '-pg','-c','-std=c++11'] + list(a for a in self.library_project.get_c_source_args() if a is not None)

        cmd = ['g++'] + args + [self.file_source, '-o', self.file_object] + include_args + define_args
        
        print(crayons.yellow("CSourceFile {}".format(self.file_object), bold = True))
        print(crayons.yellow("    args: {}".format(" ".join(args)), bold = True))
        #print(" ".join(cmd))

        ret = subprocess.call(cmd)

        if ret != 0:
            print('ret:', ret)
            print('include args:')

            for s in include_args:
                print(s)

            #print('files header processed')

            #for f in self.library_project.files_header_processed():
            #    print(f)

            raise pbs.exception.CompileError(" ".join(cmd))
        
        return ret






