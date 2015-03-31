
src       = $(shell find $(src_dir) -name '*.cpp')
inc_files = $(shell find $(inc_dir) -name '*.hpp')

pre           = $(patsubst $(src_dir)/%.cpp,    $(objects_dir)/%.cpp.pre, $(src))
pre2          = $(patsubst $(src_dir)/%.cpp,    $(objects_dir)/%.cpp.pre2, $(src))
pre3          = $(patsubst $(src_dir)/%.cpp,    $(objects_dir)/%.cpp.pre2.pre_proj, $(src))
obj           = $(patsubst $(src_dir)/%.cpp,    $(objects_dir)/%.cpp.o,   $(src))
dep_files     = $(patsubst $(src_dir)/%.cpp,    $(depends_dir)/%.cpp.d,   $(src))

#pch_files     = $(patsubst $(inc_dir)/%.hpp,    $(inc_dir)/%.hpp.gch,             $(inc_files))

GCH = $(CC) -c -x c++-header

precompiler: $(pre2) $(pre3)

$(obj): $(build_dir)/objects/%.cpp.o: $(src_dir)/%.cpp
	@bash -c "echo -e \"$(COLOR_BLUE)build $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@mkdir -p $(dir $(depends_dir)/$*.cpp.d)
	@$(MAKEDEPEND)
	@$(CC) -c $(CARGS) -o $@ $<

$(pre): $(build_dir)/objects/%.cpp.pre: $(src_dir)/%.cpp
	@bash -c "echo -e \"$(COLOR_YELLOW)precompiler $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@$(CC) -E $(CARGS) -o $@ $<

$(pre2): $(build_dir)/objects/%.cpp.pre2: $(build_dir)/objects/%.cpp.pre
	@bash -c "echo -e \"$(COLOR_YELLOW)precompiler2  $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@python /home/chuck/git/chuck1/python/projects/c_projects/gcc_header_dep/pre_to_pre2.py $<

$(pre3): $(build_dir)/objects/%.cpp.pre2.pre_proj: $(build_dir)/objects/%.cpp.pre2
	@bash -c "echo -e \"$(COLOR_YELLOW)precompiler3  $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@python /home/chuck/git/chuck1/python/projects/c_projects/gcc_header_dep/pre2_to_pre3.py $<

$(pch_files): $(inc_dir)/%.hpp.gch: $(inc_dir)/%.hpp
	@bash -c "echo -e \"$(COLOR_BLUE)pch $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@$(GCH) $(CARGS) -o $@ $<


#$(obj): $(pch_files)

# preprocessing
inc_in    = $(shell find $(inc_dir) -name '*.hpp.in')
src_in    = $(shell find $(src_dir) -name '*.cpp.in')

inc_process   = $(patsubst $(inc_dir)/%.hpp.in, $(process_dir)/include/%.hpp,     $(inc_in))

src_process   = $(patsubst $(src_dir)/%.cpp.in, $(process_dir)/src/%.cpp,     $(src_in))
obj_process   = $(patsubst $(src_dir)/%.cpp.in, $(objects_dir)/%.cpp.o,       $(src_in))

pch_in_files  = $(patsubst $(inc_dir)/%.hpp.in, $(process_dir)/include/%.hpp.gch, $(inc_in))

$(inc_process): $(process_dir)/include/%.hpp: $(inc_dir)/%.hpp.in
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

$(pch_in_files): $(process_dir)/include/%.hpp.gch: $(process_dir)/include/%.hpp
	@bash -c "echo -e \"$(COLOR_BLUE)pch $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@$(GCH) $(CARGS) -o $@ $<





