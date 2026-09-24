import sqlite3
import json
from datetime import datetime, timedelta

DB = r"C:\Users\Lenovo\.local\share\mimocode\mimocode.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Find all file writes in ses_08d0e237effe6j7Yg417A0R15O (the big session that built 22 pages)
print("=== FILES WRITTEN IN SES_08d0e237effe6j7Yg417A0R15O ===")
cur.execute("""
    SELECT json_extract(p.data, '$.tool') as tool,
           json_extract(p.data, '$.state.input') as inp
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') IN ('write', 'edit')
      AND m.session_id = 'ses_08d0e237effe6j7Yg417A0R15O'
    ORDER BY m.time_created
""")
writes = []
for r in cur.fetchall():
    try:
        inp = json.loads(r[1]) if r[1] else {}
        fp = inp.get('file_path', inp.get('filePath', 'N/A'))
        writes.append((r[0], fp))
    except:
        writes.append((r[0], r[1][:100] if r[1] else 'N/A'))

for tool, fp in writes:
    print(f"  {tool}: {fp}")

# Also check ses_08dadb90affeZOVITEpouqT813 (the implementation session)
print("\n=== FILES WRITTEN IN SES_08dadb90affeZOVITEpouqT813 ===")
cur.execute("""
    SELECT json_extract(p.data, '$.tool') as tool,
           json_extract(p.data, '$.state.input') as inp
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') IN ('write', 'edit')
      AND m.session_id = 'ses_08dadb90affeZOVITEpouqT813'
    ORDER BY m.time_created
""")
for r in cur.fetchall():
    try:
        inp = json.loads(r[1]) if r[1] else {}
        fp = inp.get('file_path', inp.get('filePath', 'N/A'))
        print(f"  {r[0]}: {fp}")
    except:
        print(f"  {r[0]}: {r[1][:100] if r[1] else 'N/A'}")

# Look at bash commands in the big session
print("\n=== BASH COMMANDS IN SES_08d0e237effe6j7Yg417A0R15O ===")
cur.execute("""
    SELECT substr(json_extract(p.data, '$.state.input'), 1, 300) as cmd
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') = 'bash'
      AND m.session_id = 'ses_08d0e237effe6j7Yg417A0R15O'
    ORDER BY m.time_created
""")
for r in cur.fetchall():
    print(f"  {r[0]}")

conn.close()
