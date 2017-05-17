
doxyfile = $(build_dir)/Doxyfile

#$(doxyfile):
#	@echo Create Doxyfile for $(project_name)
#	doxygen -g $@

doc: $(doxyfile)
	@echo Building documentation for $(project_name)
	doxygen $<

