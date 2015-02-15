
clean:
	@rm -rf $(build_dir)/objects/*
	@rm -rf $(build_dir)/depends/*
	@rm -rf $(build_dir)/process/*
	@rm -f $(pch_files)
	@rm -rf $(binary)

