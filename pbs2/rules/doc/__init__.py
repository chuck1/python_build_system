import os
import pymake
import jinja2
import pbs2
import subprocess

class Doxyfile(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
 
        super(Doxyfile, self).__init__(self.f_out, self.f_in, self.build)
        
        self._f_out = os.path.join(self.library_project.build_dir, "Doxyfile")

        self._f_in = os.path.join(pbs2.BASE_DIR, 'templates', 'Doxyfile')

    def f_out(self):
        yield self._f_out

    def f_in(self):
        yield self._f_in

    def build(self, f_out, f_in):
        print("build Doxyfile", self._f_out)
        
        f_out = self._f_out
        f_in = self._f_in
        
        pbs2.os0.makedirs(f_out)

        env = jinja2.environment.Environment()
        template_dirs = [os.path.join(pbs2.BASE_DIR,'templates'), self.library_project.config_dir, '/', '.']
        env.loader = jinja2.FileSystemLoader(template_dirs)
        
        temp = env.get_template(f_in)

        c = {'lib':self.library_project}
        
        out = temp.render(c)
        
        with open(f_out, 'w') as f:
            f.write(out)
        
        return 0

    def rules(self):
        """
        generator of rules
        """
        yield self





class Doxygen(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
 
        super(Doxygen, self).__init__(self.f_out, self.f_in, self.build)
        
        self.doxyfile = os.path.join(self.library_project.build_dir, "Doxyfile")
    
    def f_out(self):
        yield self.library_project.name + '-doc'

    def f_in(self):
        yield self.doxyfile

    def build(self, f_out, f_in):
        #pbs2.os0.makedirs(f_out)

        print("build Doxygen", self.library_project.name)

        cmd = ['doxygen', self.doxyfile]
       
        print(" ".join(cmd))

        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        
        p.communicate()

        return p.returncode

    def rules(self):
        """
        generator of rules
        """
        yield self

        yield Doxyfile(self.library_project)




