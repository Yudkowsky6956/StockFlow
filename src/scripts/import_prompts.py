from loguru import logger
from i18n import t
from InquirerPy import inquirer

from src.core.database import Database
from src.interface.select import select_database, select_txt


def import_prompts():
    question = t("info.scripts.import_prompts.question")
    original_answer = t("info.scripts.import_prompts.original_answer")
    paraphrased_answer = t("info.scripts.import_prompts.paraphrased_answer")

    file_path = select_txt()
    choice = inquirer.select(
        message=question,
        choices=[original_answer, paraphrased_answer]
    ).execute()


    db_name = select_database()
    db = Database(db_name)

    prompts = file_path.read_text().split("\n")

    if choice == original_answer:
        db.import_prompts(prompts)
    elif choice == paraphrased_answer:
        db.import_alt_prompts(prompts)

    logger.success(t("info.scripts.import_prompts.success"), amount=len(prompts), type=choice, database=db_name)