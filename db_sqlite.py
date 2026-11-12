"""Local SQLite persistence for demonstration ONLY; not production clinical storage."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH=Path(__file__).parent/'data'/'registry_demo.sqlite3'

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    c=sqlite3.connect(DB_PATH)
    c.row_factory=sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c

def init():
    with conn() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS patients (
          patient_id TEXT PRIMARY KEY, center TEXT NOT NULL DEFAULT '',
          diagnosis TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS section_entries (
          entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
          patient_id TEXT NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
          section TEXT NOT NULL, episode INTEGER NOT NULL DEFAULT 1,
          data_json TEXT NOT NULL DEFAULT '{}', updated_at TEXT NOT NULL,
          UNIQUE(patient_id,section,episode)
        );
        CREATE TABLE IF NOT EXISTS audit_events (
          audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
          patient_id TEXT NOT NULL, section TEXT NOT NULL,
          episode INTEGER, action TEXT NOT NULL, old_json TEXT,
          new_json TEXT, recorded_at TEXT NOT NULL
        );
        ''')

def list_patients(search=''):
    with conn() as c:
        pat=f'%{search.strip()}%'
        return [dict(r) for r in c.execute('''SELECT * FROM patients
         WHERE patient_id LIKE ? OR center LIKE ? OR diagnosis LIKE ?
         ORDER BY updated_at DESC''',(pat,pat,pat))]

def get_patient(pid):
    with conn() as c:
        r=c.execute('SELECT * FROM patients WHERE patient_id=?',(pid,)).fetchone()
        return dict(r) if r else None

def create_patient(pid,center='',diagnosis=''):
    pid=pid.strip()
    if not pid or len(pid)>60: raise ValueError('Patient research ID must be 1–60 characters.')
    if not all(ch.isalnum() or ch in '-_.' for ch in pid):
        raise ValueError('Only letters, digits, hyphens, underscores and dots are allowed in the research ID.')
    with conn() as c:
        c.execute('INSERT INTO patients VALUES (?,?,?,?,?)',(pid,center,diagnosis,now(),now()))
        c.execute('INSERT INTO audit_events(patient_id,section,episode,action,new_json,recorded_at) VALUES (?,?,?,?,?,?)',
                  (pid,'Patient registry',None,'Created',json.dumps({'center':center,'diagnosis':diagnosis}),now()))

def update_patient(pid,center=None,diagnosis=None):
    p=get_patient(pid)
    if not p: raise ValueError('Patient not found')
    new={'center':p['center'] if center is None else center,
         'diagnosis':p['diagnosis'] if diagnosis is None else diagnosis}
    with conn() as c:
        c.execute('UPDATE patients SET center=?,diagnosis=?,updated_at=? WHERE patient_id=?',(new['center'],new['diagnosis'],now(),pid))
        if new!={'center':p['center'],'diagnosis':p['diagnosis']}:
            c.execute('INSERT INTO audit_events(patient_id,section,action,old_json,new_json,recorded_at) VALUES (?,?,?,?,?,?)',
                      (pid,'Patient registry','Updated',json.dumps({'center':p['center'],'diagnosis':p['diagnosis']}),json.dumps(new),now()))

def entries(pid,section=None):
    with conn() as c:
        if section:
            rows=c.execute('SELECT * FROM section_entries WHERE patient_id=? AND section=? ORDER BY episode',(pid,section))
        else:
            rows=c.execute('SELECT * FROM section_entries WHERE patient_id=? ORDER BY section,episode',(pid,))
        return [{**dict(r),'data':json.loads(r['data_json'])} for r in rows]

def get_entry(pid,section,episode=1):
    with conn() as c:
        r=c.execute('SELECT data_json FROM section_entries WHERE patient_id=? AND section=? AND episode=?',(pid,section,episode)).fetchone()
        return json.loads(r['data_json']) if r else {}

def next_episode(pid,section):
    with conn() as c:
        r=c.execute('SELECT MAX(episode) FROM section_entries WHERE patient_id=? AND section=?',(pid,section)).fetchone()
        return (r[0] or 0)+1

def save_entry(pid,section,episode,data):
    if get_patient(pid) is None: raise ValueError('Patient not found')
    clean={k:v for k,v in data.items() if v is not None and str(v).strip()}
    old=get_entry(pid,section,episode)
    if clean==old:return False
    stamp=now()
    with conn() as c:
        c.execute('''INSERT INTO section_entries(patient_id,section,episode,data_json,updated_at) VALUES (?,?,?,?,?)
        ON CONFLICT(patient_id,section,episode) DO UPDATE SET data_json=excluded.data_json,updated_at=excluded.updated_at''',
                  (pid,section,episode,json.dumps(clean,ensure_ascii=False),stamp))
        c.execute('UPDATE patients SET updated_at=? WHERE patient_id=?',(stamp,pid))
        c.execute('INSERT INTO audit_events(patient_id,section,episode,action,old_json,new_json,recorded_at) VALUES (?,?,?,?,?,?,?)',
                  (pid,section,episode,'Updated' if old else 'Saved',json.dumps(old,ensure_ascii=False),json.dumps(clean,ensure_ascii=False),stamp))
    return True

def audit(pid):
    with conn() as c:
        return [dict(r) for r in c.execute('SELECT * FROM audit_events WHERE patient_id=? ORDER BY audit_id DESC',(pid,))]

def stats():
    with conn() as c:
        n=c.execute('SELECT COUNT(*) FROM patients').fetchone()[0]
        e=c.execute('SELECT COUNT(*) FROM section_entries').fetchone()[0]
        return n,e

def seed_demo():
    if stats()[0]:return
    for pid,center,diag in [('DEMO-001','Demo center A','MDS'),('DEMO-002','Demo center A','AML'),('DEMO-003','Demo center B','MDS')]:
        create_patient(pid,center,diag)
    save_entry('DEMO-001','Patient details',1,{'c2':'Demo center A','c3':'1','c11':'0'})
    save_entry('DEMO-001','Diagnosis & TP53',1,{'c2':'1','c4':'8','c19':'p.Arg273His','c25':'26.5'})
    save_entry('DEMO-001','Treatment episode',1,{'title':'First-line HMA-based therapy','date':'2026-01-10','response':'CR','notes':'Fictional example'})
    save_entry('DEMO-001','Molecular follow-up',1,{'c2':'Post-treatment','c4':'2026-04-20','c10':'12.1'})
    save_entry('DEMO-001','Molecular follow-up',2,{'c2':'Follow-up visit','c4':'2026-07-20','c10':'7.4'})
    save_entry('DEMO-002','Diagnosis & TP53',1,{'c2':'2','c4':'23','c25':'41.2'})
