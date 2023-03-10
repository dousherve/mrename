from parsing import *
from core import *

CFG_FILE = ".mrename.json"

def app():
	args = parse_args()
	path = parse_path(args)
	cfg = parse_cfg(path, CFG_FILE)
	env = Environment(args, cfg)
	
	prefix = parse_option('prefix', env)
	if prefix is None:
		error_exit("Please provide a prefix with '-p' or in a .mrename.json file.")
		
	format = parse_option('format', env)
		
	copy_mode = parse_option('copy', env) or args.dest
	if copy_mode:
		dest = parse_and_create_dest(env)
		copy(path, dest, prefix, format)
	
	if not copy_mode or parse_option('force', env):
		rename(path, prefix, format)

if __name__ == "__main__":
	app()
