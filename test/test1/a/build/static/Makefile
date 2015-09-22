
root_dir   = /home/chuck/home/git/pbs/test/test1/a
src_dir    = /home/chuck/home/git/pbs/test/test1/a/src
inc_dir    = /home/chuck/home/git/pbs/test/test1/a/include
build_dir  = /home/chuck/home/git/pbs/test/test1/a/build/static
inc        = -I/home/chuck/home/git/pbs/test/test1/a/include -I/home/chuck/home/git/pbs/test/test1/a/build/static/process/include 
define_str = 
binary     = /home/chuck/home/git/pbs/test/test1/a/build/static/liba.a
compiler_dir = /home/chuck/home/git/pbs
master_config_dir = /home/chuck/home/git/pbs/test/test1
makefile          = /home/chuck/home/git/pbs/test/test1/a/build/static/Makefile
project_name      = a
library_type      = static

depends_dir = $(build_dir)/depends
objects_dir = $(build_dir)/objects
process_dir = $(build_dir)/process

include $(compiler_dir)/makefiles/color.mk

CFLAGS  = -g -std=c++0x -rdynamic -fPIC
CFLAGS += -Wno-format-security
CFLAGS += -Wall -Werror
CFLAGS += -Wno-unused-local-typedefs -Wno-unknown-pragmas

CARGS = $(CFLAGS) $(inc) $(define_str)

.PHONY: all

all: $(binary)
	@bash -c "echo -e \"$(COLOR_BLUE)$(build_dir)$(COLOR_RESET)\""
	@echo CC=$(CC)

MAKEDEPEND = $(CC) -c $(CARGS) -MM $< -MF $(depends_dir)/$*.cpp.d -MT $(objects_dir)/$*.cpp.o


include $(compiler_dir)/makefiles/cpp_library.mk

precompiler: $(pre)

$(binary): $(makefile)

$(binary): $(obj)
	@bash -c "echo -e \"$(COLOR_BLUE)build $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@ar rcs $@ $(filter %.cpp.o, $^)


include $(compiler_dir)/makefiles/clean.mk
include $(compiler_dir)/makefiles/help.mk
include $(compiler_dir)/makefiles/depend.mk
include $(compiler_dir)/makefiles/doc.mk



