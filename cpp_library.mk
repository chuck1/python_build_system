
src    = $(shell find $(src_dir) -name '*.cpp')
src_in = $(shell find $(src_dir) -name '*.cpp.in')
inc_in = $(shell find $(inc_dir) -name '*.hpp.in')

inc_processed = $(patsubst $(inc_dir)/%.hpp.in, $(build_dir)/processed/inc/%.hpp, $(inc_in))
src_processed = $(patsubst $(src_dir)/%.cpp.in, $(build_dir)/processed/src/%.cpp, $(src_in))
obj_processed = $(patsubst $(src_dir)/%.cpp.in, $(build_dir)/objects/%.cpp.o,     $(src_in))
obj           = $(patsubst $(src_dir)/%.cpp,    $(build_dir)/objects/%.cpp.o,     $(src))
dep_files     = $(patsubst $(src_dir)/%.cpp,    $(build_dir)/depends/%.cpp.d,     $(src))

