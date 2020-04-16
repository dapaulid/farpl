#!/usr/bin/env python
#-------------------------------------------------------------------------------
#  @license
#  Copyright (c) Daniel Pauli <dapaulid@gmail.com>
#
#  This source code is licensed under the MIT license found in the
#  LICENSE file in the root directory of this source tree.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# imports
#-------------------------------------------------------------------------------
#
import argparse
import os
import glob
import shutil

# third-party
try:
	from termcolor import colored
except ImportError:
	# not installed, use dummy instead
	print("*** HINT: run 'pip install termcolor' to support colored output ***")
	def colored(str, *args): return str
# end try

#-------------------------------------------------------------------------------
# constants
#-------------------------------------------------------------------------------
#
BACKUP_EXT = '_farpl.bak'
HRULE = colored('-' * 80, attrs=['dark'])

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
#
def find_and_replace(path, find, replace):
	files = get_files(path)
	occurrences = {}
	total_count = 0
	print(HRULE)	
	for file in files:
		count = count_occurrences(file, find)
		if count > 0:
			occurrences[file] = count
			total_count += count
			print(HRULE)
		# end if
	# end for

	# do replace
	if replace != None:
		for file in occurrences.keys():
			backup = file + BACKUP_EXT
			shutil.copy2(file, backup)
			with open(backup, 'r') as inp:
				with open(file, 'w') as out:
					for line in inp:
						replaced = line_replace(line, find, replace)
						out.write(replaced)
				# end with
			# end with
		# end for
	# end if

	# print summary
	if total_count > 0:
		# determine extensions of matching files
		extensions = set(['*' + os.path.splitext(file)[1] for file in occurrences.keys()])
		if replace == None:
			print("\n'%s' was found %d times in %d out of %d files (%s)." 
				% (colored(find, 'red'), total_count, len(occurrences), len(files), ", ".join(extensions)))
		else:
			print("\n'%s' was replaced with '%s' %d times in %d out of %d files (%s)." 
				% (colored(find, 'red'), colored(replace, 'green'), total_count, len(occurrences), len(files), ", ".join(extensions)))
		# end if
	else:	
		print("\n'%s' was found 0 times in a total of %d files."
			% (colored(find, 'red'), len(files)))
	# end if

# end function

#-------------------------------------------------------------------------------
#
def count_occurrences(filename, find):
	pretty_filename = colored(filename, 'cyan')
	total_count = 0
	with open(filename, 'r') as inp:
		for i, line in enumerate(inp):
			count = line_count(line, find)
			if count > 0:
				pretty_linenum = colored(i+1, 'magenta')
				pretty_line = line_replace(line, find, colored(find, 'red')).strip()
				print("[%s:%s] %s" % (pretty_filename, pretty_linenum, pretty_line))
				total_count += count
			# end if
		# end for
	# end with
	return total_count
# end function

#-------------------------------------------------------------------------------
#
def line_count(line, find):
	return line.count(find)
# end function

#-------------------------------------------------------------------------------
#
def line_replace(line, old, new):
	return line.replace(old, new)
# end function

#-------------------------------------------------------------------------------
#
def get_files(path):
	return [file for file in glob.glob(path + '/**') if not file.endswith(BACKUP_EXT)]
# end function

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
#
def main():
	# parse command line
	parser = argparse.ArgumentParser()
	parser.add_argument("find", 
		help="text/pattern to find")
	parser.add_argument("replace", 
		help="replacement text")
	parser.add_argument("path", 
		help="path to file or directory")
	args = parser.parse_args()
	print(args)

	find_and_replace(args.path, args.find, args.replace)
	#count_occurrences(args.path, args.find)
# end function

#-------------------------------------------------------------------------------
# entry point
#-------------------------------------------------------------------------------
#
if __name__ == "__main__":
    main()
# end if

#-------------------------------------------------------------------------------
# end of file
#-------------------------------------------------------------------------------
