"""Module regrouping functions to rename/copy files."""

import sys, argparse, shutil
from pathlib import Path
from typing import Any, NamedTuple

class Environment(NamedTuple):
	args: argparse.Namespace
	cfg: dict[str, Any]
	
def error_exit(msg: str):
	print(msg, file=sys.stderr)
	sys.exit(1)
	
def find_index(filename: str, format: str = "") -> int:
	"""
	If no format is specified, returns the first number present in the given filename.
	Else, returns the index present in the given filename according to the provided format.
	Used to skip potential numbers before the index.
	Only the position of the '{}' in the format string matters, the rest is disregarded.
	Returns -1 if no index is found.
	"""
	if format is not None and format != "":
		try:
			filename = filename[format.index('{}'):]
		except:
			error_exit("Invalid format. Cannot find {}.")
	else:
		while len(filename) > 0 and not filename[0].isdigit():
			filename = filename[1:]
	if len(filename) == 0:
		return -1
	i = 0
	while i < len(filename) and filename[i].isdigit():
		i += 1
	try:
		return int(filename[:i])
	except:
		return -1	

def is_formatted(filepath: Path, prefix: str) -> bool:
	name = filepath.stem
	if not name.startswith(prefix):
		return False
	name = name[len(prefix):]	
	try:
		int(name)
		return True
	except:
		return False

def formatted_filename(path: Path, prefix: str, format: str = "") -> str:
	"""Returns the new name of the given file. Returns an empty string if an index can't be found."""
	index = find_index(path.name, format)
	if index != -1:
		# TODO: Does not work with "multiple" extensions, for instance .tar.gz (discards the .tar)
		# ''.join(suffixes) fixes this but breaks 'Ch. 51.cbz' for instance (-> 'Ch-51. 51.cbz')
		# How to differentiate both cases ?
		return "{}{:02d}{}".format(prefix, index, path.suffix)
	else:
		return ""
	
def to_process(dir: Path):
	"""Returns an array of all the files to process in the given directory."""
	return [f for f in dir.iterdir() if not (f.is_dir() or f.name.startswith('.'))]

def rename_file(path: Path, prefix: str, format: str = "") -> bool:
	"""Renames a single file with the given prefix."""
	if is_formatted(path, prefix):
		return False
	name = formatted_filename(path, prefix, format)
	if name == "":
		return False
	new_path = path.with_name(name)
	if not new_path == path and not new_path.exists():
		path.rename(new_path)
		return True
	return False
	
def rename_all_files_in_dir(dir: Path, prefix: str, format: str = "") -> tuple[int, int, int]:
	"""
	Renames all the files in the given directory with the given prefix.
	Returns the number of renamed files, the number of unrenamed files and the total number of processed files.
	"""
	renamed_count = 0
	unrenamed_count = 0
	for filepath in to_process(dir):
		if rename_file(filepath, prefix, format):
			renamed_count += 1
		else:
			unrenamed_count += 1
	return (renamed_count, unrenamed_count, renamed_count + unrenamed_count)

def copy_file(src: Path, dest: Path, prefix: str, format: str = "") -> bool:
	"""
	Copies the given file to the destination directory with the correct name.
	Does not copy it if an indexed name cannot be found or if the target file already exists.
	"""
	if not is_formatted(src, prefix):
		name = formatted_filename(src, prefix, format)
		if name == "":
			return False
	else:
		name = src.name
	dest_filepath = dest.joinpath(name)
	if not dest_filepath.exists():
		shutil.copy(src, dest_filepath)
		return True
	else:
		return False
		
def copy_all_files_in_dir(src: Path, dest: Path, prefix: str, format: str = "") -> tuple[int, int, int]:
	"""
	Copies all the files in the given directory to the destination directory with the correct names.
	Does not copy the files for which an indexed name cannot be found or if the target file already exists.
	"""
	uncopied_count = 0
	copied_count = 0
	for filepath in to_process(src):
		if copy_file(filepath, dest, prefix, format):
			copied_count += 1
		else:
			uncopied_count += 1
	return (copied_count, uncopied_count, copied_count + uncopied_count)
	
def rename(path: Path, prefix: str, format: str = ""):
	"""
	If the given path points to a directory, renames all files in it with the given prefix.
	If the given path points to a file, renames it with the given prefix.
	Does not do anything with files for which an index cannot be found, or if the name is already correct.
	"""
	if path.is_dir():
		res = rename_all_files_in_dir(path, prefix, format)
		print(f"{res[2]} files processed.", end=' ')
		if res[0] == 0:
			print("No file renamed.")
		elif res[0] == res[2]:
			print("All files renamed.")
		else:
			print(f"{res[0]} renamed. {res[1]} unchanged.")
	else:
		if not rename_file(path, prefix, format):
			print("File not renamed.")
		
def copy(src: Path, dest: Path, prefix: str, format: str = ""):
	"""
	If the given source path points to a directory,
	copies all files in it to the destination directory with the given prefix.
	If the given source path points to a file,
	copies it to the destination directory with the given prefix.
	Does not do anything with files for which an index cannot be found,
	or if the target file already exists.
	"""
	if src.is_dir():
		res = copy_all_files_in_dir(src, dest, prefix, format)
		print(f"{res[2]} files processed.", end=' ')
		if res[0] == 0:
			print("No file copied.")
		elif res[0] == res[2]:
			print("All files copied.")
		else:
			print(f"{res[0]} copied. {res[1]} not copied.")
	else:
		if not copy_file(src, dest, prefix, format):
			print("File not copied.")
