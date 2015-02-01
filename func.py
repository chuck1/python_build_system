import os
import inspect

def get_caller():
    #print inspect.getfile(inspect.currentframe())
    #print __file__
    st = inspect.stack()
    s = st[2]
    #print s[1]
    caller = os.path.abspath(s[1])
    #print caller
    return caller

def get_caller_dir():
    #print inspect.getfile(inspect.currentframe())
    #print __file__
    st = inspect.stack()
    s = st[2]
    #print s[1]
    caller = os.path.abspath(s[1])
    dirname = os.path.dirname(caller)
    return dirname

def mkdir(d):
    try:
        os.makedirs(d)
    except:
        pass

