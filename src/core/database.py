import threading
from typing import List, Optional
from collections import namedtuple

from i18n import t
from loguru import logger
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    select,
    update,
    func
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, Session

from src.utils.hash import get_short_hash
from .vars import DATABASE_FOLDER


DATABASE_FOLDER.mkdir(parents=True, exist_ok=True)
Base = declarative_base()


class PromptEntry(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt = Column(String, nullable=True)
    alt_prompt = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    error = Column(Boolean, default=False)
    VEO = Column(Boolean, default=False)
    RUNWAY = Column(Boolean, default=False)
    SORA = Column(Boolean, default=False)
    MIDJOURNEY = Column(Boolean, default=False)

PromptRecord = namedtuple("PromptRecord", ["prompt", "alt_prompt", "hash"])


class Database:
    def __init__(self, name: str):
        self.name = name
        self._lock = threading.RLock()
        self.logger = logger.bind(module_name=self.name, module_color="#111111")

        db_path = DATABASE_FOLDER / f"{self.name}.db"
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)

        Base.metadata.create_all(self.engine)
        self.logger.debug(f"DB initialized at {db_path}")

        # Лог количества строк
        with Session(self.engine) as session:
            self.logger.debug(f"Current rows in DB: {self.count_rows()}")

    # ---------------------------
    # Работа с данными
    # ---------------------------
    def get(self, amount: Optional[int] = None, modules: Optional[List[str]] = None) -> List[PromptRecord]:
        with Session(self.engine) as session:
            # Базовый фильтр: без ошибок
            conditions = [(PromptEntry.error == False) | (PromptEntry.error.is_(None))]

            # Если заданы модули, добавляем фильтр "хотя бы один из них не завершён"
            if modules:
                module_conditions = [
                    (getattr(PromptEntry, m) == False) | (getattr(PromptEntry, m).is_(None))
                    for m in modules
                ]
                # хотя бы один из флагов False или NULL
                from sqlalchemy import or_
                conditions.append(or_(*module_conditions))

            # Собираем основной запрос
            query = select(PromptEntry).where(*conditions)

            if amount is not None:
                query = query.limit(amount)

            rows = session.execute(query).scalars().all()

            rows = [
                PromptRecord(r.prompt, r.alt_prompt, r.hash)
                for r in rows
                if r.alt_prompt is not None
            ]
            logger.info(t("info.database.imported_prompts"), amount=len(rows))
            return rows

    def count_rows(self, include_error: bool = True) -> int:
        with Session(self.engine) as session:
            query = select(func.count(PromptEntry.id))
            if not include_error:
                query = query.where((PromptEntry.error == False) | (PromptEntry.error.is_(None)))
            return session.scalar(query)

    # ---------------------------
    # Импорт данных
    # ---------------------------
    def import_prompts(self, prompts: List[str]):
        with Session(self.engine) as session:
            for p in prompts:
                session.add(PromptEntry(prompt=p))
            session.commit()
            self.logger.debug(f"Imported {len(prompts)} prompts")

    def import_alt_prompts(self, prompts: List[str]):
        with Session(self.engine) as session:
            for p in prompts:
                session.add(PromptEntry(alt_prompt=p))
            session.commit()
            self.logger.debug(f"Imported {len(prompts)} alt_prompts")
            self._ensure_hash(session)

    # ---------------------------
    # Хэши
    # ---------------------------
    def _ensure_hash(self, session: Optional[Session] = None):
        own_session = False
        if session is None:
            session = Session(self.engine)
            own_session = True

        rows = session.execute(
            select(PromptEntry).where((PromptEntry.hash.is_(None)) & (PromptEntry.alt_prompt.is_not(None)))
        ).scalars().all()

        total = len(rows)
        if total == 0:
            if own_session:
                session.close()
            return

        self.logger.info(f"Generating hashes for {total} entries")
        for i, row in enumerate(rows, start=1):
            row.hash = get_short_hash(row.alt_prompt)
            self.logger.info(f"{i}/{total} hashed")

        session.commit()
        if own_session:
            session.close()

    # ---------------------------
    # Флаги
    # ---------------------------
    def mark_error(self, value: str, type: str = "hash"):
        with Session(self.engine) as session:
            row = session.execute(
                select(PromptEntry).where(
                    (PromptEntry.prompt == value)
                    | (PromptEntry.alt_prompt == value)
                    | (PromptEntry.hash == value)
                )
            ).scalars().first()

            if row:
                row.error = True
            else:
                kwargs = {type: value, "error": True}
                session.add(PromptEntry(**kwargs))
            session.commit()

    def mark_done(self, value: str, module: str, type: str = "hash"):
        with Session(self.engine) as session:
            row = session.execute(
                select(PromptEntry).where(
                    (PromptEntry.prompt == value)
                    | (PromptEntry.alt_prompt == value)
                    | (PromptEntry.hash == value)
                )
            ).scalars().first()

            if row:
                setattr(row, module, True)
            else:
                kwargs = {type: value, module: True}
                session.add(PromptEntry(**kwargs))
            session.commit()

    def is_done(self, value: str, module: str) -> bool:
        """
        Проверяет, помечена ли запись как завершённая (module=True) или как ошибка (error=True)
        по prompt / alt_prompt / hash.
        """
        with Session(self.engine) as session:
            row = session.execute(
                select(PromptEntry).where(
                    (PromptEntry.prompt == value)
                    | (PromptEntry.alt_prompt == value)
                    | (PromptEntry.hash == value)
                )
            ).scalars().first()

            if not row:
                return False

            # Если есть ошибка — сразу True
            if row.error:
                return True

            # Проверяем флаг модуля (например, VEO, RUNWAY и т.д.)
            if hasattr(row, module) and getattr(row, module):
                return True

            return False