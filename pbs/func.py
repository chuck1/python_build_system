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

def read_config_file():
    with open('config.txt', 'r') as f:
        text = f.read()
    
    lines = text.split('\n')
    lines = [l for l in lines if l]
    
    d = {}

    for l in lines:
        s = l.split(',')

        d[s[0]] = s[1]

    return d

