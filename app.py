"""TP53 Clinical Registry — synthetic-data demonstration. Not for patient care."""
import html
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title='TP53 Clinical Registry', page_icon='🧬', layout='wide', initial_sidebar_state='expanded')

STYLE = '''<style>
:root {--navy:#152842;--blue:#24618c;--soft:#eef4f9}
.block-container {max-width:1340px;padding-top:1.6rem;padding-bottom:3rem}
.stApp {background:#f8fafc}
section[data-testid="stSidebar"] {background:#f0f4f8;border-right:1px solid #dce6ef}
section[data-testid="stSidebar"] * {color:#1c3650}
section[data-testid="stSidebar"] [data-testid="stAlert"] * {color:#633e00}
h1,h2,h3 {color:#152842;letter-spacing:-.02em}
div[data-testid="stMetric"] {background:#fff;border:1px solid #e1e8ef;border-radius:13px;padding:14px 17px}
.stButton>button[kind="primary"],div[data-testid="stFormSubmitButton"] button[kind="primary"] {background:#1e567e;border-color:#1e567e}
.tp-header {background:#fff;border:1px solid #e1e8ef;padding:20px 24px;border-radius:15px;margin:5px 0 21px}
.tp-header h2 {font-size:27px;margin:0;color:#152842}.tp-header p{color:#687e91;margin:7px 0 0}
.tp-tag{color:#28714d;background:#e4f4e9;border-radius:18px;padding:4px 10px;font-size:12px;font-weight:600}
.tp-entry{background:white;border:1px solid #e0e8f0;border-radius:11px;padding:15px 18px;margin:11px 0}
.tp-small{font-size:13px;color:#60788d}
.tp-logo{font-size:24px;font-weight:800;color:#173956;margin-top:2px}
</style>'''
st.markdown(STYLE, unsafe_allow_html=True)

try:
    import db
    db.init()
except Exception as exc:
    st.error('Unable to start the database. Check your Streamlit requirements and DATABASE_URL in App settings → Secrets.')
    st.code(f'{type(exc).__name__}: {exc}',language='text')
    st.info('For Supabase use the Session pooler URI and ensure requirements.txt includes psycopg[binary]. Never share database passwords in screenshots or messages.')
    st.stop()

SECTIONS=json.loads((Path(__file__).parent/'field_schema.json').read_text(encoding='utf8'))['sections']
PAGES={
    'Patient Information':'Patient details',
    'Molecular Diagnosis':'Diagnosis & TP53',
    'Treatment & Outcomes':'Treatment & outcomes',
    'Treatment Episodes':'Treatment episode',
    'Allogeneic SCT':'Allogeneic transplant',
    'Molecular Follow-up':'Molecular follow-up',
}
REPEAT={'Treatment episode','Molecular follow-up'}
ICONS={'Patient Information':'👤','Molecular Diagnosis':'🧬','Treatment & Outcomes':'💊','Treatment Episodes':'📋','Allogeneic SCT':'❤️','Molecular Follow-up':'🔬'}
EPISODE_FIELDS=[
    {'key':'title','label':'Treatment / regimen'},
    {'key':'date','label':'Date of initiation'},
    {'key':'response','label':'Response'},
    {'key':'response_date','label':'Date of response'},
    {'key':'relapse_date','label':'Date of relapse'},
    {'key':'notes','label':'Additional information'},
]

def safe(x):return html.escape(str(x or ''))
def header(title,subtitle):
    st.markdown(f'<div class="tp-header"><h2>{safe(title)}</h2><p>{safe(subtitle)}</p></div>',unsafe_allow_html=True)

def navigate(page,pid=None):
    st.session_state.page=page
    if pid is not None:st.session_state.patient_id=pid
    st.rerun()

def fix_date(value):
    if value and not re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(value)):
        raise ValueError('Dates must use YYYY-MM-DD format.')
    if value:datetime.strptime(str(value),'%Y-%m-%d')

