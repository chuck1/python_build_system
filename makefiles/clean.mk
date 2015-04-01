
clean_pre:
	@rm -f $(build_dir)/*.pre2
	@rm -f $(build_dir)/*.pre2.pre_proj

clean:
	@rm -rf $(build_dir)/*
	@#rm -rf $(build_dir)/depends/
	@#rm -rf $(build_dir)/process/
	@#rm -f $(pch_files)
	@#rm -rf $(binary)

