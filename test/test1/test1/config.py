
import pbs.classes.Executable

e = pbs.classes.Executable.Executable("test1", self)

e.require('a')

e.make()




