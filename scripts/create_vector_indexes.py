from sqlalchemy import text

from app.db.session import engine


SQLS = [
    """
    CREATE INDEX IF NOT EXISTS idx_memory_embeddings_vector_cosine
    ON memory_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100)
    """
]


def main():
    with engine.begin() as conn:
        for sql in SQLS:
            conn.execute(text(sql))
    print("Vector indexes created.")


if __name__ == "__main__":
    main()
