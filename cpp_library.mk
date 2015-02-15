
src       = $(shell find $(src_dir) -name '*.cpp')
inc_files = $(shell find $(inc_dir) -name '*.hpp')

obj           = $(patsubst $(src_dir)/%.cpp,    $(objects_dir)/%.cpp.o,   $(src))
dep_files     = $(patsubst $(src_dir)/%.cpp,    $(depends_dir)/%.cpp.d,   $(src))

#pch_files     = $(patsubst $(inc_dir)/%.hpp,    $(inc_dir)/%.hpp.gch,             $(inc_files))

GCH = g++ -c -x c++-header

$(obj): $(build_dir)/objects/%.cpp.o: $(src_dir)/%.cpp
	@bash -c "echo -e \"$(COLOR_BLUE)build $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@mkdir -p $(dir $(depends_dir)/$*.cpp.d)
	@$(MAKEDEPEND)
	@$(CC) -c $(CARGS) -o $@ $<


$(pch_files): $(inc_dir)/%.hpp.gch: $(inc_dir)/%.hpp
	@bash -c "echo -e \"$(COLOR_BLUE)pch $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@$(GCH) $(CARGS) -o $@ $<


#$(obj): $(pch_files)

# preprocessing
inc_in    = $(shell find $(inc_dir) -name '*.hpp.in')
src_in    = $(shell find $(src_dir) -name '*.cpp.in')

inc_process   = $(patsubst $(inc_dir)/%.hpp.in, $(process_dir)/inc/%.hpp,     $(inc_in))

src_process   = $(patsubst $(src_dir)/%.cpp.in, $(process_dir)/src/%.cpp,     $(src_in))
obj_process   = $(patsubst $(src_dir)/%.cpp.in, $(objects_dir)/%.cpp.o,       $(src_in))

pch_in_files  = $(patsubst $(inc_dir)/%.hpp.in, $(process_dir)/inc/%.hpp.gch, $(inc_in))

$(inc_process): $(process_dir)/inc/%.hpp: $(inc_dir)/%.hpp.in
	@bash -c "echo -e \"$(COLOR_BLUE)preproc $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@pmake $(master_config_dir) -p $(project_name)$(library_type) $< $@

$(src_process): $(process_dir)/src/%.cpp: $(src_dir)/%.cpp.in
	@bash -c "echo -e \"$(COLOR_BLUE)preproc $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@pmake $(master_config_dir)

#$(obj): $(inc_process) $(pch_in_files)
$(obj): $(inc_process)

$(obj_process): $(objects_dir)/%.cpp.o: $(process_dir)/src/%.cpp
	@bash -c "echo -e \"$(COLOR_BLUE)build $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@mkdir -p $(dir $(depends_dir)/$*.cpp.d)
	@$(MAKEDEPEND)
	@$(CC) -c $(CARGS) -o $@ $<

$(pch_in_files): $(process_dir)/inc/%.hpp.gch: $(process_dir)/inc/%.hpp
	@bash -c "echo -e \"$(COLOR_BLUE)pch $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@$(GCH) $(CARGS) -o $@ $<