def input_field(field, old, prefix):
    raw=field['label']; label=' '.join(raw.split()); key=prefix+'_'+field['key']
    value=str(old or '')
    lower=label.lower()
    if 'sex ' in lower and 'f=1' in lower:
        opts={'':'Not recorded','1':'Female','2':'Male'}
    elif lower.startswith('diagnosis ') and 'mds=1' in lower:
        opts={'':'Not recorded','1':'MDS','2':'AML'}
    elif '(yes=1, no=0)' in lower or '(no=0, yes=1' in lower or '(available=1, n/a=0)' in lower:
        opts={'':'Not recorded','0':'0 — No / negative / unavailable','1':'1 — Yes / positive / available'}
        if 'n/a=9' in lower:opts['9']='9 — Not available'
    elif 'donor matching' in lower:
        opts={'':'Not recorded','0':'Haploidentical','1':'10/10','2':'9/10','3':'8/10'}
    else:opts=None
    if opts is not None:
        if value not in opts:opts[value]=value
        return st.selectbox(label,list(opts),index=list(opts).index(value),format_func=lambda v:opts[v],key=key)
    if any(s in lower for s in ['additional information','comorbidities','immunophenotype','specific mutation','annotation','conditioning','karyotype at','cause of death','specific drugs']):
        return st.text_area(label,value=value,height=95,key=key)
    placeholder='YYYY-MM-DD' if ('date ' in lower or lower.startswith('date')) else None
    return st.text_input(label,value=value,placeholder=placeholder,key=key)

def render_section(pid,section):
    st.caption('Blank fields are permitted. Original workbook field names are retained for traceability.')
    if section in REPEAT:
        existing=db.entries(pid,section)
        nums=[e['episode'] for e in existing]
        selected=st.selectbox('Assessment / episode',nums+['+ New entry'],format_func=lambda x:f'Entry {x}' if isinstance(x,int) else x,key='episode_'+pid+section)
        episode=db.next_episode(pid,section) if selected=='+ New entry' else selected
    else: episode=1
    fields=EPISODE_FIELDS if section=='Treatment episode' else SECTIONS[section]
    old=db.get_entry(pid,section,episode)
    with st.form('form_'+pid+section+str(episode)):
        values={}
        for i in range(0,len(fields),2):
            cols=st.columns(2,gap='large')
            for j,col in enumerate(cols):
                if i+j<len(fields):
                    with col:
                        f=fields[i+j]
                        values[f['key']]=input_field(f,old.get(f['key'],''),pid+section+str(episode))
        submitted=st.form_submit_button('💾 Save section to database',type='primary',use_container_width=True)
    if submitted:
        try:
            for f in fields:
                k=f['key'];label=f['label'].lower()
                if 'date' in label:fix_date(values.get(k))
                if 'vaf (%)' in label.lower() and values.get(k):
                    v=float(values[k])
                    if not 0<=v<=100:raise ValueError('VAF must be between 0 and 100.')
            changed=db.save_entry(pid,section,episode,values)
            if section=='Patient details':db.update_patient(pid,center=values.get('c2',''))
            if section=='Diagnosis & TP53':db.update_patient(pid,diagnosis={'1':'MDS','2':'AML'}.get(values.get('c2',''),''))
            if changed:st.success('Saved successfully. This entry is now in '+db.BACKEND+'.')
            else:st.info('No changes to save.')
        except Exception as exc:st.error(f'Could not save: {exc}')

