src_dir    = /home/chuck/git/chuck1/python_build_system/src
inc_dir    = /home/chuck/git/chuck1/python_build_system/include
build_dir  = /home/chuck/git/chuck1/python_build_system/build
inc        = -I/home/chuck/git/chuck1/python_build_system/include -I/home/chuck/git/chuck1/python_build_system/build/processed/inc -I/home/chuck/git/chuck1/python_build_system/include -I/home/chuck/git/chuck1/python_build_system/build/processed/inc -I/home/chuck/git/chuck1/python_build_system/include -I/home/chuck/git/chuck1/python_build_system/build/processed/inc -I/usr/include/python2.7 -I/home/chuck/git/chuck1/python_build_system/include -I/home/chuck/git/chuck1/python_build_system/build/processed/inc -I/home/chuck/git/chuck1/python_build_system/include -I/home/chuck/git/chuck1/python_build_system/build/processed/inc -I/usr/include/freetype2 -I/home/chuck/git/chuck1/python_build_system/include -I/home/chuck/git/chuck1/python_build_system/build/processed/inc -I/home/chuck/git/chuck1/python_build_system/include -I/home/chuck/git/chuck1/python_build_system/build/processed/inc -I/usr/include/python2.7 -I/home/chuck/physx-3.3.1_linux_sdk_core/Include -I/home/chuck/git/chuck1/python_build_system/include -I/home/chuck/git/chuck1/python_build_system/build/processed/inc -I/usr/include/freetype2 
define_str = -DGLM_FORCE_RADIANS=1 -D_DEBUG=1
binary     = /home/chuck/git/chuck1/python_build_system/build/libnebula_final.a
master_config_dir = None

CC = g++


COLOR_RESET  = \e[0m
COLOR_BLUE   = \e[0;34m
COLOR_GREEN  = \x1b[32;01m
COLOR_RED    = \x1b[31;01m
COLOR_YELLOW = \x1b[33;01m

src    = $(shell find $(src_dir) -name '*.cpp')
src_in = $(shell find $(src_dir) -name '*.cpp.in')
inc_in = $(shell find $(inc_dir) -name '*.hpp.in')

inc_processed = $(patsubst $(inc_dir)/%.hpp.in, $(build_dir)/processed/inc/%.hpp, $(inc_in))
src_processed = $(patsubst $(src_dir)/%.cpp.in, $(build_dir)/processed/src/%.cpp, $(src_in))
obj_processed = $(patsubst $(src_dir)/%.cpp.in, $(build_dir)/objects/%.cpp.o,     $(src_in))
obj           = $(patsubst $(src_dir)/%.cpp,    $(build_dir)/objects/%.cpp.o,     $(src))
dep_files     = $(patsubst $(src_dir)/%.cpp,    $(build_dir)/depends/%.cpp.d,     $(src))

.PHONY: all

all: $(binary)
	@bash -c "echo -e \"$(COLOR_BLUE)$(build_dir)$(COLOR_RESET)\""

s = $(COLOR_BLUE)build$(COLOR_RESET)

CFLAGS = -g -std=c++0x -Wno-format-security

CARGS = $(CFLAGS) $(inc) $(define_str)

$(src_processed): $(build_dir)/processed/src/%.cpp: $(src_dir)/%.cpp.in
	@mkdir -p $(dir $@)
	@pmake $(master_config_dir)

$(inc_processed): $(build_dir)/processed/inc/%.hpp: $(inc_dir)/%.hpp.in
	@mkdir -p $(dir $@)
	@pmake $(master_config_dir) -p $(project_name) $< $@

$(obj): $(build_dir)/objects/%.cpp.o: $(src_dir)/%.cpp
	@bash -c "echo -e \"$(COLOR_BLUE)build $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@$(CC) -c $(CARGS) -o $@ $<

$(obj_processed): $(build_dir)/objects/%.cpp.o: $(build_dir)/processed/src/%.cpp
	@bash -c "echo -e \"$(COLOR_BLUE)build $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@$(CC) -c $(CARGS) -o $@ $<

$(binary): $(obj)
	@bash -c "echo -e \"$(COLOR_BLUE)build $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@ar rcs $@ $^

clean:
	@rm -rf $(build_dir)/*

dependclean:
	@rm -rf $(build_dir)/depends/*

$(dep_files): $(build_dir)/depends/%.cpp.d: $(src_dir)/%.cpp
	@bash -c "echo -e \"$(COLOR_BLUE)build deps $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@rm -f $@
	@$(CC) -c $(CARGS) -MM $^ -MF $@ -MT $(build_dir)/objects/$*.cpp.o
	@#cat $@

include $(dep_files)



