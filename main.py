import argparse
import pyrogram

from src.core.logger import setup_logger
from src.interface.main_menu import MainMenu
import src.core.global_config as config


def main():
    MainMenu.run_menu()

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
    config.DEBUG = args.debug
    config.LANG = args.lang
    setup_logger()

    main()

