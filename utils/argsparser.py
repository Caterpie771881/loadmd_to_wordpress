import argparse

def MyBool(value: str):
    if value.lower() in ["t", "true", "1"]:
        return True
    if value.lower() in ["f", "false", "0"]:
        return False
    raise argparse.ArgumentTypeError(f"'{value}' can't change to bool")

argparser = argparse.ArgumentParser()
argparser.add_argument("-c", "--config",
                       metavar='',
                       help="load you config")
argparser.add_argument("-p", "--path",
                       metavar='',
                       help="force specified md path")
argparser.add_argument("-ow", "--over-write",
                       metavar='TRUE/FALSE',
                       help="overwrite exist file",
                       type=MyBool)
argparser.add_argument("--sniffer",
                       help="open sniffer mode by this option",
                       action="store_true")
args = argparser.parse_args()
