
import pymake

class Project(object):
    def __init__(self):
        self.parts = list()
    def execfile(self, filename):
        """
        execute a python script
        """
        execfile(filename, {'self': self})
    def rules(self):
        """
        generator of rules
        """
        yield pymake.RuleStatic(['all'], [p.name + '-all' for p in self.parts], lambda:None)

        for p in self.parts:
            for r in p.rules():
                yield r

"""
cpp library
"""
class Library(object):
    def __init__(self, name):
        self.name = name
    
    def rules(self):
        """
        generator of rules
        """

