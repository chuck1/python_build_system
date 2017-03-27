import os

def makedirs(f):
    d = os.path.dirname(f)
    try:
        os.makedirs(d)
    except OSError:
        pass

