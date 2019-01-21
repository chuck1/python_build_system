import os
import pymake
import jinja2
import pbs
import subprocess

class Doxyfile(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
 
        super(Doxyfile, self).__init__(os.path.join(self.library_project.build_dir, "Doxyfile"))
        
    def f_in(self, makefile):
        yield pymake.ReqFile(os.path.join(pbs.BASE_DIR, 'templates', 'Doxyfile'))
        yield pymake.ReqFile(self.library_project.config_file)

    async def build(self, mc, _, f_in):
        print("build Doxyfile", self.f_out)
        
        f_out = self.f_out
        f_in = f_in[0].fn
        
        pymake.makedirs(os.path.dirname(f_out))

        env = jinja2.environment.Environment()
        template_dirs = [os.path.join(pbs.BASE_DIR,'templates'), self.library_project.config_dir, '/', '.']
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
 
        super(Doxygen, self).__init__(self.library_project.name + '-doc')
        
        self.doxyfile = os.path.join(self.library_project.build_dir, "Doxyfile")
    
    def f_in(self, makefile):
        yield pymake.ReqFile(self.doxyfile)

        for f in self.library_project.files_header():
            yield pymake.ReqFile(f)

        for f in self.library_project.files_header_processed():
            yield pymake.ReqFile(f)

    async def build(self, mc, _, f_in):
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




