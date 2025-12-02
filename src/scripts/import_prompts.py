from loguru import logger as default_logger
from i18n import t
from InquirerPy import inquirer

from .core_script import ScriptsDB
from src.core.database import Database
from src.interface.file_dialog import select_txt
from src.interface.console_dialog import ask_database


class ImportPrompts(ScriptsDB):
    question_locale = "info.scripts.import_prompts.question"
    original_answer_locale = "info.scripts.import_prompts.original_answer"
    paraphrased_answer_locale = "info.scripts.import_prompts.paraphrased_answer"
    prompts_selected_locale = "info.scripts.import_prompts.prompts_selected"
    success_locale = "info.scripts.import_prompts.success"

    @classmethod
    async def _run(cls):
        logger = default_logger.bind(module_name=cls.__name__)

        file_path = select_txt()
        prompts = file_path.read_text().split("\n")
        logger.info(t(cls.prompts_selected_locale), amount=len(prompts), filename=file_path.name)

        choice = inquirer.select(
            message=t(cls.question_locale),
            choices=[t(cls.original_answer_locale), t(cls.paraphrased_answer_locale)]
        ).execute()

        db_name = ask_database()
        if not db_name:
            return
        db = Database(db_name)

        if choice == t(cls.original_answer_locale):
            db.import_prompts(prompts)
        elif choice == t(cls.paraphrased_answer_locale):
            db.import_alt_prompts(prompts)

        logger.success(t(cls.success_locale), amount=len(prompts), type=choice, database=db_name)
