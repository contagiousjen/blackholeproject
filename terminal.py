import sys
import config as cfg
import file as f


def parse_args():
    if ((len(sys.argv) == 2) and (sys.argv[1] == '-help')):
        print(cfg.HELP_MSG)
        sys.exit(cfg.OK)
        
    elif ((len(sys.argv) == 3) and (sys.argv[1] == '-generate')):
        f.generate_file()
        sys.exit(cfg.OK)

    elif (len(sys.argv) != 1):
        print(cfg.CALL_ERROR_MSG)
        sys.exit(cfg.INVALID_CALL)

def get_file_name(option):
    if option:
        name = input(cfg.OUTPUT_FILE_MSG)
        if not name:
            name = cfg.DEFAULT_OUTPUT_NAME
        return name
    else:
        name = input(cfg.INPUT_FILE_MSG)
        if not name:
            name = cfg.DEFAULT_INPUT_NAME
        return name
        
