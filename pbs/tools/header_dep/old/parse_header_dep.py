#!/usr/bin/python

import re
import os
import glob
import sys
import fnmatch
import gv
import argparse
import logging

def process(fileto,flags):
	global i

	#print fileto[:4],fileto[:4]=="/usr"
	if fileto[:4]=="/usr":
		flag = 3
		#pass
	
	fileto = re.sub('\/nfs\/stak\/students\/r\/rymalc\/usr\/include','',fileto)
	
	logging.debug("fileto {0}".format(fileto))
	
	if 1 in flags or 3 in flags: # decend
		try:
			h = files.index(fileto)
			#print "header file found",h
		except:
			files.append(fileto)
			filetype.append(flags)

			h = len(files)-1
			#print "appending \"{0}\" to files".format(m.group(1))
		
		
		if i==h: #if i[-1]==h:
			#print "skip(already in)                 \"{0}\"".format(fileto)
			pass
		else:
			if 3 in filetype[i]: #elif filetype[i[-1]]==3:
				#print "skip(currently in system header) \"{0}\"".format(fileto)
				pass
			elif 3 in filetype[h]:
				pass
			else:	
				newdep = [i,h] #newdep = [i[-1],h]
				if not newdep in dep:
					dep.append(newdep)
			
			logging.debug("descend   from \"{0:40}\":{1:10} to \"{2:40}\":{3}".format(
						files[i],
						filetype[i],
						fileto,
						flags))

			i = h #i.append(h)
			
			#print "i=",i

	elif 2 in flags: #ascend
		j = files.index(fileto)

		logging.debug("ascending from \"{0:40}\":{1:10} to \"{2:40}\":{3}".format(
				files[i],
				filetype[i],
				files[j],
				filetype[j]))

		
		
		#print line

		i = j #i.pop()
		
		#print "i=",i
	else:
		logging.debug("don't care about...")
		logging.debug(line[0:-2])





###########################################################3333

parser = argparse.ArgumentParser()
parser.add_argument('-v','--verbose',action='store_true')
args = parser.parse_args()

if args.verbose:
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(level=logging.INFO)

cfiles = []
for root, dirnames, filenames in os.walk('.'):
	for filename in fnmatch.filter(filenames, '*.cc'):
		cfiles.append(os.path.join(root, filename))


#['foo.c']

files = cfiles
filetype = [[1]]*len(cfiles)
i = 0

dep = []




for cfile,c in zip(cfiles,range(len(cfiles))):
	
	logging.info("parsing file \"{0}\"".format(cfile))
	
	i = c
	
	root,ext = os.path.splitext(cfile)
	
	additional_opt = ' -DNDEBUG -std=c++0x '
	include_dir    = ' -I. -I../build/src '
	
	os.system("g++ -E " + include_dir + additional_opt + cfile + " > " + root + '.pre')
	
	with open(root + '.pre','r') as f:
		lines = f.readlines()
		#print lines
	
	newlines = []
	for line in lines:
		if line[0]=='#':
			newlines.append(line)
			#print line[:-1]
	
	lines = newlines
	
	for line in lines:
		#print line
		
		header_exts = '|'.join(['h','hh','hpp'])
		
		m = re.search('# \d+ "(\.?[\w\/]+\.(' + header_exts + '))"( \d)( \d)?( \d)?',line)
		if m:
			#print "groups=",len(m.groups())
			g = list(m.groups())
			g = g[2:]
			#print "g",g
			flags = []
			for a in g:
				if a:
					#print "a",a
					flags.append(int(a))
			
			#print flags
			fileto = m.group(1)
			logging.debug(line[:-1])
			#print "match \"{0}\".format(m.group(0))
				
			process(fileto,flags)
		else:
			pass
			#m = re.search('# \d+ "([\w\/]+\.(c|cpp|h|hpp))"',line)
			#if m:
			#	fileto = m.group(1)
			#	if fileto==cfile:
			#		print "return to c file"
			#
			#		process(fileto,1)	

print "cfiles",cfiles
print "files ",files
print "dep   ",dep

filesclean = []
for file in files:
	file = re.sub('\.','',file)
	file = re.sub('\/','',file)
	filesclean.append(file)

depflat = [d for subl in dep for d in subl]

graph = gv.digraph('header_dep')


for file,fileclean,i in zip(files,filesclean,range(len(files))):
	if i in depflat:
		node = gv.node(graph, fileclean);
		gv.setv(node, 'label', file)

for d in dep:
	gv.edge(graph, filesclean[d[0]], filesclean[d[1]])

i
#os.system('cat header_dep.dot')

gv.write(graph, 'header_dep.dot')

os.system('dot header_dep.dot -Tpdf -oheader_dep.pdf')


