import sqlite3
from collections import namedtuple
from pathlib import Path

from loguru import logger
from tqdm import tqdm

from src.utils.hash import get_short_hash
from .vars import DATABASE_FOLDER

PromptRecord = namedtuple("PromptRecord", ["prompt", "alt_prompt", "hash"])


class Database:
    REQUIRED_COLUMNS = {
        "prompt": "TEXT",
        "alt_prompt": "TEXT",
        "hash": "TEXT",
        "error": "INTEGER",
        "VEO": "INTEGER",
        "RUNWAY": "INTEGER",
        "SORA": "INTEGER",
        "MINIMAX": "INTEGER",
        "LUMA": "INTEGER",
        "MIDJOURNEY": "INTEGER",
        "NANO": "INTEGER",
    }

    def __init__(self, name: str):
        self.name = name
        self.path = DATABASE_FOLDER / f"{name}.db"
        self.logger = logger.bind(module=name)

    # -------------------- context --------------------
    def __enter__(self):
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        self._ensure_schema()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def commit(self):
        self.connection.commit()

    # -------------------- schema --------------------
    @property
    def existing_columns(self) -> set[str]:
        self.cursor.execute(f'PRAGMA table_info("{self.name}")')
        return {row[1] for row in self.cursor.fetchall()}

    def _ensure_schema(self):
        self._ensure_table()
        self._ensure_columns()
        self._ensure_hash_filled()

    def _ensure_table(self):
        cols = ", ".join(f'"{name}" {type_}' for name, type_ in self.REQUIRED_COLUMNS.items())
        self.cursor.execute(
            f'''
            CREATE TABLE IF NOT EXISTS "{self.name}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {cols}
            )
            '''
        )
        self.commit()

    def _ensure_columns(self):
        existing = self.existing_columns
        for name, type_ in self.REQUIRED_COLUMNS.items():
            if name not in existing:
                self.logger.debug(f'Adding column "{name}"')
                self.cursor.execute(f'ALTER TABLE "{self.name}" ADD COLUMN "{name}" {type_}')
                if type_.upper().startswith("INT"):
                    self.cursor.execute(f'UPDATE "{self.name}" SET "{name}" = 0 WHERE "{name}" IS NULL')
        self.commit()

    def _ensure_hash_filled(self):
        self.cursor.execute(
            f'''
            SELECT id, alt_prompt
            FROM "{self.name}"
            WHERE alt_prompt IS NOT NULL
              AND alt_prompt != ''
              AND hash IS NULL
            '''
        )
        rows = self.cursor.fetchall()
        if not rows:
            return
        self.logger.debug(f"Filling hash for {len(rows)} rows")
        for row_id, alt_prompt in rows:
            self.cursor.execute(
                f'UPDATE "{self.name}" SET hash = ? WHERE id = ?',
                (get_short_hash(alt_prompt), row_id)
            )
        self.commit()

    # -------------------- CRUD --------------------
    def get_not_paraphrased(self, amount: int | None = None) -> list[PromptRecord]:
        sql = f'''
            SELECT prompt, alt_prompt, hash
            FROM "{self.name}"
            WHERE (alt_prompt IS NULL OR alt_prompt = '')
              AND COALESCE("error", 0) = 0
            ORDER BY ROWID DESC
        '''
        params = []
        if amount:
            sql += " LIMIT ?"
            params.append(amount)
        self.cursor.execute(sql, params)
        return [PromptRecord(*row) for row in self.cursor.fetchall()]

    def insert_prompt(self, prompt: str, alt_prompt: str = "", error: int = 0, **modules) -> None:
        """Добавляет один prompt через create_row"""
        if not prompt and not alt_prompt:
            raise ValueError("Either prompt or alt_prompt is required")
        values = {}
        for col in self.REQUIRED_COLUMNS:
            if col == "prompt":
                values[col] = prompt
            elif col == "alt_prompt":
                values[col] = alt_prompt
            elif col == "hash":
                source = alt_prompt or prompt
                values[col] = get_short_hash(source) if source else ""
            elif col == "error":
                values[col] = int(error)
            else:
                values[col] = int(modules.get(col, 0))
        self.create_row(**values)

    def insert_prompts_bulk(self, prompts: list[dict], batch_size: int = 500):
        """Вставка пачками через executemany для ускорения"""
        columns = list(self.REQUIRED_COLUMNS.keys())
        placeholders = ",".join("?" for _ in columns)
        sql = f'INSERT INTO "{self.name}" ({",".join(columns)}) VALUES ({placeholders})'

        batch = []
        with tqdm(total=len(prompts), desc="Inserting prompts", unit="row") as pbar:
            for rec in prompts:
                row = []
                for col in columns:
                    if col == "hash":
                        source = rec.get("alt_prompt") or rec.get("prompt") or ""
                        row.append(get_short_hash(source))
                    elif col in rec:
                        row.append(rec[col])
                    else:
                        row.append(0 if self.REQUIRED_COLUMNS[col].upper().startswith("INT") else "")
                batch.append(tuple(row))
                if len(batch) >= batch_size:
                    self.cursor.executemany(sql, batch)
                    self.commit()
                    pbar.update(len(batch))
                    batch.clear()
            if batch:
                self.cursor.executemany(sql, batch)
                self.commit()
                pbar.update(len(batch))

    def create_row(self, **values):
        if not values:
            raise ValueError("At least one value required")
        columns = []
        params = []
        for name in self.REQUIRED_COLUMNS:
            if name in values:
                columns.append(f'"{name}"')
                val = values[name]
                params.append(int(val) if isinstance(val, bool) else val)
        sql = f'''
            INSERT INTO "{self.name}"
            ({", ".join(columns)})
            VALUES ({", ".join("?" for _ in params)})
        '''
        self.cursor.execute(sql, params)
        self.commit()

    def get(self, modules: list[str], amount: int | None = None) -> dict:
        result = {}
        for module in modules:
            if module not in self.REQUIRED_COLUMNS:
                raise ValueError(f"Unknown module: {module}")
            sql = f'''
                SELECT prompt, alt_prompt, hash
                FROM "{self.name}"
                WHERE alt_prompt IS NOT NULL
                  AND alt_prompt != ''
                  AND COALESCE("error", 0) = 0
                  AND COALESCE("{module}", 0) = 0
                ORDER BY ROWID DESC
            '''
            params = []
            if amount:
                sql += " LIMIT ?"
                params.append(amount)
            self.cursor.execute(sql, params)
            result[module] = [PromptRecord(*row) for row in self.cursor.fetchall()]
        return result

    def mark_error(self, value: str) -> bool:
        self.cursor.execute(
            f'UPDATE "{self.name}" SET error = 1 WHERE prompt = ? OR alt_prompt = ? OR hash = ?',
            (value, value, value)
        )
        self.commit()
        return self.cursor.rowcount > 0

    def is_error(self, value: str) -> bool:
        self.cursor.execute(
            f'SELECT 1 FROM "{self.name}" WHERE (prompt = ? OR alt_prompt = ? OR hash = ?) AND COALESCE(error,0)=1 LIMIT 1',
            (value, value, value)
        )
        return self.cursor.fetchone() is not None

    def is_done(self, value: str, module: str) -> bool:
        if module not in self.REQUIRED_COLUMNS:
            raise ValueError(f"Unknown module: {module}")
        self.cursor.execute(
            f'''SELECT 1 FROM "{self.name}"
               WHERE (prompt = ? OR alt_prompt = ? OR hash = ?)
                 AND (COALESCE(error,0)=1 OR COALESCE("{module}",0)=1)
               LIMIT 1''',
            (value, value, value)
        )
        return self.cursor.fetchone() is not None

    def mark_done(self, value: str, module: str) -> bool:
        self.cursor.execute(
            f'UPDATE "{self.name}" SET "{module}" = 1 WHERE prompt = ? OR alt_prompt = ? OR hash = ?',
            (value, value, value)
        )
        self.commit()
        return self.cursor.rowcount > 0

    def set_paraphrased(self, value: str, paraphrased: str) -> bool:
        self.cursor.execute(
            f'UPDATE "{self.name}" SET alt_prompt = ? WHERE hash = ? OR prompt = ?',
            (paraphrased, value, value)
        )
        self.commit()
        return self.cursor.rowcount > 0

    # -------------------- utils --------------------
    def ensure_hash(self):
        self.cursor.execute(f'SELECT id, alt_prompt FROM "{self.name}" WHERE hash IS NULL AND alt_prompt IS NOT NULL')
        rows = self.cursor.fetchall()
        for row_id, alt_prompt in rows:
            self.cursor.execute(f'UPDATE "{self.name}" SET hash = ? WHERE id = ?', (get_short_hash(alt_prompt), row_id))
        self.commit()
