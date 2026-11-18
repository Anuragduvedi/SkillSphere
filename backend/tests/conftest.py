import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import text
from app.database import engine, Base
import app.models.models

# Ensure all tables are created in the database before running tests
Base.metadata.create_all(bind=engine)

# Ensure columns in assessments table exist
try:
    with engine.connect() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(assessments)")).fetchall()]
        if 'template_id' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN template_id INTEGER REFERENCES assessment_templates(template_id)"))
        if 'passing_percentage' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN passing_percentage FLOAT DEFAULT 60.0"))
        if 'violation_count' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN violation_count INTEGER DEFAULT 0"))
        if 'auto_submitted_proctoring' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN auto_submitted_proctoring BOOLEAN DEFAULT 0"))
        if 'proctoring_submission_reason' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN proctoring_submission_reason TEXT"))
        if 'description' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN description TEXT"))
        if 'expires_at' not in cols:
            conn.execute(text("ALTER TABLE assessments ADD COLUMN expires_at DATETIME"))

        # Check assessment_templates columns
        t_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(assessment_templates)")).fetchall()]
        if 'description' not in t_cols:
            conn.execute(text("ALTER TABLE assessment_templates ADD COLUMN description TEXT"))
        conn.commit()
except Exception:
    pass
