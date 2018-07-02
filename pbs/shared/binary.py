import stat
import os
import pymake
import subprocess
import jinja2
import logging

import crayons

import pbs.rules
import pbs.rules.doc
from pbs.util import *

logger = logging.getLogger(__name__)

"""
the shared library binary file
"""
class CSharedLibraryPython(pymake.Rule):
    
    def __init__(self, library_project):
        self.p = library_project
 
        super().__init__(pymake.ReqFile(self.p.binary_file()))
        
        self.args = Arguments()

    async def build_requirements(self, makefile, func):
        yield func(pymake.ReqFile(__file__))

        for d in self.p.deps:
            yield func(pymake.ReqFile(d.binary_file()))

        for s in self.p.files_object():
            yield func(pymake.ReqFile(s))

        for s in self.p.files_header_processed():
            yield func(pymake.ReqFile(s))

    def get_args_link(self):
        args_link = ['-l' + d.name for d in self.p.deps]
        for d in self.p.deps:
            for l in d.args.libraries:
                args_link.append('-l' + l)
        return args_link

    async def build(self, mc, _, f_in):

        #libhello.so: hello.cpp hello.h
        #g++ hello.cpp -shared -o libhello.so -fPIC -std=c++0x ${inc_paths} ${libs}

        f_out = self.req.fn

        pymake.makedirs(os.path.dirname(f_out))

        #inc_paths = -I/usr/include/python3.5

        libs = ['-lboost_python-py36','-lpython3.6m']
        #libs = ['-lboost_python-py27','-lpython2.7']

        args_library_dir = ['-L' + d.build_dir for d in self.p.deps]
        
        args_link = self.get_args_link()
        
        # whole archive
        args_link_whole = ["-Wl,-whole-archive"] + args_link + libs + ["-Wl,-no-whole-archive"]

        objs = list(self.p.files_object())

        cmd = ['g++'] + objs + ['-shared', '-o', f_out, '-fPIC', '-std=c++0x']
        cmd += args_library_dir + args_link_whole + libs + libs
        
        logger.info(" ".join(cmd))

        return subprocess.call(cmd)

    def rules(self):
        """
        generator of rules
        """
        yield self

        for s in self.p.rules_source_files():
            yield s



