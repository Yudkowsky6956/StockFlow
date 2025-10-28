from loguru import logger
from i18n import t
from InquirerPy import inquirer

from src.core.database import Database
from src.interface.file_dialog import select_txt
from src.interface.console_dialog import ask_database


def import_prompts():
    question = t("info.scripts.import_prompts.question")
    original_answer = t("info.scripts.import_prompts.original_answer")
    paraphrased_answer = t("info.scripts.import_prompts.paraphrased_answer")

    file_path = select_txt()
    prompts = file_path.read_text().split("\n")
    logger.info(t("info.scripts.import_prompts.prompts_selected"), amount=len(prompts), filename=file_path.name)

    choice = inquirer.select(
        message=question,
        choices=[original_answer, paraphrased_answer]
    ).execute()

    db_name = ask_database()
    if not db_name:
        return
    db = Database(db_name)

    if choice == original_answer:
        db.import_prompts(prompts)
    elif choice == paraphrased_answer:
        db.import_alt_prompts(prompts)

    logger.success(t("info.scripts.import_prompts.success"), amount=len(prompts), type=choice, database=db_name)