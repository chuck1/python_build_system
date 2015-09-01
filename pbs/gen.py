#!/usr/bin/env python

import jinja2
import argparse
import os
import inspect
import myos

import pbs.classes.Static
import pbs.settings
import pbs.Project

def gen_func(args):
    project = pbs.Project.Project(os.path.abspath(args.root), args)

    project.save_config()

    project.do()


