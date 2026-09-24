import sqlite3
import json
import sys
from datetime import datetime, timedelta

DB = r"C:\Users\Lenovo\.local\share\mimocode\mimocode.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

now_ms = int(datetime.now().timestamp() * 1000)
thirty_days_ago_ms = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)

# Recent sessions for this project
print("=== RECENT SESSIONS (last 30 days) ===")
cur.execute("""
    SELECT id, title, directory, time_created, project_id
    FROM session
    WHERE time_created > ?
    ORDER BY time_created DESC
""", (thirty_days_ago_ms,))
sessions = cur.fetchall()
project_sessions = []
for r in sessions:
    print(f"  {r[0]} | {r[1]} | dir={r[2]} | ts={r[3]} | proj={r[4]}")
    project_sessions.append(r[0])

print(f"\nTotal recent sessions: {len(sessions)}")

# Top tool usage patterns
print("\n=== TOP TOOL USAGE (last 30 days) ===")
cur.execute("""
    SELECT json_extract(p.data, '$.tool') as tool,
           substr(json_extract(p.data, '$.state.input'), 1, 200) as input_preview,
           count(*) as n
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND m.time_created > ?
    GROUP BY tool, input_preview
    ORDER BY n DESC
    LIMIT 50
""", (thirty_days_ago_ms,))
for r in cur.fetchall():
    print(f"  [{r[2]}x] {r[0]}: {r[1][:180]}")

# Tool frequency overall
print("\n=== TOOL FREQUENCY OVERALL (last 30 days) ===")
cur.execute("""
    SELECT json_extract(p.data, '$.tool') as tool,
           count(*) as n
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND m.time_created > ?
    GROUP BY tool
    ORDER BY n DESC
""", (thirty_days_ago_ms,))
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

# Search for repeated patterns in user messages
print("\n=== USER TURN KEYWORDS ===")
for kw in ['again', 'every time', 'like last time', 'usual', 'repeat', 'same as before', 'same pattern', 'also', 'next', 'now', 'continue']:
    cur.execute("""
        SELECT count(*) as n
        FROM message m
        WHERE json_extract(m.data, '$.role') = 'user'
          AND m.time_created > ?
          AND json_extract(m.data, '$.content') LIKE ?
    """, (thirty_days_ago_ms, '%' + kw + '%'))
    r = cur.fetchone()
    if r and r[0] > 0:
        print(f"  '{kw}': {r[0]} occurrences")

# Repeated write/edit operations on same files
print("\n=== REPEATED WRITE/EDIT ON SAME FILE (last 30 days) ===")
cur.execute("""
    SELECT json_extract(p.data, '$.tool') as tool,
           substr(json_extract(p.data, '$.state.input'), 1, 300) as inp,
           count(*) as n
    FROM message m
    JOIN part p ON p.message_id = m.id
    WHERE json_extract(m.data, '$.role') = 'assistant'
      AND json_extract(p.data, '$.type') = 'tool'
      AND json_extract(p.data, '$.tool') IN ('write', 'edit')
      AND m.time_created > ?
    GROUP BY tool, substr(json_extract(p.data, '$.state.input'), 1, 150)
    HAVING n >= 2
    ORDER BY n DESC
    LIMIT 30
""", (thirty_days_ago_ms,))
for r in cur.fetchall():
    inp = r[1][:250] if r[1] else 'N/A'
    print(f"  [{r[2]}x] {r[0]}: {inp}")

conn.close()
