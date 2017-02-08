import shutil
import jinja2
import os
import re
import logging
import itertools

import pbs
import pbs.func
import pbs.doc


class Req(object):
    """
    l     - Library object
    whole - boolean something to do with copying symbols when linking
    """
    def __init__(self, l, whole):
        self.l = l
        self.whole = whole

class Dirs(object): pass

class Base(object):
    """
    reqs - list of Req objects
    """
    def __init__(self, name, proj):
        self.name = name
	if not isinstance(name, str):
		print "name",name
		raise ValueError()

        self.proj = proj

        self.reqs = []
    
        # specific for this project
        # include directories
        self.inc_dirs = []
        # library directories
        self.lib_dirs = []
        # manual link arguments
        self._libs = []

        self.tests = []

        self.root = pbs.func.get_caller_dir(4)

        self.doc = pbs.doc.Doc(self)
        self.dirs = Dirs()

        self.dirs.header_process = os.path.join(self.get_build_dir(), "process", "include")

    def get_objects_dir(self):
        return os.path.join(
			self.get_build_dir(),
			'objects'
			)
    def make_binary_links(self, d):
        pass

    def get_c_files(self):
        patstr = ".*\.cpp$"
        #print "glob {} {}".format(repr(patstr), repr(self.root))
        return pbs.glob(patstr, self.root)
    def get_h_in_files(self):
        patstr = ".*\.hpp\.in$"
        #rint "glob {} {}".format(repr(patstr), repr(self.root))
        return pbs.glob(patstr, os.path.join(self.root, 'include'))
    def get_h_files(self):
        patstr = ".*\.hpp$"
        #rint "glob {} {}".format(repr(patstr), repr(self.root))
        return pbs.glob(patstr, os.path.join(self.root, 'include'))

    def get_o_files(self):
	logging.debug("get_o_files")
	pat  = self.root + r'/(.*)\.cpp$'
        repl = self.get_objects_dir() + r'/\1.o'

        for c in self.get_c_files():
	    s = re.sub(pat, repl, c)
	    logging.debug("  pat  = {}".format(repr(pat)))
	    logging.debug("  repl = {}".format(repr(repl)))
	    logging.debug("  c    = {}".format(repr(c)))
	    logging.debug("  s    = {}".format(repr(s)))
            yield s

    def get_gch_for(self, f):
	pat  = self.root + r'/(.*)\.hpp$'
        repl = self.get_build_dir() + r'/gch/\1.hpp.gch'
	s = re.sub(pat, repl, f)
        return s
    def get_gch_files(self):
        return [self.get_gch_for(c) for c in self.get_h_files()]

    def get_dep_for(self, c):
       	pat  = self.root + r'/(.*)\.cpp$'
        repl = self.get_build_dir() + r'/depends/\1.txt'
        s = re.sub(pat, repl, c)
        return s
 
    def get_dep_files(self):
        for c in self.get_c_files():
            yield self.get_dep_for(c)
    def get_pre_files(self):
	pat  = self.root + r'/(.*)\.cpp$'
        repl = self.get_objects_dir() + r'/\1.pre'
        
        for c in self.get_c_files():
	    s = re.sub(pat, repl, c)
            yield s

    def get_pre2_files(self):
	pat  = self.root + r'/(.*)\.cpp$'
        repl = self.get_objects_dir() + r'/\1.pre2'
        
        for c in self.get_c_files():
	    s = re.sub(pat, repl, c)
            yield s
    
    def get_pre3_files(self):
	pat  = self.root + r'/(.*)\.cpp$'
        repl = self.get_objects_dir() + r'/\1.pre3'
        
        for c in self.get_c_files():
	    s = re.sub(pat, repl, c)
            yield s

    def clean(self):
        #print "rm "+self.get_build_dir()
        #print "rm "+self.get_binary_file()

	shutil.rmtree(self.get_build_dir())
	
        try:
            os.remove(self.get_binary_file())
        except OSError:
            pass

    def require(self, o, lib_type = 'static', whole = False):
        if isinstance(o, list):
            raise Exception("deprecated")
            for l in o:
                self.require1(l, lib_type, whole)
        else:
            self.require1(o, lib_type, whole)

    def require_from_config(self, filename, name, lib_type = 'static', whole = False):
        """
        create dependency by passing absolute path of a config.py file
        """
        try:
            l = self.proj.libraries[name + lib_type]
        except:
            execfile(filename, {'self':self.proj})
            l = self.proj.libraries[name + lib_type]
        
        self.reqs.append(Req(l, whole)) 

    def require1(self, name, lib_type, whole):
        # look for .pmake_config file in ~/usr/lib/pmake
        filename = os.path.join(os.environ['HOME']+"/usr/lib/pmake", name + ".py")
        try:
            l = self.proj.libraries[name + lib_type]
        except:
            execfile(filename, {'self':self.proj})
            l = self.proj.libraries[name + lib_type]
        
        self.reqs.append(Req(l, whole)) 

        # get info from required library

        
    #def require_library(self, l):
    #    self.inc_dirs.append(l.inc_dir)
    
    
    def get_libraries_required(self, whole = False):
        libs = []
        for r in self.reqs:
            if(r.whole == whole):
                libs += r.l.libs
        
        # manual libs
        libs += self._libs

        return libs

    def get_libraries_short_required(self):
        libs = []
        for r in self.reqs:
            for l in r.l.libs:
                if l[0] != ":":
                    libs.append(l)
        return libs

    def get_libraries_long_required(self):
        libs = []
        for r in self.reqs:
            for l in r.l.libs:
                #if l[0] == ":":
                #    libs.append(l[1:])
                #print "lib ", r.l.get_binary_file()
                libs.append(r.l.get_binary_file())
                pass
        return libs
        
    def get_library_dirs_required(self):
        lib_dirs = []
        for r in self.reqs:
            lib_dirs += r.l.lib_dirs
        return lib_dirs

    def get_include_dirs_required(self):
        inc_dirs = []
        for r in self.reqs:
            inc_dirs += r.l.inc_dirs
        return inc_dirs
    def get_gch_inc_dirs_required(self):
        inc_dirs = []
        for r in self.reqs:
            inc_dirs += [r.l.gch_inc_dir]
        return inc_dirs

    def get_inc_list(self):
	#rint "get_inc_list"
        for s in (self.get_include_dirs_required() + self.inc_dirs):
	    #print "  "+s
            yield "-I" + s

    def get_gch_inc_list(self):
       	#rint "get_gch_inc_list"
        for s in (self.get_gch_inc_dirs_required() + [self.gch_inc_dir]):
	    #rint "  "+s
            yield "-I" + s

    def get_define_list(self):
        for d in self.proj.defines:
            yield "-D" + d 

    def render2(self, fn_in, fn_out):

        #inc0 = self.get_include_dirs_required() + self.inc_dirs
        #l0 = list("-I" + s for s in inc0)
        
        inc_str = " ".join(self.get_inc_list())
    
        define_str = " ".join(self.get_define_list())

        # only for dynamic
        lib_short_str = " ".join(
                list(self.get_libraries_short_required()))
        lib_long_str  = " ".join(
                list(self.get_libraries_long_required()))
        lib_link_str  = " ".join(
                list("-l" + s for s in self.get_libraries_required()))

        lib_link_str_whole  = " ".join(
                list("-l" + s for s in self.get_libraries_required(True)))
        lib_link_str_no_whole  = " ".join(
                list("-l" + s for s in self.get_libraries_required(False)))

        lib_dir_str   = " ".join(list(self.get_library_dirs_required()))

	tag_files = " ".join(list("{}/tagfile".format(r.l.get_build_dir()) for r in self.reqs))
        
        with open(fn_in, 'r') as f:
            temp = jinja2.Template(f.read())
        
        out = temp.render(
                inc_str           = inc_str,
                define_str        = define_str,
                root_dir          = self.root,
                inc_dir           = self.inc_dir,
                src_dir           = self.src_dir,
                binary_file       = self.get_binary_file(),
                build_dir         = self.get_build_dir(),
                master_config_dir = self.proj.root_dir,
                compiler_dir      = self.proj.compiler_dir,
                lib_long_str      = lib_long_str,
                lib_link_str_whole      = lib_link_str_whole,
                lib_link_str_no_whole   = lib_link_str_no_whole,
                lib_link_str      = lib_link_str,
                lib_dir_str       = lib_dir_str,
                project_name      = self.name,
                makefile		= self.get_makefile_filename_out(),
		tag_files		= tag_files,
                doc = self.doc,
                dirs = self.dirs,
                )
        
        context = {
                "doc":self.doc,
                "dirs":self.dirs}

        out2 = temp.render(context)

        with open(fn_out,'w') as f:
            f.write(out)

    def get_cargs(self):
	cargs = [
	        '-g', '-std=c++0x', '-rdynamic', '-fPIC',
	        '-Wno-format-security',
	        '-Wall',
	        '-Werror',
	        '-Wno-unused-local-typedefs',
	        '-Wno-unknown-pragmas']
	
	cargs += list(self.get_define_list())

	return cargs

    def include_block(self, h):
        """
	generate c preprocessor include block from filename
        """
	logging.debug("include_block")
	logging.debug("  "+h)

        h = os.path.relpath(h, os.path.join(self.root,'include'))
	
	logging.debug("  "+h)

	h = h.replace('.','_')
	h = h.upper()

	logging.debug("  "+h)
	
	return h
	
    def get_make_targets_0(self):
        
	cargs = self.get_cargs()
        
	inc = list(self.get_inc_list())
	gch_inc = list(self.get_gch_inc_list())

	#include = ['-include', 'A.hpp']
        def filter_local_gch_2(proj, deps):
	    for d in deps:
		r = proj.root_dir
	        d = os.path.realpath(d)
		c = os.path.commonprefix([d, r])
		if c == r:
		    h,t = os.path.splitext(d)
		    if t == '.gch':
		        yield d
		    if t == '.h':
			yield get_gch_for_any(proj, d)
		    if t == '.hpp':
			yield get_gch_for_any(proj, d)
		else:
		    yield d

	def do_o_dep(proj, target, deps):
            df = self.get_dep_for(deps[0])
	    #rint deps[0]
	    #rint df
            with open(df,'r') as f:
	        dep = f.read().split("\n")

	    dep = list(filter_local_gch_2(proj, dep))

	    #rint "dep"
	    for l in dep:
                #rint "  ",l
		yield l

	def get_gch_for_any(proj, f):
	    """
	    convert any local header to correct gch
	    """
	    #rint "get gch for any"
            rel = os.path.relpath(f, proj.root_dir)
	    #rint "rel = "+rel

            h = rel
            while h:
	        h,t = os.path.split(h)
	        if t == 'include':
		   break

	    #rint "h = "+h
	    p = proj.projects[h]
            #rint p
	    g = p.get_gch_for(f)
            #rint "g = "+g
	    return g

	def filter_local_gch(proj, deps):
	    logging.debug("filter_local_gch")
	    for d in deps:
		r = proj.root_dir
	        d = os.path.realpath(d)
		c = os.path.commonprefix([d, r])
		logging.debug("  d "+d)
		logging.debug("  r "+r)
		logging.debug("  c "+c)
		if c == r:
		    h,t = os.path.splitext(d)
		    if t == '.gch':
		        yield h
		    if t == '.h':
			yield d
		    if t == '.hpp':
			yield d


        def do_o(proj, target, deps):
            logging.debug("do_o")

            pbs.tools.make.call(['mkdir','-p', os.path.dirname(target)])

	    #cmd = ['g++', '-c', '-H', deps[0], '-o', target] + cargs + gch_inc + include
            #pbs.tools.make.call(cmd)

	    logging.debug("deps")
	    for d in deps:
	        d = os.path.relpath(d, proj.root_dir)
	        logging.debug("  "+d)
	    
            # list of -include options for all gch headers

	    gch_files = list(filter_local_gch(proj, deps))

	    include = list(itertools.chain.from_iterable(("-include",f) for f in gch_files))

	    logging.debug("include\n"+"\n".join("  "+repr(l) for l in include))
	    
            cmd = ['g++', '-c', deps[0], '-o', target] + cargs + gch_inc + inc + include

            pbs.tools.make.call(cmd)

	def do_pre(proj, target, deps):
            pbs.tools.make.call(['mkdir','-p', os.path.dirname(target)])
            pbs.tools.make.call(['g++', '-E', '-H', deps[0], '-o', target] + cargs + inc)
            pbs.tools.make.call(['g++', '-E', deps[0], '-o', target] + cargs + inc)

	def do_pre2(proj, target, deps):
            pbs.tools.make.call(['mkdir','-p', os.path.dirname(target)])
	    pbs.tools.header_dep.func.pre_to_pre2(deps[0], target)
	
	def do_pre3(proj, target, deps):
            pbs.tools.make.call(['mkdir','-p', os.path.dirname(target)])
	    pbs.tools.header_dep.func.pre2_to_pre3(deps[0], target)

	def do_gch(proj, target, deps):
	    h = self.include_block(deps[0])

            pbs.tools.make.call(['mkdir','-p', os.path.dirname(target)])

	    cmd = ['g++', deps[0], '-o', target] + cargs
	    #cmd = ['g++', deps[0], '-o', target] + cargs
	    #cmd = ['g++', '-x', 'c++-header', deps[0], '-o', target] + cargs
            pbs.tools.make.call(cmd)

            head,_ = os.path.splitext(target)

            with open(head,'w') as f:
		f.write("#ifndef "+h+"\n")
		f.write("#define "+h+"\n")
	        f.write("#error gch file missing\n")
		f.write("#endif\n")

	# create text file with a list of header files
	def do_dep(proj, target, deps):
            """
	    convert regular local header files into gch files
	    """
	    pbs.tools.make.call(['mkdir','-p', os.path.dirname(target)])

	    cmd = ['g++', '-E', '-H', deps[0], '-o', '/dev/null'] + cargs + inc
            o,e = pbs.tools.make.call(cmd)
	    
	    def fil(s):
                m = re.match("\.*[ ](\/.*)", s)
                if m:
		    return m.group(1)
		return None

	    e = e.split('\n')

            logging.debug("unfiltered\n"+"\n".join("  {}".format(l) for l in e))

            e = list(fil(l) for l in e)
	    e = list(l for l in e if l)

	    e = list(filter_local_gch_2(proj, e))

            logging.debug("filtered\n"+"\n".join("  {}".format(l) for l in e))

	    with open(target, 'w') as f:
                f.write("\n".join(e))


	h_files = list(self.get_h_files())
	for f in h_files:
	    #rint "  "+f
	    pass
	gch_files = list(self.get_gch_files())
	for f in gch_files:
	    #rint "  "+f
	    pass

        # make rules for general cpp project
	for c in self.get_c_files():
		o = re.sub(
			self.root + r'/(.*)\.cpp$',
			self.get_build_dir() + r'/objects/\1.o',
			c)

		yield pbs.tools.make.Target(
				o,
				[c] + [self.get_dep_for(c)],
				do_o,
				do_o_dep)
	
	for c in self.get_h_files():
		o = re.sub(
			self.root + r'/(.*)\.hpp$',
			self.get_build_dir() + r'/gch/\1.hpp.gch',
			c)
				
		yield pbs.tools.make.Target(o, [c], do_gch)

	for c in self.get_c_files():
		o = re.sub(
			self.root + r'/(.*)\.cpp$',
			self.get_build_dir() + r'/objects/\1.pre',
			c)
				
		yield pbs.tools.make.Target(o, [c] + gch_files, do_pre)

	for c in self.get_c_files():
		o = re.sub(
			self.root + r'/(.*)\.cpp$',
			self.get_build_dir() + r'/depends/\1.txt',
			c)
		
		yield pbs.tools.make.Target(o, [c], do_dep)

	for c in self.get_pre_files():
		o = re.sub(
			self.get_objects_dir() + r'/(.*)\.pre$',
			self.get_objects_dir() + r'/\1.pre2',
			c)
				
		yield pbs.tools.make.Target(o, [c], do_pre2)

	for c in self.get_pre2_files():
		o = re.sub(
			self.get_objects_dir() + r'/(.*)\.pre2$',
			self.get_objects_dir() + r'/\1.pre3',
			c)
				
		yield pbs.tools.make.Target(o, [c], do_pre3)

	yield pbs.tools.make.Target(
	    "precompile_{}".format(self.name),
	    list(self.get_pre3_files()) + list(self.get_dep_files()),
	    None)

    def generate_doxyfile(self):

        self.render2(
            os.path.join(self.proj.compiler_dir, "Doxyfile"),
            os.path.join(self.get_build_dir(), "Doxyfile"))

