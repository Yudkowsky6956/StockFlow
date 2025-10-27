import argparse

from src.core.logger import setup_logger
from src.core.menu import start_menu



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Enables debug-mode"
    )
    parser.add_argument(
        "--lang",
        "-l",
        type=str,
        default="en",
        help="Set application language (en/ru)"
    )
    args = parser.parse_args()
    setup_logger(args.debug, args.lang)

    start_menu()

