import sqlite3
from collections import namedtuple

from loguru import logger
from i18n import t

from .vars import DATABASE_FOLDER
from ..utils.hash import get_short_hash


PromptRecord = namedtuple("PromptRecord", ["prompt", "alt_prompt", "hash"])


class Database:
    REQUIRED_COLUMNS = [
        {"name": "prompt", "type": "TEXT"},
        {"name": "alt_prompt", "type": "TEXT"},
        {"name": "hash", "type": "TEXT"},
        {"name": "error", "type": "INTEGER"},
        {"name": "VEO", "type": "INTEGER"},
        {"name": "RUNWAY", "type": "INTEGER"},
        {"name": "SORA", "type": "INTEGER"},
        {"name": "MINIMAX", "type": "INTEGER"},
        {"name": "LUMA", "type": "INTEGER"},
        {"name": "MIDJOURNEY", "type": "INTEGER"},
        {"name": "NANO", "type": "INTEGER"}
    ]

    def __init__(self, name: str):
        self.name = name
        self.path = DATABASE_FOLDER / f"{name}.db"
        self.logger = logger.bind(module=self.name)
        self.logger.debug("DB Initialized.")


    def __enter__(self):
        """Запускает соединение с БД"""
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        self._ensure_all_exists()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Останавливает соединение с БД"""
        self.connection.close()

    def commit(self):
        self.connection.commit()

    @property
    def existing_columns(self):
        self.cursor.execute(f"PRAGMA table_info({self.name})")
        existing_columns = [row[1] for row in self.cursor.fetchall()]
        return existing_columns

    def get(self, amount: int = None, modules: list[str] | str = None) -> dict:
        """
        Возвращает словарь вида:
        {
            "VEO": [PromptRecord, ...],
            "SORA": [...],
            ...
        }

        Для каждого модуля выбирает amount строк, где:
            - alt_prompt НЕ NULL и не пустой
            - error != 1
            - module != 1
        """

        # Если передали одну строку — превращаем в список
        if isinstance(modules, str):
            modules = [modules]

        if modules is None:
            modules = []

        # Проверка что modules — список строк
        if not isinstance(modules, list) or not all(isinstance(m, str) for m in modules):
            raise ValueError("Modules должен быть строкой или списком строк")

        result = {}

        for module in modules:
            # Проверяем, что колонка существует
            if module.upper() not in (col["name"] for col in self.REQUIRED_COLUMNS):
                raise ValueError(f"Неизвестный модуль: {module}")

            query = f"""
                SELECT prompt, alt_prompt, hash
                FROM "{self.name}"
                WHERE alt_prompt IS NOT NULL
                  AND alt_prompt != ''
                  AND error != 1
                  AND "{module}" != 1
                ORDER BY ROWID DESC
            """

            params = []
            if amount is not None:
                query += " LIMIT ?"
                params.append(amount)

            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()

            result[module] = [
                PromptRecord(prompt=row[0], alt_prompt=row[1], hash=row[2])
                for row in rows
            ]

        return result

    def get_not_paraphrased(self, amount: int = None) -> list[PromptRecord]:
        self.cursor.execute(f'''
            SELECT prompt, alt_prompt, hash FROM "{self.name}"
            WHERE prompt IS NOT NULL AND alt_prompt IS NULL
        ''')
        rows = self.cursor.fetchall()

        result = []
        for prompt, alt_prompt, _hash in rows:
            result.append(PromptRecord(prompt, alt_prompt, _hash))
            if amount and len(result) >= amount:
                break

        self.logger.info(t("info.database.imported_prompts"), amount=len(result))
        return result

    def _ensure_column_exists(self, column: dict):
        """Проверяет, что колонка существует и заменяет NULL на 0 для INTEGER"""
        if column["name"] not in self.existing_columns:
            self.logger.debug(f'Column with name "{column["name"]}" not exists, creating it…')
            self.cursor.execute(f'ALTER TABLE "{self.name}" ADD COLUMN {column["name"]} {column["type"]}')
            self.commit()

        if column["type"].upper() in ("INTEGER", "INT", "BIGINT", "SMALLINT"):
            self.logger.debug(f'Filling NULLs with 0 in column "{column["name"]}"…')
            self.cursor.execute(
                f'UPDATE "{self.name}" SET "{column["name"]}" = 0 WHERE "{column["name"]}" IS NULL'
            )
            self.commit()

    def _ensure_table_exists(self):
        columns_sql = ", ".join(f"{col["name"]} {col["type"]}" for col in self.REQUIRED_COLUMNS)
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS \"{self.name}\" (
            id INTEGER PRIMARY KEY AUTOINCREMENT, {columns_sql}
            )"""
        )

    def _ensure_all_exists(self):
        """Проверяет наличие таблицы и нужных колонок, создаёт при необходимости."""
        self._ensure_table_exists()
        for col in self.REQUIRED_COLUMNS:
            self._ensure_column_exists(col)
        self.commit()


    def is_done(self, value: str, module: str) -> bool:
        """Проверяет сделан ли value в module.
        (Возвращает True, если в error стоит 1 или в module стоит 1)
        """
        return self.is_error(value) or self.is_marked(value, module)

    def is_error(self, value: str) -> bool:
        """Проверяет помечен ли value как ошибочный"""
        return self.is_marked(value, "error")

    def is_marked(self, value: str, module: str) -> bool:
        """Общий модуль для проверки 1 в колонке module по value"""
        self.cursor.execute(
            f"""SELECT 1 FROM \"{self.name}\"
            WHERE (prompt = ? OR alt_prompt = ? OR hash = ?)
                AND \"{module}\" = 1
            LIMIT 1""",
            (value, value, value)
        )
        return self.cursor.fetchone() is not None


    def mark_error(self, value: str):
        """Маркирует данный value ошибочным"""
        self.mark_done(value, "error")

    def mark_done(self, value: str, module: str) -> bool:
        """Общий метод для маркировки"""
        self.cursor.execute(
            f"""UPDATE \"{self.name}\"
            SET \"{module}\" = 1
            WHERE prompt = ? OR alt_prompt = ? OR hash = ?
            """,
            (value, value, value)
        )
        self.commit()
        return bool(self.cursor.rowcount)

    def set_paraphrased(self, value: str, paraphrased: str) -> bool:
        """
        Находит строку, где hash=value или prompt=value,
        и устанавливает alt_prompt=paraphrased.
        Возвращает True, если строка была обновлена.
        """
        self.cursor.execute(
            f"""
            UPDATE "{self.name}"
            SET alt_prompt = ?
            WHERE hash = ? OR prompt = ?
            """,
            (paraphrased, value, value)
        )
        self.commit()
        return bool(self.cursor.rowcount)

    def create_row(
            self,
            prompt: str = None,
            alt_prompt: str = None,
            _hash: str = None,
            error: bool = None,
            veo: bool = None,
            runway: bool = None,
            sora: bool = None,
            midjourney: bool = None
        ):
        if not (prompt or alt_prompt or _hash):
            raise ValueError("Required at least one of these parameters: prompt, alt_prompt, _hash")
        self.cursor.execute(f"""
        INSERT INTO \"{self.name}\" 
        (prompt, alt_prompt, hash, error, VEO, RUNWAY, SORA, MIDJOURNEY)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prompt,
            alt_prompt,
            _hash,
            int(error) if error is not None else None,
            int(veo) if veo is not None else None,
            int(runway) if runway is not None else None,
            int(sora) if sora is not None else None,
            int(midjourney) if midjourney is not None else None,
        ))
        self.commit()

    def _ensure_hash(self):
        self.cursor.execute(f"""
            SELECT id, alt_hash FROM "{self.name}"
            WHERE hash IS NULL AND alt_hash IS NOT NULL
        """)
        rows = self.cursor.fetchall()
        total = len(rows)

        # Локализованные логи
        self.logger.info(t("info.database.ensure_hash.rows_found"), amount=total)
        self.logger.info(t("info.database.ensure_hash.start"))

        if total == 0:
            self.logger.info(t("info.database.ensure_hash.done"))
            return

        next_percent_log = 10  # следующий порог для логирования в процентах

        for index, (row_id, alt_hash) in enumerate(rows, start=1):
            short_hash = get_short_hash(alt_hash)
            self.cursor.execute(
                f'UPDATE "{self.name}" SET hash = ? WHERE id = ?',
                (short_hash, row_id)
            )

            percent_done = (index / total) * 100
            if percent_done >= next_percent_log:
                self.logger.info(
                    t("info.database.ensure_hash.progress"),
                    percent=int(percent_done),
                    processed=index,
                    total=total,
                    last_id=row_id
                )
                next_percent_log += 10  # следующий порог

        self.commit()
        self.logger.info(t("info.database.ensure_hash.done"))

    def import_prompts(self, prompts: list[str]):
        """Импортирует список prompt в таблицу"""
        for p in prompts:
            self.create_row(prompt=p)
        self.commit()
        self.logger.debug(f"Imported {len(prompts)} prompts")

    def import_alt_prompts(self, prompts: list[str]):
        """Импортирует список alt_prompt в таблицу и заполняет hash, если нужно"""
        for p in prompts:
            self.create_row(alt_prompt=p)
        self.commit()
        self.logger.debug(f"Imported {len(prompts)} alt_prompts")
        self._ensure_hash()