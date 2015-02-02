

dependclean:
	@rm -rf $(build_dir)/depends/*

$(dep_files): $(build_dir)/depends/%.cpp.d: $(src_dir)/%.cpp
	@bash -c "echo -e \"$(COLOR_BLUE)build deps $@$(COLOR_RESET)\""
	@mkdir -p $(dir $@)
	@rm -f $@
	@$(CC) -c $(CARGS) -MM $^ -MF $@ -MT $(build_dir)/objects/$*.cpp.o
	@#cat $@

include $(dep_files)




