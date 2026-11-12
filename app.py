"""TP53 Registry — proof-of-concept; fictional patients only."""
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import db

ROOT=Path(__file__).parent
SCHEMA=json.loads((ROOT/'field_schema.json').read_text(encoding='utf-8'))['sections']
SECTIONS=['Patient details','Diagnosis & TP53','Treatment & outcomes','Treatment episode','Allogeneic transplant','Molecular follow-up']
REPEATABLE={'Treatment episode','Molecular follow-up'}
PAGE_ICONS={'Patient details':'👤','Diagnosis & TP53':'🧬','Treatment & outcomes':'💊','Treatment episode':'💉','Allogeneic transplant':'🏥','Molecular follow-up':'🔬'}

st.set_page_config(page_title='TP53 Research Registry | Demo',page_icon='🧬',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
.stApp {background: #f7f9fc; color:#14243d;}
section[data-testid="stSidebar"] {background:#101e36;}
section[data-testid="stSidebar"] * {color:#e8edf5;}
.block-container {padding-top:2rem;max-width:1350px;}
.hero {background:linear-gradient(115deg,#152945,#234d74);padding:24px 28px;border-radius:16px;color:#fff;margin-bottom:16px}
.hero h1{font-size:28px;margin:0;color:white}.hero p{margin:6px 0 0;color:#cddfeb}
.pill {display:inline-block;padding:5px 11px;background:#e8f0f8;border-radius:100px;color:#235075;font-size:12px}
small{color:#657792}
[data-testid="stMetric"]{background:white;padding:15px;border:1px solid #e4ebf3;border-radius:12px}
</style>''',unsafe_allow_html=True)
db.init()
if 'initialized' not in st.session_state:
    db.seed_demo()
    st.session_state.initialized=True
if 'patient_id' not in st.session_state:st.session_state.patient_id=None
if 'nav' not in st.session_state:st.session_state.nav='Dashboard'

st.sidebar.markdown('## 🧬 TP53 Registry')
st.sidebar.caption('Clinical research · Prototype')
st.sidebar.warning('DEMO ONLY · Use fictional / synthetic records. Not approved for real patient data.')
if st.session_state.get('pending_nav'):
    st.session_state.nav=st.session_state.pop('pending_nav')
nav=st.sidebar.radio('Workspace',['Dashboard','Patient registry','New patient','Research export'],key='nav')
st.sidebar.divider()
st.sidebar.caption('LOCAL TESTING')
st.sidebar.markdown('📁 SQLite database on this computer')
st.sidebar.markdown('🔐 No login in this prototype')

def go_patient(pid):
    st.session_state.patient_id=pid
    st.session_state.pending_nav='Patient registry'
    st.rerun()

def header(title,subtitle):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',unsafe_allow_html=True)

def field_type(label):
    l=label.lower()
    if 'date' in l or 'dob' in l:return 'date'
    if ('yes=1' in l or 'no=0' in l or 'no =0' in l or 'available=1' in l or 'n/a=9' in l or 'n/a=0' in l):return 'coded'
    if l.startswith('sex ') or l.startswith('diagnosis ') or 'donor matching' in l:return 'choice'
    if any(x in l for x in ['vaf (%)','blast percentage','height (cm)','weight (kg)','bsa (','ecog','karnofsky']):return 'number'
    if any(x in l for x in ['information','comorbidities','karyotype at','specific drugs','conditioning','annotation','mutation/alteration','immunophenotype','cause of death']):return 'long'
    return 'text'

def widget(field,value,namespace):
    name=field['label'];key=f'{namespace}_{field["key"]}'
    kind=field_type(name)
    label=name.replace('                    ',' ').replace('       ',' ')
    if kind=='coded':
        val=str(value or '')
        opts=['','0','1','9'] if '9' in label else ['','0','1']
        if val not in opts: opts.append(val)
        return st.selectbox(label,opts,index=opts.index(val),format_func=lambda v:{'':'— Not entered —','0':'0 — No / negative / unavailable (see label)','1':'1 — Yes / positive / available (see label)','9':'9 — N/A'}.get(v,v),key=key)
    if kind=='choice':
        if name.lower().startswith('sex'): opts=['','1','2'];names={'':'— Not entered —','1':'1 — Female','2':'2 — Male'}
        elif name.lower().startswith('diagnosis'):opts=['','1','2'];names={'':'— Not entered —','1':'1 — MDS','2':'2 — AML'}
        else: opts=['','0','1','2','3'];names={'':'— Not entered —','0':'0 — Haplo','1':'1 — 10/10','2':'2 — 9/10','3':'3 — 8/10'}
        v=str(value or '')
        if v not in opts:opts.append(v)
        return st.selectbox(label,opts,index=opts.index(v),format_func=lambda x:names.get(x,x),key=key)
    if kind=='date':
        return st.text_input(label,value=str(value or ''),placeholder='YYYY-MM-DD',key=key,help='Use ISO date format YYYY-MM-DD; blank is allowed.')
    if kind=='long':return st.text_area(label,value=str(value or ''),height=82,key=key)
    return st.text_input(label,value=str(value or ''),key=key)

def render_form(pid,section,episode):
    data=db.get_entry(pid,section,episode)
    if section=='Treatment episode':
        fields=[{'key':'title','label':'Treatment / regimen'}, {'key':'date','label':'Date of initiation'},
                {'key':'response','label':'Response'}, {'key':'response_date','label':'Date of response'},
                {'key':'relapse_date','label':'Date of relapse'}, {'key':'notes','label':'Additional information'}]
        st.info('Add as many treatment episodes as needed. The original Excel treatment fields are also available separately in Treatment & outcomes.')
    else:fields=SCHEMA[section]
    st.caption(f'{len(fields)} fields · Blank fields are allowed · Editing patient {pid} · Entry {episode}')
    with st.form(f'form_{pid}_{section}_{episode}'):
        values={}
        for i in range(0,len(fields),2):
            cols=st.columns(2)
            for j,col in enumerate(cols):
                if i+j<len(fields):
                    f=fields[i+j]
                    with col:values[f['key']]=widget(f,data.get(f['key'],''),f'{pid}_{section}_{episode}')
        submitted=st.form_submit_button('💾 Save this section',type='primary',use_container_width=True)
    if submitted:
        for f in fields:
            if field_type(f['label'])=='date' and values.get(f['key']):
                try:datetime.strptime(values[f['key']],'%Y-%m-%d')
                except ValueError:
                    st.error(f'Invalid date in "{f["label"]}". Use YYYY-MM-DD.')
                    return
        for f in fields:
            if 'vaf (%)' in f['label'].lower() and values.get(f['key']):
                try:
                    if not 0<=float(values[f['key']])<=100:raise ValueError()
                except ValueError:
                    st.error('VAF must be a percentage between 0 and 100.');return
        changed=db.save_entry(pid,section,episode,values)
        if section=='Patient details':db.update_patient(pid,center=values.get('c2',''))
        if section=='Diagnosis & TP53':
            d={'1':'MDS','2':'AML'};db.update_patient(pid,diagnosis=d.get(values.get('c2',''),''))
        st.success('Saved to the local database.' if changed else 'No changes to save.')

def patient_timeline(pid):
    all_entries=db.entries(pid)
    timeline=[]
    for e in all_entries:
        s=e['section'];d=e['data'];ep=e['episode']
        if s=='Patient details':date=d.get('c8','');title='Patient diagnosis recorded'
        elif s=='Diagnosis & TP53':date=d.get('c3','');title='Molecular diagnosis'
        elif s=='Treatment episode':date=d.get('date','');title=d.get('title','Treatment episode')
        elif s=='Molecular follow-up':date=d.get('c4','');title=d.get('c2','Molecular assessment')
        elif s=='Allogeneic transplant':date=d.get('c4','');title='Allogeneic transplant'
        else:date=d.get('c7','') or d.get('c2','');title='Treatment / outcomes entry'
        timeline.append((date if re.fullmatch(r'\d{4}-\d{2}-\d{2}',date or '') else '9999-99-99',date,title,s,ep))
    for _,date,title,section,ep in sorted(timeline):
        with st.container(border=True):
            st.markdown(f'**{title}** &nbsp; <span class="pill">{section}</span>',unsafe_allow_html=True)
            st.caption(f'{date or "Date not recorded"} · Entry {ep}')
    if not timeline:st.info('No history yet. Fill in sections to create the clinical timeline.')

def patient_workspace(pid):
    p=db.get_patient(pid)
    if not p:st.error('Patient not found.');return
    header(f'Patient {pid}','Clinical profile · Sections · Longitudinal history')
    a,b,c=st.columns(3)
    a.metric('Diagnosis',p['diagnosis'] or 'Not set')
    b.metric('Center',p['center'] or 'Not set')
    c.metric('Saved entries',len(db.entries(pid)))
    sec=st.selectbox('Clinical section',['Overview & timeline']+SECTIONS+['Modification history'],key=f'section_{pid}')
    if sec=='Overview & timeline':
        st.subheader('Patient timeline')
        patient_timeline(pid)
        st.subheader('Molecular VAF trend')
        graph=[]
        for e in db.entries(pid,'Molecular follow-up'):
            d=e['data'];date=d.get('c4','');v=d.get('c10','')
            try:
                if date:graph.append({'Date':pd.to_datetime(date),'VAF (%)':float(v)})
            except (ValueError,TypeError):pass
        if graph:
            chart=pd.DataFrame(graph).sort_values('Date').set_index('Date')
            st.line_chart(chart)
        else:st.caption('Enter dated molecular follow-up entries with VAF to display the trend.')
    elif sec=='Modification history':
        st.subheader('Record change history')
        for a in db.audit(pid):
            with st.expander(f'{a["recorded_at"]} · {a["action"]} · {a["section"]}'):
                st.caption('Prototype audit log; not a validated clinical audit trail or per-user attribution.')
                st.json({'previous':json.loads(a['old_json']) if a['old_json'] else None,'new':json.loads(a['new_json']) if a['new_json'] else None})
    else:
        choices=db.entries(pid,sec)
        if sec in REPEATABLE:
            options=[e['episode'] for e in choices]
            selected=st.selectbox('Select saved episode (or create a new one)',options+['+ New entry'],format_func=lambda v:f'Entry {v}' if isinstance(v,int) else v,key=f'ep_{pid}_{sec}')
            ep=db.next_episode(pid,sec) if selected=='+ New entry' else selected
        else:ep=1
        render_form(pid,sec,ep)

if nav=='Dashboard':
    header('Research dashboard','A simple, searchable TP53 registry for one research team')
    n,e=db.stats();a,b,c=st.columns(3)
    a.metric('Registered patients',n);b.metric('Saved clinical entries',e);c.metric('Study mode','Demo')
    st.info('This prototype contains fictional patient records. It has no authentication or production security controls. Do not enter actual patient or identifiable health information.')
    st.subheader('Recent patients')
    for p in db.list_patients()[:5]:
        left,right=st.columns([5,1]);left.write(f'**{p["patient_id"]}** · {p["diagnosis"] or "Not classified"} · {p["center"]}')
        if right.button('Open',key=f'dash_{p["patient_id"]}'):go_patient(p['patient_id'])
    if st.button('Open patient registry →',type='primary'):
        st.session_state.pending_nav='Patient registry';st.rerun()
elif nav=='New patient':
    header('Register a patient','Create a pseudonymized research record')
    with st.form('create_patient'):
        pid=st.text_input('Unique research ID *',placeholder='DEMO-004',help='No names, dates of birth, hospital record numbers or other directly identifying IDs.')
        center=st.text_input('Center / hospital (optional)')
        diag=st.selectbox('Diagnosis (optional)',['','MDS','AML'])
        created=st.form_submit_button('Create patient',type='primary')
    if created:
        try:db.create_patient(pid,center,diag)
        except Exception as ex:st.error(f'Could not create patient: {ex}')
        else:st.success(f'Created {pid}.');go_patient(pid)
elif nav=='Patient registry':
    header('Patient registry','Search, open, and update the complete patient record')
    search=st.text_input('Search research ID, diagnosis or center',placeholder='Try DEMO-001 or MDS')
    rows=db.list_patients(search)
    st.caption(f'{len(rows)} record(s) found')
    for p in rows:
        left,right=st.columns([5,1])
        with left:
            st.markdown(f'**{p["patient_id"]}** · {p["diagnosis"] or "Not classified"} · {p["center"] or "No center"}')
            st.caption('Last edited '+p['updated_at'][:16].replace('T',' '))
        with right:
            if st.button('Open →',key='open_'+p['patient_id'],use_container_width=True):
                st.session_state.patient_id=p['patient_id'];st.rerun()
    if not rows:st.info('No matching records.')
    pid=st.session_state.patient_id
    if pid and db.get_patient(pid):
        st.divider()
        patient_workspace(pid)
else:
    header('Research export','Export fictional research records for analysis')
    data=[]
    for p in db.list_patients():
        for e in db.entries(p['patient_id']):
            data.append({'patient_id':p['patient_id'],'center':p['center'],'diagnosis':p['diagnosis'],
                         'section':e['section'],'episode':e['episode'],**e['data']})
    if data:
        st.download_button('⬇ Download research data (CSV)',pd.DataFrame(data).to_csv(index=False).encode('utf-8-sig'),
                           file_name='tp53_demo_export.csv',mime='text/csv',type='primary')
        st.caption('Columns c2, c3, etc. match positions in the original Excel sheets; field descriptions are in field_schema.json.')
        with st.expander('Preview export'):st.dataframe(pd.DataFrame(data),use_container_width=True)
    else:st.info('No saved data to export.')
st.divider()
st.caption('TP53 Registry · Research prototype · Not a medical device · Not for clinical decision-making or real patient records')
