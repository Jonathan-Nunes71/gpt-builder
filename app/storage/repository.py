"""SQLite repository backed by SQLAlchemy."""
from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import Column, DateTime, Integer, MetaData, Numeric, String, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.models.items import ProductItem
from app.utils.fingerprint import fingerprint_content, fingerprint_url


metadata = MetaData()

products_table = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source", String(128), nullable=False, index=True),
    Column("url", String(512), nullable=False, unique=True),
    Column("url_fingerprint", String(64), nullable=False, index=True),
    Column("content_fingerprint", String(64), nullable=False, index=True),
    Column("titre", String(256), nullable=False),
    Column("prix", Numeric(12, 2), nullable=False),
    Column("disponibilite", String(128)),
    Column("crawled_at", DateTime, nullable=False),
)


class Repository:
    """Simple repository to persist and deduplicate products."""

    def __init__(self, database_url: str):
        self.engine: Engine = create_engine(database_url, future=True)
        self.Session = sessionmaker(bind=self.engine, autoflush=False)

    def ensure_schema(self) -> None:
        metadata.create_all(self.engine)

    @contextmanager
    def session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    def is_duplicate(self, url_fp: str, item: ProductItem) -> bool:
        content_fp = fingerprint_content(item.titre + str(item.prix))
        query = products_table.select().where(
            products_table.c.url_fingerprint == url_fp,
            products_table.c.content_fingerprint == content_fp,
        )
        with self.engine.connect() as conn:
            result = conn.execute(query).first()
            return result is not None

    def save_item(self, item: ProductItem) -> None:
        url_fp = fingerprint_url(item.url)
        content_fp = fingerprint_content(item.titre + str(item.prix))
        insert_stmt = products_table.insert().values(
            source=item.source,
            url=item.url,
            url_fingerprint=url_fp,
            content_fingerprint=content_fp,
            titre=item.titre,
            prix=item.prix,
            disponibilite=item.disponibilite,
            crawled_at=item.crawled_at,
        )
        with self.engine.begin() as conn:
            conn.execute(insert_stmt)

    def close(self) -> None:
        self.engine.dispose()
