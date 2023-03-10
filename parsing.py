"""Module regrouping functions used to parse different parameters from the command line and the config file."""

from core import *

import json

def parse_args() -> argparse.Namespace:
	"""Parses the arguments from the command line with argparse."""
	parser = argparse.ArgumentParser(prog="mrename", description="Rename indexed files. All parameters specified in the CLI ovveride those in .mrename.json")
	
	parser.add_argument("path", nargs='?', default=Path(), help="The path to the file to rename or to the directory containing the files to rename.")
	parser.add_argument("--prefix", "-p", type=str, help="The prefix of the renamed file(s).")
	parser.add_argument("--copy", "-c", action=argparse.BooleanOptionalAction, help="After renaming the files, copy them to the destination provided with --dest (-d) or in .mrename.json")
	parser.add_argument("--dest", "-d", type=str, help="The path to the directory in which the files will be copied after being renamed.")
	parser.add_argument("--force", action="store_true", help="Rename the file(s) even when copied.")
	parser.add_argument("--format", "-f", type=str, help="A string which indicates the position of the index in the filenames with '{}'. Useful when wanting to disregard a number before the index.")
	
	return parser.parse_args()
	
def parse_option(option: str, env: Environment) -> Any:
	"""Parses the given option from the config and the command line. Command line takes precedence."""
	if option in vars(env.args).keys() and vars(env.args)[option] is not None:
		return vars(env.args)[option]
	if option in env.cfg.keys():
		return env.cfg[option]
	return None

def parse_path(args) -> Path:
	"""Parses the path of the file to process or the directory containing the files to process."""
	path = Path(args.path).expanduser()
	if not path.exists():
		error_exit("The specified file/directory does not exist.")
	return path

def parse_cfg(dirpath: Path, filename: str) -> dict:
	"""Parses the JSON config file if it exists in the given directory."""
	if not dirpath.is_dir():
		return {}
	p = dirpath.joinpath(filename)
	if p.is_file():
		with open(p) as cfg_file:
			try:
				return json.load(cfg_file)
			except json.decoder.JSONDecodeError:
				error_exit("Failed to decode the config file. Aborting.")
	else:
		return {}		

def parse_and_create_dest(env: Environment) -> Path:
	"""Parses the destination path of the files from the command line if it is specified, or from the config file."""
	dest_path_str = parse_option('dest', env)
	if dest_path_str is None:
		error_exit("Please provide a destination directory with '-d' or in a .mrename.json file.")
	
	dest = Path(dest_path_str).expanduser()
	if not dest.exists():
		dest.mkdir(parents=True)
	elif dest.is_file():
		error_exit("The destination directory specified is a file. Aborting.")
		
	return dest
