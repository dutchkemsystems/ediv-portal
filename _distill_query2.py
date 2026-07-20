import sqlite3
import json
from datetime import datetime, timedelta

DB = r"C:\Users\Lenovo\.local\share\mimocode\mimocode.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

now_ms = int(datetime.now().timestamp() * 1000)
thirty_days_ago_ms = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)

# Find sessions specifically for educationdistrictivportal project
proj_id = "8f1ddea8-1bb6-479f-a192-80fa85ee178a"
print("=== SESSIONS FOR THIS PROJECT ===")
cur.execute("""
    SELECT id, title, directory, time_created
    FROM session
    WHERE time_created > ? AND project_id = ?
    ORDER BY time_created DESC
""", (thirty_days_ago_ms, proj_id))
for r in cur.fetchall():
    ts = datetime.fromtimestamp(r[3]/1000).strftime('%Y-%m-%d %H:%M')
    print(f"  {r[0]} | {r[1]} | dir={r[2]} | {ts}")

# Get all non-checkpoint-writer user messages for this project's sessions
print("\n=== USER MESSAGES IN THIS PROJECT (last 30 days, sample) ===")
cur.execute("""
    SELECT m.id, m.session_id, json_extract(m.data, '$.content'), m.time_created
    FROM message m
    JOIN session s ON s.id = m.session_id
    WHERE json_extract(m.data, '$.role') = 'user'
      AND m.time_created > ?
      AND s.project_id = ?
    ORDER BY m.time_created DESC
    LIMIT 50
""", (thirty_days_ago_ms, proj_id))
for r in cur.fetchall():
    content = r[2][:200] if r[2] else 'N/A'
    print(f"  [{r[1]}] {content}")

# Get assistant tool calls for this project only
print("\n=== TOOL CALLS IN THIS PROJECT (last 30 days, sample) ===")
cur.execute("""
    SELECT json_extract(p.data, '$.tool') as tool,
           substr(json_extract(p.data, '$.state.input'), 1, 200) as inp,
           count(*) as n
    FROM message m
    JOIN part p ON p.message_id = m.id
    JOIN session s ON s.id = m.session_id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND m.time_created > ?
      AND s.project_id = ?
    GROUP BY tool, inp
    ORDER BY n DESC
    LIMIT 40
""", (thirty_days_ago_ms, proj_id))
for r in cur.fetchall():
    print(f"  [{r[2]}x] {r[0]}: {r[1][:180]}")

# Check what files were repeatedly written/edited in this project
print("\n=== REPEATED WRITES/EDITS IN THIS PROJECT ===")
cur.execute("""
    SELECT json_extract(p.data, '$.tool') as tool,
           json_extract(p.data, '$.state.input') as inp,
           count(*) as n
    FROM message m
    JOIN part p ON p.message_id = m.id
    JOIN session s ON s.id = m.session_id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') IN ('write', 'edit')
      AND m.time_created > ?
      AND s.project_id = ?
    GROUP BY tool, json_extract(p.data, '$.state.input')
    HAVING n >= 2
    ORDER BY n DESC
    LIMIT 30
""", (thirty_days_ago_ms, proj_id))
for r in cur.fetchall():
    inp = r[1][:250] if r[1] else 'N/A'
    print(f"  [{r[2]}x] {r[0]}: {inp}")

# Look for bash command patterns (deployment, testing, etc.)
print("\n=== REPEATED BASH COMMANDS IN THIS PROJECT ===")
cur.execute("""
    SELECT substr(json_extract(p.data, '$.state.input'), 1, 200) as cmd,
           count(*) as n
    FROM message m
    JOIN part p ON p.message_id = m.id
    JOIN session s ON s.id = m.session_id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') = 'bash'
      AND m.time_created > ?
      AND s.project_id = ?
    GROUP BY cmd
    ORDER BY n DESC
    LIMIT 30
""", (thirty_days_ago_ms, proj_id))
for r in cur.fetchall():
    print(f"  [{r[1]}x] {r[0]}")

conn.close()
