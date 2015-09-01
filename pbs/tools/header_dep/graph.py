import pickle
import re
import os
import glob
import myos
import sys
import subprocess
import argparse
import networkx as nx
import logging
import graphviz as gv

class Node(object):
    def __init__(self, filename, path_clean, filename_pre):
        self.filename = filename
        self.path_clean = path_clean
        self.filename_pre = filename_pre
    def __str__(self):
        return self.filename_pre

def prefixed(fn, args):
    if args.p:
        if not fn[0:5] == '/usr/':
            fn = os.path.relpath(fn, args.p)
    return fn


def print_degree(g, l = False, ff = None, out = sys.stdout):
    c = 0
    d = g.out_degree()

    if not d:
        return 0
    
    s = sorted(d.items(), cmp = lambda x,y: cmp(x[1],y[1]))
    s = filter(lambda x: ff(x[0].filename), s)
    if not s:
        return 0
    m = min(i[1] for i in s)
    #print "min", m
    for i in s:
        if l:
            if i[1] == m:
                c += 1
                out.write(after_include(i[0].filename) + "\n")
                #print i[1], after_include(i[0].filename)
            else:
                return c
        else:
            print i[0]
            #print i[0]
    return c

def remove_zero(g):
    
    d = g.out_degree()

    s = sorted(d.items(), cmp = lambda x,y: cmp(x[1],y[1]))
    m = min(i[1] for i in s)

    for i in sorted(d.items(), cmp = lambda x,y: cmp(x[1],y[1])):
        if i[1] == m:
            g.remove_node(i[0])

def after_include(filename):
    #print filename
    lst = []
    h,t = os.path.split(filename)
    while t:
        #print "h",h
        #print "t",t
        if t == 'include':
            #print repr(t),"== 'include'"
            break
        else:
            lst.insert(0, t)

        h,t = os.path.split(h)

    return os.path.join(*lst)


def graph_analysis(G, out = sys.stdout):
    i = 0
    while True:
        c = print_degree(G, True, ff=is_header, out=out)
        if c == 0:
            break
        remove_zero(G)
        i += 1

def create_dot(G):

    dot = gv.Digraph()
    
    for n in G.nodes():
        dot.node(n.path_clean, n.filename)
        
    for e in G.edges():
        n0 = e[0]
        n1 = e[1]
        dot.edge(n0.path_clean, n1.path_clean)

    return dot

def clean(s):
    s = re.sub('\.','',s)
    s = re.sub('\/','',s)
    s = re.sub( '-','',s)
    return s

def make_graph(proj, args, ):

    depflat = [d for subl in proj.dep for d in subl]

    G = nx.DiGraph()

    nodes = {}

    # create all nodes first
    for filename,i in zip(proj.files,range(len(proj.files))):
        fp = prefixed(filename, args)
        fc = clean(filename)

        if not args.s and issys(filename):
            continue

        if i in depflat:
            # if prefix specified, use it to shorten names
            if args.p:
                if not filename[0:5] == '/usr/':
                    filename = os.path.relpath(filename, args.p)

            #print "create node:", filename
            n = Node(filename, fc, fp)

            G.add_node(n)
            nodes[filename] = n
    
    # create all edges
    for d in proj.dep:
        #print "create edge"
        f0 = prefixed(proj.files[d[0]], args)
        f1 = prefixed(proj.files[d[1]], args)
        try:
            n0 = nodes[f0]
            n1 = nodes[f1]
        except:
            pass
        else:
            #print f0
            #print f1
            logging.debug("{0}--->{1}".format(n0, n1))

            G.add_edge(n0,n1)

    dot = create_dot(G)
    dot.format = "png"
    dot.render()

    return G


