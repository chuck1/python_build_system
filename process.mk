
$(src_processed): $(build_dir)/processed/src/%.cpp: $(src_dir)/%.cpp.in
	@mkdir -p $(dir $@)
	@pmake $(master_config_dir)

$(inc_processed): $(build_dir)/processed/inc/%.hpp: $(inc_dir)/%.hpp.in
	@mkdir -p $(dir $@)
	@pmake $(master_config_dir) -p $(project_name)$(library_type) $< $@

