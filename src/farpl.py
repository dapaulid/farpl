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
EXCLUDE_DIRS = ['.svn', '.git']
TEXTCHARS = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})


#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
#
def find_and_replace(path, find, replace):
	files = get_files(path)
	occurrences = {}
	total_count = 0
	skipped_files = []
	failed_files = []
	print(HRULE)	
	for file in files:
		try:
			if (is_binary_file(file)):
				#print("%s: skipping binary file" % (file))
				skipped_files.append(file)
				continue
			# end if
		except IOError as e:
			print('[%s] error: %s' % (file, e.strerror))
			failed_files.append(file)
			continue
		# end try
		count = count_occurrences(file, find)
		if count > 0:
			occurrences[file] = count
			total_count += count
			print(HRULE)
		# end if
	# end for
	matched_files = occurrences.keys()

	# do replace
	if replace != None:
		for file in matched_files:
			backup = file + BACKUP_EXT
			copy_file(file, backup)
			with open(backup, 'r') as inp:
				with open(file, 'w') as out:
					for line in inp:
						replaced = line_replace(line, find, replace)
						out.write(replaced)
				# end with
			# end with
		# end for
	# end if

	print("total files    : " + file_summary(files))
	print("matched files  : " + file_summary(matched_files))
	print("skipped files  : " + file_summary(skipped_files))
	print("failed files   : " + file_summary(failed_files))

	# print summary
	if total_count > 0:
		if replace == None:
			print("\n'%s' was found %d times in %d files." 
				% (colored(find, 'red'), total_count, len(matched_files)))
		else:
			print("\n'%s' was replaced with '%s' %d times in %d files." 
				% (colored(find, 'red'), colored(replace, 'green'), total_count, len(matched_files)))
		# end if
	else:	
		print("\n'%s' was not found."
			% (colored(find, 'red')))
	# end if

# end function

#-------------------------------------------------------------------------------
#
def undo(path):
	# determine backup files
	backups = get_backups(path)
	if len(backups) > 0:
		print("restoring files...")
		for backup in backups:
			file = backup[:-len(BACKUP_EXT)]
			print('  ' + file)
			copy_file(backup, file)
			os.remove(backup)
		# end for
	else:
		print("nothing to restore.")
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
def copy_file(src, dst):
	# copy data and metadata
	shutil.copy2(src, dst)
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
def is_binary_file(filename):
	# https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
	with open(filename, 'rb') as f:
		bytes = f.read(1024)
		return bool(bytes.translate(None, TEXTCHARS))
# end function

#-------------------------------------------------------------------------------
#
def file_summary(files):
	summary = "{0:>5d}".format(len(files))
	if len(files) > 0:
		unique_ext = set(['*' + os.path.splitext(file)[1] for file in files])
		if len(unique_ext) <= 16:
			summary += " (%s)" % (", ".join(unique_ext))
		# end if
	# end if
	return summary
# end function

#-------------------------------------------------------------------------------
#
def get_files(path):
	files = []
	for dirpath, dirnames, filenames in os.walk(path):
		# filter directories in-place
		dirnames[:] = [dirname for dirname in dirnames 
			if dirname not in EXCLUDE_DIRS]
		# add files
		files += [os.path.join(dirpath, filename) for filename in filenames 
			if not filename.endswith(BACKUP_EXT)]
	# end for
	return files
# end function

#-------------------------------------------------------------------------------
#
def get_backups(path):
	files = []
	for dirpath, dirnames, filenames in os.walk(path):
		# filter directories in-place
		dirnames[:] = [dirname for dirname in dirnames 
			if dirname not in EXCLUDE_DIRS]
		# add files
		files += [os.path.join(dirpath, filename) for filename in filenames 
			if filename.endswith(BACKUP_EXT)]
	# end for
	return files
# end function

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
#
def main():
	# parse command line
	parser = argparse.ArgumentParser()
	parser.add_argument('find', nargs='?',
		help="text/pattern to find")
	parser.add_argument('replace', nargs='?',
		help="replacement text")
	parser.add_argument('-p', '--path', default=".",
		help="path to file or directory")
	parser.add_argument('-u', '--undo', action='store_true',
		help="undo the last replace operation")
	args = parser.parse_args()
	print(args)

	if args.undo:
		undo(args.path)
	else:
		find_and_replace(args.path, args.find, args.replace)
	# end if
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
