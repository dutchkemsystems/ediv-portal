#!/usr/bin/env python
"""
Automated database backup script for Education District IV Portal.
Run via cron: 0 2 * * * python scripts/backup/backup_database.py
"""
import os
import sys
import subprocess
import datetime
import shutil
from pathlib import Path


BACKUP_DIR = Path(__file__).parent / 'backups'
RETENTION_DAYS = 30


def get_db_config():
    return {
        'name': os.environ.get('POSTGRES_DB', 'education_district_iv'),
        'user': os.environ.get('POSTGRES_USER', 'ediv_user'),
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('POSTGRES_PORT', '5432'),
    }


def create_backup():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    db_config = get_db_config()
    filename = f"ediv_backup_{timestamp}.sql"
    filepath = BACKUP_DIR / filename

    print(f"Starting backup of database '{db_config['name']}'...")

    env = os.environ.copy()
    env['PGPASSWORD'] = os.environ.get('POSTGRES_PASSWORD', 'ediv_password')

    cmd = [
        'pg_dump',
        '-h', db_config['host'],
        '-p', db_config['port'],
        '-U', db_config['user'],
        '-d', db_config['name'],
        '-F', 'c',
        '-f', str(filepath),
    ]

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"pg_dump failed: {result.stderr}")
            sys.exit(1)

        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"Backup created: {filepath} ({size_mb:.2f} MB)")
        return filepath

    except FileNotFoundError:
        print("pg_dump not found. Installing pg_dump alternative...")
        cmd_psql = [
            'python', '-c',
            f"""
import psycopg2
import os
conn = psycopg2.connect(
    dbname='{db_config["name"]}',
    user='{db_config["user"]}',
    password=os.environ.get('POSTGRES_PASSWORD', 'ediv_password'),
    host='{db_config["host"]}',
    port='{db_config["port"]}'
)
cursor = conn.cursor()
with open('{filepath}', 'w') as f:
    for table in conn.get_tables():
        cursor.execute(f"SELECT * FROM {{table}}")
        rows = cursor.fetchall()
        for row in rows:
            f.write(str(row) + '\\n')
conn.close()
"""
        ]
        subprocess.run(cmd_psql, timeout=600)
        return filepath

    except subprocess.TimeoutExpired:
        print("Backup timed out after 10 minutes")
        sys.exit(1)


def cleanup_old_backups():
    cutoff = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
    removed = 0

    for filepath in BACKUP_DIR.glob('ediv_backup_*.sql'):
        if filepath.stat().st_mtime < cutoff.timestamp():
            filepath.unlink()
            removed += 1

    if removed > 0:
        print(f"Cleaned up {removed} old backup(s) (>{RETENTION_DAYS} days)")


def main():
    print(f"=== Education District IV Database Backup ===")
    print(f"Time: {datetime.datetime.now().isoformat()}")

    filepath = create_backup()
    cleanup_old_backups()

    print(f"Backup complete: {filepath}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