def timeline(pid):
    timeline_rows=[];trends=[]
    for row in db.entries(pid):
        section=row['section'];d=row['data'];num=row['episode']
        if section=='Patient details':date=d.get('c8','');title='Initial patient record'
        elif section=='Diagnosis & TP53':date=d.get('c3','');title='Molecular diagnosis'
        elif section=='Treatment episode':date=d.get('date','');title=d.get('title') or 'Treatment episode'
        elif section=='Molecular follow-up':
            date=d.get('c4','');title=d.get('c2') or 'Molecular reassessment'
            try:
                v=float(d.get('c10',''))
                if date and 0<=v<=100:trends.append({'Date':pd.to_datetime(date),'VAF (%)':v})
            except (ValueError,TypeError):pass
        elif section=='Allogeneic transplant':date=d.get('c4','');title='Allogeneic transplant'
        else:date='';title=section
        timeline_rows.append((date if re.fullmatch(r'\d{4}-\d{2}-\d{2}',date or '') else '9999-12-31',date,title,section,num))
    st.subheader('Clinical timeline')
    if not timeline_rows:st.info('Save a clinical section to create the first timeline event.')
    for _,date,title,section,num in sorted(timeline_rows):
        st.markdown(f'<div class="tp-entry"><strong>{safe(title)}</strong><div class="tp-small">{safe(date or "Date not recorded")} · {safe(section)} · Entry {num}</div></div>',unsafe_allow_html=True)
    st.subheader('TP53 VAF over time')
    if trends:
        st.line_chart(pd.DataFrame(trends).sort_values('Date').set_index('Date'))
    else:st.caption('Add dated molecular assessments with VAF measurements to display the chart.')

def patient_page(pid):
    p=db.get_patient(pid)
    if not p:st.warning('Patient record not found.');return
    header('Patient '+pid,'Clinical record · '+(p['diagnosis'] or 'Diagnosis not recorded')+' · '+(p['center'] or 'Center not recorded'))
    c1,c2,c3=st.columns(3)
    c1.metric('Diagnosis',p['diagnosis'] or 'Not recorded')
    c2.metric('Center',p['center'] or 'Not recorded')
    c3.metric('Saved sections',len(db.entries(pid)))
    selection=st.session_state.get('patient_section','Patient Overview')
    if selection=='Patient Overview':timeline(pid)
    elif selection=='Modification History':
        st.subheader('Record modification history')
        for evt in db.audit(pid):
            with st.expander(f'{evt["recorded_at"]} · {evt["section"]} · {evt["action"]}'):
                st.caption('Prototype change log; no individual-user attribution yet.')
                st.json({'Before':json.loads(evt['old_json']) if evt['old_json'] else None,
                         'After':json.loads(evt['new_json']) if evt['new_json'] else None})
    else:
        section=PAGES.get(selection)
        if section:
            st.subheader(selection)
            if section in REPEAT:st.info('You can save any number of separate assessments or treatment episodes.')
            render_section(pid,section)

# Only insert fictional seed patients on a fresh, empty database.
if not st.session_state.get('bootstrapped'):
    try:db.seed_demo()
    except Exception as exc:st.warning(f'Demo data not initialized: {exc}')
    st.session_state.bootstrapped=True
if 'page' not in st.session_state:st.session_state.page='Dashboard'
if 'patient_id' not in st.session_state:st.session_state.patient_id=None
if 'patient_section' not in st.session_state:st.session_state.patient_section='Patient Overview'

st.sidebar.markdown('<div class="tp-logo">✚ TP53 Clinical Registry</div>',unsafe_allow_html=True)
st.sidebar.caption('Research data management · Prototype')
st.sidebar.info('🧪 TEST MODE — Synthetic data only. No clinical use.')
st.sidebar.markdown('##### WORKSPACE')
for label,icon in [('Dashboard','▦'),('Patient Registry','♧'),('New Patient','⊕'),('Export Data','⇩')]:
    if st.sidebar.button(icon+'  '+label,key='work_'+label,use_container_width=True):navigate(label)
patient_id=st.session_state.patient_id
if patient_id and db.get_patient(patient_id):
    st.sidebar.divider()
    st.sidebar.markdown('##### PATIENT RECORD')
    st.sidebar.caption('Selected: '+patient_id)
    labels=['Patient Overview']+list(PAGES)+['Modification History']
    st.sidebar.radio('Clinical sections',labels,key='patient_section',label_visibility='collapsed')
    if st.sidebar.button('Open selected patient',use_container_width=True):navigate('Patient Workspace')
