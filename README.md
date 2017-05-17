# python\_build\_system
python-based c++ project build system to replace cmake

## Features
- create makefiles for static and shared libraries and executables
- library dependencies created using simple python API
- tools for mapping header dependencies, checking for redundant #includes, and moving/renaming headers and automatically updating the code

## HOW TO

### add compiler flags

#### permanently

edit templates in makefiles/

#### temporarily

    # config.py
    project.c_flags = "--flag --flag"

### define an external library

### add defines

    project.add_define("-DFOO=1")

