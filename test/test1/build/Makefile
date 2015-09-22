include files/vars.make


CC = g++
export CC

.PHONY: all2

all2: Makefile $(make_files) $(projects)

all3: Makefile $(make_files)
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/a/build/static/Makefile  --no-print-directory
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/test1/build/Makefile  --no-print-directory

help:
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/a/build/static/Makefile help --no-print-directory
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/test1/build/Makefile help --no-print-directory

clean:
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/a/build/static/Makefile clean --no-print-directory
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/test1/build/Makefile clean --no-print-directory

clean_pre:
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/a/build/static/Makefile clean_pre --no-print-directory
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/test1/build/Makefile clean_pre --no-print-directory

dependclean:
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/a/build/static/Makefile dependclean --no-print-directory
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/test1/build/Makefile dependclean --no-print-directory

depend:
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/a/build/static/Makefile depend --no-print-directory
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/test1/build/Makefile depend --no-print-directory

.PHONY: a
.PHONY: test1
.PHONY: a_PRE
.PHONY: test1_PRE

a_PRE:  
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/a/build/static/Makefile --no-print-directory

test1_PRE: a_PRE
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/test1/build/Makefile --no-print-directory

a: a_PRE 

test1: test1_PRE 



doc:
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/a/build/static/Makefile doc --no-print-directory
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/test1/build/Makefile doc --no-print-directory

header_dep:
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/a/build/static/Makefile precompiler --no-print-directory
	@$(MAKE) -f /home/chuck/home/git/pbs/test/test1/test1/build/Makefile precompiler --no-print-directory

doc_all:
	@doxygen Doxyfile

Makefile: $(config_file_str) $(compiler_file)
	@pbs gen ..

