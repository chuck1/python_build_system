import subprocess
import pymake
import os

import pbs2.os0

class CSourceFile(pymake.Rule):
    def __init__(self, library_project, filename):
        self.library_project = library_project

        h,_ = os.path.splitext(os.path.relpath(filename, library_project.source_dir))
        
        self.file_source = filename

        self.file_object = os.path.join(library_project.object_dir, h+'.o')

        super(CSourceFile, self).__init__(self.f_out, self.f_in, self.build)

    def f_out(self):
        yield self.file_object
    
    def f_in(self):
        yield self.file_source
        yield from self.library_project.files_header_processed()
        yield from self.library_project.deps

        #yield from [d.binary_file() for d in self.library_project.deps]

    def build(self, f_out, f_in):
        f_out = f_out[0]
        pbs2.os0.makedirs(f_out)

        include_args = ['-I' + d for d in self.library_project.include_dirs()]
        define_args = ['-D' + d for d in self.library_project.defines()]
        args = ['-g','-pg','-c','-std=c++11']
        cmd = ['g++'] + args + [self.file_source, '-o', self.file_object] + include_args + define_args
        #print(" ".join(cmd))
        print('CSourceFile', self.file_object)
        return subprocess.call(cmd)






