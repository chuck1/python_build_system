
depend: $(dep_files)

dependclean:
	rm -rf $(depends_dir)

$(dep_files): $(depends_dir)/%.cpp.d: $(src_dir)/%.cpp
	@bash -c "echo -e \"$(COLOR_BLUE)build deps $(patsubst $(build_dir)/%,%,$@)$(COLOR_RESET)\""
	@mkdir -p $(dir $(depends_dir)/$*.cpp.d)
	@$(MAKEDEPEND)
	@#@sed -i 's/\(\/neb\/.*\)\.hpp/\1\.hpp.gch/' $@
	@#@sed -i 's/\(\/gal\/.*\)\.hpp/\1\.hpp.gch/' $@

# replace hpp files in dep file with hpp.gch
#sed 's/\(\/neb\/.*\)\.hpp/\1\.hpp.gch/' base.cpp.d

include $(dep_files)




