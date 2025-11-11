import os

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class PostgresClient:
    def __init__(self):
        self.host = os.getenv("PG_HOST", "localhost")
        self.port = os.getenv("PG_PORT", "5432")
        self.db = os.getenv("PG_DB", "realdb")
        self.user = os.getenv("PG_USER", "postgres")
        self.password = os.getenv("PG_PASSWORD", "postgres")

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.db,
            user=self.user,
            password=self.password,
            cursor_factory=RealDictCursor
        )

    def init_schema(self):
        ddl = """
                CREATE TABLE IF NOT EXISTS offers (
                    id SERIAL PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    titlu TEXT,
                    sursa TEXT,
                    pret NUMERIC,
                    judet TEXT,
                    oras TEXT,
                    zona TEXT,
                    lat FLOAT,
                    lng FLOAT,
                    tip_proprietate TEXT,
                    tip_tranzactie TEXT,
                    tip_vanzator TEXT,
                    descriere TEXT,
                    data_postarii TIMESTAMP DEFAULT NOW(),
                    suprafata TEXT,
                    numar_camere TEXT,
                    etaj TEXT,
                    compartimentare TEXT,
                    an_constructie TEXT,
                    imagini TEXT[],
                    active BOOLEAN DEFAULT TRUE
                );
                
                CREATE TABLE IF NOT EXISTS locations (
                    id SERIAL PRIMARY KEY,
                    judet TEXT,
                    zona TEXT,
                    lat FLOAT,
                    lng FLOAT
                );
                """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(ddl)
                conn.commit()
