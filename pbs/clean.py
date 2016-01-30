#!/usr/bin/env python

import jinja2
import argparse
import os
import inspect

import pbs.classes.Static
import pbs.settings
import pbs.Project
import pbs.func

def func_clean(args):
    d = pbs.func.read_config_file()
    
    project = pbs.Project.Project(d['root'], args)
   
    project.do()
    
    project.clean()


