import os
import pymake
import subprocess

def makedirs(f):
    d = os.path.dirname(f)
    try:
        os.makedirs(d)
    except OSError:
        pass

class Project(object):
    def __init__(self):
        self.parts = list()
    def execfile(self, filename):
        """
        execute a python script
        """
        execfile(filename, {'self': self, '__file__': filename})
    def rules(self):
        """
        generator of rules
        """
        yield pymake.RuleStatic(['all'], [p.name + '-all' for p in self.parts], self.build)

        for p in self.parts:
            for r in p.rules():
                yield r

    def build(self, f_out, f_in):
        print 'Project build out:', f_out, 'in:', f_in


class CSourceFile(pymake.RuleStatic):
    def __init__(self, library, filename):
        h,_ = os.path.splitext(filename)
        
        self.f_in = os.path.join(library.source_dir, filename)
        self.f_out = os.path.join(library.object_dir, h+'.o')

        super(CSourceFile, self).__init__([self.f_out], [self.f_in], self.build)

    def rules(self):
        yield RuleStatic([self.f_out], [self.f_in], self.build)

    def build(self, f_out, f_in):
        f_out = f_out[0]
        makedirs(f_out)
        cmd = ['gcc','-g','-c'] + f_in + ['-o', f_out]
        print " ".join(cmd)
        subprocess.call(cmd)
        

"""
the actual library file
"""
class CStaticLibrary(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
 
        super(CStaticLibrary, self).__init__(self.f_out, self.f_in, self.build)
    
    def f_out(self):
        return [self.library_project.library_file]

    def f_in(self):
        for s in self.library_project.rules_source_files():
            yield list(s.f_out())[0]

    def build(self, f_out, f_in):
        f_out = f_out[0]
        makedirs(f_out)

        cmd = ['ar', '-cvq', f_out] + f_in
        
        print ' '.join(cmd)

        subprocess.call(cmd)

"""
cpp library project
"""
class Library(pymake.Rule):
    def __init__(self, name, config_file):
        #print name, config_file
        self.name = name
        self.config_dir = os.path.dirname(config_file)
        self.source_dir = os.path.join(self.config_dir, 'source')
        self.source_extensions = ['.cpp']
        self.build_dir = os.path.join(self.config_dir, 'build')
        self.object_dir = os.path.join(self.build_dir, 'object')
        self.library_file = os.path.join(self.build_dir, 'lib' + self.name + '.a')

        super(Library, self).__init__(self.f_out, self.f_in, self.build)
    
    def f_out(self):
        return [self.name+'-all']
    
    def f_in(self):
        return [self.library_file]

    def build(self, f_out, f_in):
        print 'Library build', f_out, f_in

    def source_files(self):
        for root, dirs, files in os.walk(self.source_dir):
            for f in files:
                _,ext = os.path.splitext(f)
                if ext in self.source_extensions:
                    yield os.path.relpath(os.path.join(root,f), self.source_dir)
    
    def rules_source_files(self):
        for s in self.source_files():
            yield CSourceFile(self, s)

    def rules(self):
        """
        generator of rules
        """
        
        yield self

        yield CStaticLibrary(self)

        for s in self.rules_source_files():
            yield s









