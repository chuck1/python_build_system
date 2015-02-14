
src       = $(shell find $(src_dir) -name '*.cpp')

inc_files = $(shell find $(inc_dir) -name '*.hpp')

src_in = $(shell find $(src_dir) -name '*.cpp.in')
inc_in = $(shell find $(inc_dir) -name '*.hpp.in')

inc_processed = $(patsubst $(inc_dir)/%.hpp.in, $(build_dir)/processed/inc/%.hpp, $(inc_in))
src_processed = $(patsubst $(src_dir)/%.cpp.in, $(build_dir)/processed/src/%.cpp, $(src_in))
obj_processed = $(patsubst $(src_dir)/%.cpp.in, $(build_dir)/objects/%.cpp.o,     $(src_in))
obj           = $(patsubst $(src_dir)/%.cpp,    $(build_dir)/objects/%.cpp.o,     $(src))
dep_files     = $(patsubst $(src_dir)/%.cpp,    $(build_dir)/depends/%.cpp.d,     $(src))

pch_files     = $(patsubst $(inc_dir)/%.hpp,    $(inc_dir)/%.hpp.gch,             $(inc_files))

GCH = g++ -c -x c++-header

$(obj): $(pch_files)

$(obj): $(build_dir)/objects/%.cpp.o: $(src_dir)/%.cpp
	@bash -c "echo -e \"$(COLOR_BLUE)build $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@mkdir -p $(dir $(build_dir)/depends/$*.cpp.d)
	@$(MAKEDEPEND)
	@$(CC) -c $(CARGS) -o $@ $<

$(obj_processed): $(build_dir)/objects/%.cpp.o: $(build_dir)/processed/src/%.cpp
	@bash -c "echo -e \"$(COLOR_BLUE)build $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@mkdir -p $(dir $(build_dir)/depends/$*.cpp.d)
	@$(MAKEDEPEND)
	@$(CC) -c $(CARGS) -o $@ $<

$(pch_files): $(inc_dir)/%.hpp.gch: $(inc_dir)/%.hpp
	@bash -c "echo -e \"$(COLOR_BLUE)pch $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@$(GCH) $(CARGS) -o $@ $<







