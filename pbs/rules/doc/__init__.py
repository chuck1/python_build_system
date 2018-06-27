import os
import pymake
import jinja2
import pbs
import subprocess

class Doxyfile(pymake.Rule):
    def __init__(self, library_project):
        self.library_project = library_project
        f_out = os.path.join(self.library_project.build_dir, "Doxyfile")
        super().__init__(pymake.ReqFile(f_out))
        
    async def build_requirements(self, makefile, func):
        yield func(pymake.ReqFile(os.path.join(pbs.BASE_DIR, 'templates', 'Doxyfile')))
        yield func(pymake.ReqFile(self.library_project.config_file))

    async def build(self, mc, _, f_in):
        
        f_in = f_in[0].fn

        env = jinja2.environment.Environment()
        template_dirs = [os.path.join(pbs.BASE_DIR,'templates'), self.library_project.config_dir, '/', '.']
        env.loader = jinja2.FileSystemLoader(template_dirs)
        
        temp = env.get_template(f_in)

        c = {'lib':self.library_project}
        
        out = temp.render(c)
        
        with self.req.open('w') as f:
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
 
        super().__init__(pymake.ReqFile(self.library_project.name + '-doc'))
        
        self.doxyfile = os.path.join(self.library_project.build_dir, "Doxyfile")
    
    async def build_requirements(self, mc, func):
        yield func(pymake.ReqFile(self.doxyfile))

        for f in self.library_project.files_header():
            yield func(pymake.ReqFile(f))

        for f in self.library_project.files_header_processed():
            yield func(pymake.ReqFile(f))

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




