import stat
import os
import pymake
import subprocess
import jinja2

import crayons

import pbs.rules
import pbs.rules.doc
from pbs.util import *

"""
the shared library binary file
"""
class CSharedLibraryPython(pymake.Rule):
    
    def __init__(self, library_project):
        self.p = library_project
 
        super(CSharedLibraryPython, self).__init__(self.p.binary_file())
        
        self.args = Arguments()

    def f_in(self, makefile):
        yield pymake.ReqFile(__file__)

        for d in self.p.deps:
            yield pymake.ReqFile(d.binary_file())

        for s in self.p.files_object():
            yield pymake.ReqFile(s)

        for s in self.p.files_header_processed():
            yield pymake.ReqFile(s)

    def get_args_link(self):
        args_link = ['-l' + d.name for d in self.p.deps]
        for d in self.p.deps:
            for l in d.args.libraries:
                args_link.append('-l' + l)
        return args_link

    def build(self, mc, _, f_in):
        print(crayons.green('Build CStaticLibrary ' + self.p.name, bold = True))

        #libhello.so: hello.cpp hello.h
        #g++ hello.cpp -shared -o libhello.so -fPIC -std=c++0x ${inc_paths} ${libs}

        f_out = self.f_out

        pymake.makedirs(os.path.dirname(f_out))

        #inc_paths = -I/usr/include/python3.5

        #libs = ['-lboost_python-py35','-lpython3.5m']
        libs = ['-lboost_python-py27','-lpython2.7']

        args_library_dir = ['-L' + d.build_dir for d in self.p.deps]
        
        args_link = self.get_args_link()
        
        # whole archive
        args_link_whole = ["-Wl,-whole-archive"] + args_link + ["-Wl,-no-whole-archive"]

        objs = list(self.p.files_object())

        cmd = ['g++'] + objs + ['-shared', '-o', f_out, '-fPIC', '-std=c++0x'] + args_library_dir + args_link_whole + libs
        
        print(" ".join(cmd))

        return subprocess.call(cmd)

    def rules(self):
        """
        generator of rules
        """
        yield self

        for s in self.p.rules_source_files():
            yield s