st.sidebar.divider()
st.sidebar.caption('Storage: '+db.BACKEND)
st.sidebar.caption('Not authenticated · Do not use real patient data')

page=st.session_state.page
if page=='Dashboard':
    header('Research dashboard','Explore your TP53 study cohort and recently saved records')
    n,e=db.stats();a,b,c=st.columns(3)
    a.metric('Registered patients',n);b.metric('Clinical entries',e);c.metric('Database','Connected')
    st.info('This is a synthetic-data prototype without user authentication. Do not enter real clinical information.')
    st.subheader('Recent patients')
    for p in db.list_patients()[:10]:
        with st.container(border=True):
            c1,c2=st.columns([5,1])
            c1.markdown('**'+safe(p['patient_id'])+'**  · '+safe(p['diagnosis'] or 'Not classified')+'  · '+safe(p['center']))
            if c2.button('Open →',key='recent_'+p['patient_id'],use_container_width=True):navigate('Patient Workspace',p['patient_id'])
    if st.button('Search all patients →',type='primary'):navigate('Patient Registry')
elif page=='Patient Registry':
    header('Patient registry','Find a patient and open their complete clinical history')
    q=st.text_input('Search patients',placeholder='Search by research ID, hospital or diagnosis')
    rows=db.list_patients(q)
    st.caption(f'{len(rows)} patient(s) found')
    for p in rows:
        with st.container(border=True):
            c1,c2=st.columns([5,1])
            c1.markdown('**'+safe(p['patient_id'])+'**')
            c1.caption((p['diagnosis'] or 'Unclassified')+' · '+(p['center'] or 'No center')+' · Updated '+p['updated_at'][:10])
            if c2.button('View history →',key='patient_'+p['patient_id'],use_container_width=True):navigate('Patient Workspace',p['patient_id'])
    if not rows:st.info('No matching patient records.')
elif page=='New Patient':
    header('Register a new patient','Only fictional, pseudonymized research codes during testing')
    with st.form('create'):
        pid=st.text_input('Unique research ID *',placeholder='DEMO-004')
        center=st.text_input('Hospital / Center',placeholder='Demo center')
        diagnosis=st.selectbox('Diagnosis',['','MDS','AML'])
        submitted=st.form_submit_button('Create patient record',type='primary')
    if submitted:
        try:
            db.create_patient(pid,center,diagnosis)
            navigate('Patient Workspace',pid.strip())
        except Exception as exc:st.error(f'Could not create patient: {exc}')
elif page=='Patient Workspace':
    if not patient_id:st.info('Select a patient from Patient Registry.')
    else:patient_page(patient_id)
elif page=='Export Data':
    header('Export research data','Download the saved synthetic cohort for statistical analysis')
    export=[]
    for p in db.list_patients():
        es=db.entries(p['patient_id'])
        if not es:export.append({'patient_id':p['patient_id'],'center':p['center'],'diagnosis':p['diagnosis']})
        for e in es:export.append({'patient_id':p['patient_id'],'center':p['center'],'diagnosis':p['diagnosis'],
                                 'section':e['section'],'episode':e['episode'],**e['data']})
    if export:
        frame=pd.DataFrame(export)
        st.download_button('Download CSV',frame.to_csv(index=False).encode('utf-8-sig'),file_name='tp53_demo_export.csv',mime='text/csv',type='primary')
        st.dataframe(frame,hide_index=True,use_container_width=True)
        st.caption('Field codes c2/c3/etc. correspond to original workbook columns; definitions are in field_schema.json.')
    else:st.info('No records to export.')
st.divider()
st.caption('TP53 Clinical Registry · Demonstration only · No clinical decision making · No real patient data')
