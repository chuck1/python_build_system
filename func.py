import os
import inspect

def get_caller(n = 2):
    #print inspect.getfile(inspect.currentframe())
    #print __file__
    st = inspect.stack()
    s = st[n]
    #print s[1]
    caller = os.path.abspath(s[1])
    #print caller
    return caller

def get_caller_dir(n = 2):
    #print inspect.getfile(inspect.currentframe())
    #print __file__
    st = inspect.stack()
    s = st[n]
    #print s[1]
    caller = os.path.abspath(s[1])
    dirname = os.path.dirname(caller)
    return dirname

def mkdir(d):
    try:
        os.makedirs(d)
    except:
        pass

