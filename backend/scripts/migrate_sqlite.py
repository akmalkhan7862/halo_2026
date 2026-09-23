import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resume_platform.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='analysis_results'")
ddl = cur.fetchone()[0]
print("Old DDL:\n", ddl)

# Recreate with nullable job_description_id
cur.execute("PRAGMA foreign_keys=OFF")
cur.execute("""
CREATE TABLE IF NOT EXISTS analysis_results_new (
    id CHAR(36) NOT NULL PRIMARY KEY,
    resume_id CHAR(36) NOT NULL,
    job_description_id CHAR(36),
    role_key VARCHAR(100),
    target_role VARCHAR(255),
    matched_skills JSON NOT NULL,
    missing_skills JSON NOT NULL,
    weak_skills JSON NOT NULL,
    related_partial_skills JSON NOT NULL,
    extra_skills JSON NOT NULL,
    gap_summary JSON NOT NULL,
    scores JSON NOT NULL,
    explanations JSON NOT NULL,
    provenance JSON,
    created_at DATETIME NOT NULL,
    FOREIGN KEY(resume_id) REFERENCES resumes (id) ON DELETE CASCADE,
    FOREIGN KEY(job_description_id) REFERENCES job_descriptions (id) ON DELETE CASCADE
)
""")

cur.execute("""
INSERT INTO analysis_results_new (
    id, resume_id, job_description_id, role_key, target_role,
    matched_skills, missing_skills, weak_skills, related_partial_skills,
    extra_skills, gap_summary, scores, explanations, provenance, created_at
)
SELECT 
    id, resume_id, job_description_id, role_key, target_role,
    matched_skills, missing_skills, weak_skills, related_partial_skills,
    extra_skills, gap_summary, scores, explanations, provenance, created_at
FROM analysis_results
""")

cur.execute("DROP TABLE analysis_results")
cur.execute("ALTER TABLE analysis_results_new RENAME TO analysis_results")
cur.execute("PRAGMA foreign_keys=ON")
conn.commit()
conn.close()
print("Migration completed successfully.")
