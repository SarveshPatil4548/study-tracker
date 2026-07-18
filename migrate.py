"""Migration: add topics table + topic_id and attachment_filename to study_sessions."""
from app import create_app
from models import db
from sqlalchemy import text, inspect as sa_inspect


def run_migration():
    app = create_app()
    with app.app_context():
        inspector = sa_inspect(db.engine)
        existing_tables = inspector.get_table_names()

        # 1. Create topics table if missing
        if "topics" not in existing_tables:
            db.session.execute(text("""
                CREATE TABLE topics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id)
                )
            """))
            db.session.commit()
            print("Created table: topics")
        else:
            print("Table 'topics' already exists — skipping")

        # 2. Add columns to study_sessions if missing
        existing_cols = {c["name"] for c in inspector.get_columns("study_sessions")}

        if "topic_id" not in existing_cols:
            db.session.execute(text("""
                ALTER TABLE study_sessions
                ADD COLUMN topic_id INT NULL,
                ADD CONSTRAINT fk_topic
                    FOREIGN KEY (topic_id) REFERENCES topics(id)
            """))
            db.session.commit()
            print("Added column: topic_id")
        else:
            print("Column 'topic_id' already exists — skipping")

        if "attachment_filename" not in existing_cols:
            db.session.execute(text("""
                ALTER TABLE study_sessions
                ADD COLUMN attachment_filename VARCHAR(255) NULL
            """))
            db.session.commit()
            print("Added column: attachment_filename")
        else:
            print("Column 'attachment_filename' already exists — skipping")

        print("\nMigration complete.")


if __name__ == "__main__":
    run_migration()
