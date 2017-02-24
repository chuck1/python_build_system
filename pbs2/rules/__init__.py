import subprocess
import pymake
import os

class RuleCSource(pymake.Rule):
    def __init__(self, f_out, f_in):
        super(RuleCSource, self).__init__(f_out, f_in, self.func1)

    def func1(self, f_out, f_in):
        #try:
        os.makedirs(os.path.dirname(f_out))
        #except: pass

        subprocess.call(['g++'] + f_in + ['-o', f_out])

m = pymake.Makefile()

m.rules['build/a.out'] = RuleCSource('build/a.out', ['main.cpp'])

m.make('build/a.out')

