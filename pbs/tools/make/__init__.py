import os
import sys
import re
import glob
import subprocess
import logging

import pbs.func

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def blue(s):
    print bcolors.BLUE+s+bcolors.END

class Target(object):
    #_dependencies = []
    #_func = None
    def __init__(self, target, dependencies, func, dep_func=lambda p,t,d:[]):
        self.target = target
        self._dependencies = dependencies
        self._func = func
        self._dep_func = dep_func
    def dependencies(self, target):
        return self._dependencies
    def dependencies1(self, proj, target):
        return list(self._dep_func(proj, target, self._dependencies))
    def do(self, proj, target):
        blue(target)
        #print "exec",target
        if self._func is not None:
            dep = list(self.dependencies(target)) + list(self.dependencies1(target))
            self._func(proj, target, dep)


class Makefile(object):
    def __init__(self, proj):
        self.proj=proj
        self.targets = []
        self.target_time = {}

    def get_target(self, target):
        for t in self.targets:
            if t.target == target:
                return t
        return None

    def make(self, target):

        r = self.get_target(target)

        if r is None:
            # if no target exists, file must exist
            if os.path.exists(target):
                return os.path.getmtime(target)
            else:
                print "no file or rule to make file: "+target
                sys.exit(1)
        
        #print r.__unicode__()

        # do the deps
        dep = list(r.dependencies(target))
        t = list(self.make(d) for d in dep)
        
        # do deps1
        dep1 = list(r.dependencies1(self.proj, target))
        t1 = list(self.make(d) for d in dep1)

        dep += dep1
        t += t1

        logging.debug("make {}".format(repr(target)))
        logging.debug("  deps:")
        for d,time in zip(dep,t):
            logging.debug("    {:16} {}".format(time, repr(d)))

        #print "   dep time:",t

        if os.path.exists(target):
            t0 = os.path.getmtime(target)
            #print "target time:",t0

            if t0 < max(t):
                r.do(self.proj, target)
                t0 = os.path.getmtime(target)
                
            return t0
        else:
            r.do(self.proj, target)
            if os.path.exists(target):
                return os.path.getmtime(target)
            else:
                return None

    def print_info(self):
        print "info"
        for t in self.targets:
            print "  " + t.target

def patsubst(pat, repl, lst):
    for l in lst:
        yield re.sub(pat, repl, l)

def call(cmd):
    print "cmd: " + " ".join(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o,e = p.communicate()
    if p.returncode != 0:
        sys.exit(p.returncode)

    return o,e



