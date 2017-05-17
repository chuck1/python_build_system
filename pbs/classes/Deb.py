import os
import jinja2

import pbs.classes.Base
import pbs.func

class Deb(pbs.classes.Base.Base):
    def __init__(self, name, proj):
        super(Deb, self).__init__(name, proj)

    def preprocess(self, filename_in, filename_out):
        print "preprocess",filename_in,filename_out

        with open(filename_in, 'r') as f:
            temp = jinja2.Template(f.read())
        
        out = self.render(temp)
        
        with open(filename_out, 'w') as f:
            f.write(out)

    def render(self, temp):
        
        out = temp.render(
                name                = self.name,
                )

