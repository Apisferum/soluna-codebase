from contextlib import closing
import sqlite3

from app.core.config import settings


def connect_db() -> sqlite3.Connection:
    settings.data_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        str(settings.database_path)
    )

    connection.row_factory = sqlite3.Row
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def column_exists(
    cursor: sqlite3.Cursor,
    table_name: str,
    column_name: str,
) -> bool:
    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    columns = cursor.fetchall()

    return any(
        column["name"] == column_name
        for column in columns
    )


def initialize_auth_tables() -> None:
    with closing(connect_db()) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                age TEXT NOT NULL,
                gender TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
            """
        )

        if not column_exists(
            cursor,
            "users",
            "token_version",
        ):
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN token_version
                INTEGER NOT NULL DEFAULT 0
                """
            )

        if not column_exists(
            cursor,
            "users",
            "role",
        ):
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN role
                TEXT NOT NULL DEFAULT 'user'
                """
            )

        cursor.execute(
            """
            UPDATE users
            SET role = 'user'
            WHERE role IS NULL
               OR TRIM(role) = ''
               OR LOWER(role)
                  NOT IN ('user', 'admin')
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            password_reset_codes (
                id INTEGER PRIMARY KEY
                    AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                attempts INTEGER NOT NULL
                    DEFAULT 0,
                used INTEGER NOT NULL
                    DEFAULT 0,
                created_at INTEGER NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_password_reset_email_created
            ON password_reset_codes (
                email,
                created_at DESC
            )
            """
        )

        connection.commit()
      
def initialize_generation_tables() -> None:
    settings.data_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    with closing(connect_db()) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                prompt TEXT NOT NULL,
                mood TEXT,
                genre TEXT,
                tempo TEXT,
                music_key TEXT,
                instrument TEXT,
                structure TEXT,
                status TEXT DEFAULT 'pending',
                message TEXT,
                midi_notes TEXT,
                midi_file_path TEXT,
                created_at INTEGER NOT NULL
            )
            """
        )

        generation_columns = {
            "music_key": "TEXT",
            "status": "TEXT DEFAULT 'pending'",
            "message": "TEXT",
            "midi_notes": "TEXT",
            "midi_file_path": "TEXT",
        }

        for column_name, column_definition in generation_columns.items():
            if not column_exists(
                cursor,
                "generations",
                column_name,
            ):
                cursor.execute(
                    f"""
                    ALTER TABLE generations
                    ADD COLUMN {column_name}
                    {column_definition}
                    """
                )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_generations_user_created
            ON generations (
                user_email,
                created_at DESC
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generation_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generation_id INTEGER NOT NULL UNIQUE,
                original_prompt TEXT NOT NULL,
                intent_json TEXT,
                structure_plan_json TEXT,
                routing_json TEXT,
                critic_trace_json TEXT,
                midi_file_path TEXT,
                audio_file_path TEXT,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                FOREIGN KEY(generation_id)
                    REFERENCES generations(id)
                    ON DELETE CASCADE
            )
            """
        )

        connection.commit()     