
import pbs.gen
import pbs.func

def pkg_func(args):

    d = pbs.func.read_config_file()

    #print "pkg:", args.component
    
    #print d
    
    project = pbs.gen.Project(d['root'], None)
    
    project.execute()
    
    p = project.projects[args.component]

    p.package()

