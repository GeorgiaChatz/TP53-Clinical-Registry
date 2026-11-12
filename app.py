"""TP53 Clinical Registry — visual prototype matching approved mockup.
Synthetic-data research demonstration; no authentication or real-patient use.
"""
import html
import json
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title='TP53 Clinical Registry',page_icon='✚',layout='wide',initial_sidebar_state='expanded')

CSS = '''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"], [data-testid="stApp"]{font-family:Inter,system-ui,-apple-system,sans-serif!important}
[data-testid="stAppViewContainer"]{background:#fff;color:#171a21}
.block-container{max-width:1080px;padding:1.55rem 2.2rem 4rem!important}
[data-testid="stSidebar"]{background:#fbfbfc;border-right:1px solid #e9ebee;width:267px!important}
[data-testid="stSidebar"] .block-container{padding:1.15rem .8rem!important}
[data-testid="stSidebarUserContent"]{padding:1.1rem .8rem}
[data-testid="stSidebar"] [data-testid="stButton"] button{border:0;box-shadow:none!important;background:transparent;text-align:left;justify-content:flex-start;padding:.55rem .75rem;border-radius:9px;color:#303642;font-weight:500;min-height:38px;width:100%}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover{background:#eef0f3;color:#101319}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]{background:#eff0f2;color:#15171b;font-weight:700}
[data-testid="stSidebar"] [data-testid="stRadio"] label{font-size:.87rem}
[data-testid="stSidebar"] hr{margin:.65rem 0;border-color:#e7e9ec}
[data-testid="stForm"]{border:0!important;padding:0!important}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] [data-baseweb="select"]>div{border:1px solid #dce0e5;background:white;border-radius:13px!important;min-height:43px}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:#547bdc}
[data-testid="stWidgetLabel"] label{font-weight:500;color:#5f636d}
[data-testid="stFormSubmitButton"] button,[data-testid="stButton"] button[kind="primary"]{border-radius:13px;background:#16181d;border:1px solid #16181d;color:white;font-weight:600;min-height:43px}
[data-testid="stFormSubmitButton"] button:hover,[data-testid="stButton"] button[kind="primary"]:hover{background:#333a43;color:white}
[data-testid="stHorizontalBlock"]{gap:.9rem}
[data-testid="stMetric"]{background:#fff;border:1px solid #ebedf0;border-radius:13px;padding:18px}
[data-testid="stMetricLabel"]{color:#747781}
[data-testid="stMetricValue"]{font-weight:700;font-size:1.65rem}
[data-testid="stExpander"]{border:1px solid #e6e8eb;border-radius:12px;background:#fff}
.tp-brand{display:flex;align-items:center;gap:10px;padding:4px 8px 14px;margin-bottom:13px;border-bottom:1px solid #e9ebee}
.tp-brand-mark{font-size:26px;font-weight:800;color:#1684e9;line-height:1}
.tp-brand-name{font-size:15px;color:#17191e;font-weight:750;letter-spacing:-.3px}
.tp-brand-sub{font-size:11px;color:#82858c;margin-top:3px}
.tp-side-caption{font-size:11px;text-transform:uppercase;letter-spacing:.065em;color:#858890;margin:15px 9px 5px}
.tp-top{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:18px;padding-bottom:17px;border-bottom:1px solid #eceef1}
.tp-title{font-size:23px;letter-spacing:-.6px;color:#181b21;font-weight:750;margin:2px 0 4px}
.tp-subtitle{font-size:12px;color:#858994}
.tp-crumb{font-size:12px;color:#83868d;margin-bottom:7px}
.tp-pill{border-radius:50px;background:#f1f2f4;padding:5px 11px;font-size:11px;font-weight:600;color:#434950;white-space:nowrap}
.tp-pill.green{background:#e2f5e8;color:#1f7d44}.tp-pill.blue{background:#e6efff;color:#1a70c8}
.tp-section-title{font-size:14px;font-weight:700;color:#25282e;margin:19px 0 12px}
.tp-line{height:1px;background:#edf0f2;margin:17px 0}
.tp-note{font-size:11px;color:#8a8e96;margin-top:10px}
.tp-card{border:1px solid #e4e6e9;border-radius:16px;padding:15px 17px;margin:10px 0 3px;background:#fff}
.tp-card-top{display:flex;justify-content:space-between;align-items:center;gap:12px}
.tp-card-title{font-size:15px;font-weight:700;color:#20242b}
.tp-card-meta{font-size:12px;color:#777d86;margin-top:10px}
.tp-card-count{font-size:12px;color:#858b92}
.tp-timeline{position:relative;margin:0 0 0 9px;padding:0 0 11px 22px;border-left:2px solid #e6e8eb}
.tp-dot{width:11px;height:11px;border:2px solid #2b78dc;background:white;border-radius:50%;position:absolute;left:-7px;top:5px}
.tp-event{font-size:14px;font-weight:650}.tp-event-meta{font-size:12px;color:#848892;margin-top:5px}
.tp-empty{border:1px dashed #d9dce0;border-radius:14px;padding:22px;color:#7b7f86;text-align:center;font-size:13px}
.tp-form-lead{font-size:12px;color:#81858e;margin-bottom:10px}
.tp-foot{border-top:1px solid #eff0f2;margin-top:34px;padding-top:14px;color:#92959a;font-size:11px}
/* Hide default top chrome and reduce Streamlit extra spacing */
#MainMenu{visibility:hidden}footer{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
[data-testid="stVerticalBlock"]{gap:.65rem}

/* Approved layout: quiet left navigation, clean two-column patient form */
[data-testid="stSidebar"]{min-width:238px!important;max-width:238px!important;width:238px!important;background:#fafafa!important}
[data-testid="stSidebarUserContent"]{padding:0.35rem 0.55rem 1.2rem!important}
[data-testid="stSidebar"] .tp-brand{padding:7px 8px 17px;margin:0 0 8px;border-bottom:1px solid #ececef}
[data-testid="stSidebar"] .tp-side-caption{font-size:12px;letter-spacing:.035em;margin:14px 8px 5px;color:#7b7e84}
.tp-side-rule{height:1px;background:#ebebee;margin:15px 0 10px}
[data-testid="stSidebar"] [data-testid="stButton"] button{border:0!important;border-radius:8px!important;background:transparent!important;min-height:35px!important;font-weight:500!important;font-size:12px!important;padding:6px 10px!important;box-shadow:none!important}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]{background:#f0f0f1!important;color:#151515!important;font-weight:650!important}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover{background:#e9eaed!important;color:#151515!important}
[data-testid="stSidebar"] [data-testid="stExpander"]{background:transparent!important;border:0!important}
.tp-sidebar-bottom{font-size:11px;color:#80838a;border-top:1px solid #ececef;margin-top:28px;padding:17px 10px}
[data-testid="stAppViewContainer"] .block-container{max-width:990px!important;padding:1.0rem 1.4rem 4rem!important}
.tp-top{margin-bottom:13px!important;padding-bottom:7px!important;border-bottom:0!important}
.tp-title{font-size:22px!important;font-weight:700!important;margin:0 0 5px!important}
.tp-section-title{font-size:14px!important;margin:14px 0 9px!important}
[data-testid="stWidgetLabel"] label{font-size:13px!important;color:#666!important}
[data-testid="stFormSubmitButton"]{display:flex;justify-content:flex-end;margin-top:16px}
[data-testid="stFormSubmitButton"] button{background:#101010!important;border-radius:22px!important;min-width:125px}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] [data-baseweb="select"]>div{border-radius:15px!important;background:#fff!important}
[data-testid="stForm"]{border:0!important}
</style>'''
st.markdown(CSS,unsafe_allow_html=True)

def esc(s):return html.escape(str(s or ''))

def top(title,crumb='',tag=None,subtitle=''):
    pill=f'<span class="tp-pill">{esc(tag)}</span>' if tag else ''
    extra=f'<div class="tp-subtitle">{esc(subtitle)}</div>' if subtitle else ''
    st.markdown(f'<div class="tp-top"><div><div class="tp-crumb">{esc(crumb)}</div><div class="tp-title">{esc(title)}</div>{extra}</div>{pill}</div>',unsafe_allow_html=True)

def section_title(label):st.markdown(f'<div class="tp-section-title">{esc(label)}</div>',unsafe_allow_html=True)
def line():st.markdown('<div class="tp-line"></div>',unsafe_allow_html=True)
def goto(page,pid=None,section=None):
    st.session_state.page=page
    if pid is not None:st.session_state.patient=pid
    if section is not None:st.session_state.section=section
    st.rerun()

try:
    import db
    db.init()
except Exception as exc:
    st.error('Database connection failed. Open your Streamlit Cloud app settings → Secrets and check DATABASE_URL.');st.code(f'{type(exc).__name__}: {exc}')
    st.info('Use a Supabase Session pooler PostgreSQL connection URI. The PostgreSQL driver must be installed from requirements.txt.')
    st.stop()

schema=json.loads((Path(__file__).parent/'field_schema.json').read_text(encoding='utf8'))['sections']
SECTION_MAP={'Patient Information':'Patient details','Molecular Diagnosis':'Diagnosis & TP53','Treatment & Outcomes':'Treatment & outcomes','Allogeneic SCT':'Allogeneic transplant','Molecular Follow-up':'Molecular follow-up'}
SIDE_SECTIONS=['Patient Information','Molecular Diagnosis','Treatment & Outcomes','Allogeneic SCT','Molecular Follow-up','Clinical Guidelines','Full Clinical History','Modification History']
REPEAT={'Molecular follow-up','Treatment episode'}

def show_sidebar():
    """The navigation follows the approved patient-workspace mockup."""
    with st.sidebar:
        st.markdown('<div class="tp-brand"><span class="tp-brand-mark">✚</span><div><div class="tp-brand-name">TP53 Clinical Registry</div><div class="tp-brand-sub">Research data management</div></div></div>',unsafe_allow_html=True)
        st.markdown('<div class="tp-side-caption">WORKSPACE</div>',unsafe_allow_html=True)
        for item,ico in [('Dashboard','▦'),('Patient Registry','♙')]:
            if st.button(f'{ico}   {item}',key='nav_'+item,type='primary' if st.session_state.page==item else 'secondary',use_container_width=True):
                goto(item)
        st.markdown('<div class="tp-side-rule"></div>',unsafe_allow_html=True)
        st.markdown('<div class="tp-side-caption">PATIENT RECORD</div>',unsafe_allow_html=True)
        pid=st.session_state.patient
        if pid and db.get_patient(pid):
            icons=['♙','⌁','◇','♡','▧','▤','◷','≡']
            for sec,ico in zip(SIDE_SECTIONS,icons):
                active=st.session_state.page=='Patient Workspace' and st.session_state.section==sec
                if st.button(f'{ico}   {sec}',key='sec_'+sec,type='primary' if active else 'secondary',use_container_width=True):
                    goto('Patient Workspace',pid,sec)
        else:
            st.caption('Choose a patient from the registry to display clinical sections.')
        st.markdown('<div class="tp-side-rule"></div>',unsafe_allow_html=True)
        with st.expander('＋  More tools',expanded=False):
            if st.button('＋  New Patient',key='nav_create',use_container_width=True):goto('New Patient')
            if st.button('⇩  Export Data',key='nav_export',use_container_width=True):goto('Export Data')
        st.markdown('<div class="tp-sidebar-bottom">♢  Research prototype · Fictional data only</div>',unsafe_allow_html=True)


def clinical_field(field,old,namespace):
    key=field['key'];label=' '.join(field['label'].split()); low=label.lower();val=str(old.get(key,'') or '');ukey=namespace+'_'+key
    if key=='c3' and 'sex' in low:
        options={'':'Not recorded','1':'Female','2':'Male'}
    elif key=='c2' and low.startswith('diagnosis'):
        options={'':'Not recorded','1':'MDS','2':'AML'}
    elif 'ecog' in low:
        options={'':'Not recorded',**{str(i):str(i)+' — '+['Fully active','Restricted strenuous activity','Ambulatory, self-care','Limited self-care','Completely disabled'][i] for i in range(5)}}
    elif any(t in low for t in ['yes=1, no=0','no=0, yes=1','available=1, n/a=0','no=0,yes=1']):
        options={'':'Not recorded','0':'No','1':'Yes','9':'Not available'}
    elif 'donor matching' in low:
        options={'':'Not recorded','0':'Haploidentical','1':'10/10','2':'9/10','3':'8/10'}
    else:options=None
    if options:
        if val not in options:options[val]=val
        return st.selectbox(label,list(options),index=list(options).index(val),format_func=lambda x:options[x],key=ukey)
    if any(t in low for t in ['additional information','comorbidit','immunophenotype','specific mutation','karyotype','conditioning','cause of death','specific drugs','annotation','notes']):
        return st.text_area(label,value=val,key=ukey,height=105,placeholder='Enter information (optional)')
    return st.text_input(label,value=val,key=ukey,placeholder='YYYY-MM-DD' if 'date' in low else 'Not recorded')


def validate_values(fields,values):
    for field in fields:
        label=field['label'].lower();v=str(values.get(field['key'],'')).strip()
        if not v:continue
        if 'date' in label and re.fullmatch(r'\d{4}-\d{2}-\d{2}',v):
            datetime.strptime(v,'%Y-%m-%d')
        elif 'date' in label and not re.fullmatch(r'\d{4}-\d{2}-\d{2}',v) and 'time to' not in label:
            raise ValueError(f'{field["label"]} must be YYYY-MM-DD.')
        if 'vaf (%)' in label:
            try:f=float(v)
            except ValueError:raise ValueError('VAF must be a number.')
            if not 0<=f<=100:raise ValueError('VAF must be between 0 and 100.')


def form(pid,name):
    section=SECTION_MAP[name]
    entries=db.entries(pid,section) if section in REPEAT else []
    episode=1
    if section in REPEAT:
        choices=[r['episode'] for r in entries]+['+ Add new assessment']
        selected=st.selectbox('Assessment',choices,format_func=lambda v:'Assessment '+str(v) if isinstance(v,int) else v,key='assessment_'+pid)
        episode=db.next_episode(pid,section) if isinstance(selected,str) else selected
    old=db.get_entry(pid,section,episode)
    fields=schema[section]
    if name=='Patient Information':
        section_title('Patient identification')
    elif name=='Molecular Diagnosis':section_title('Baseline diagnosis & molecular results')
    elif name=='Treatment & Outcomes':section_title('Treatment history and clinical response')
    elif name=='Allogeneic SCT':section_title('Transplant details')
    else:section_title('Molecular assessment')
    if name=='Patient Information':
        # Present custom visible patient ID / center / sex exactly as in the UI mockup.
        p=db.get_patient(pid)
        with st.form('patient_form_'+pid):
            col1,col2=st.columns(2)
            with col1:st.text_input('Patient code',value=pid,disabled=True,help='Research ID is fixed once the patient is registered.')
            with col2:center=st.text_input('Hospital / Center',value=old.get('c2') or p['center'])
            sex=st.radio('Biological sex',['Not recorded','Female','Male'],index={'':0,'1':1,'2':2}.get(str(old.get('c3','')),0),horizontal=True)
            line();section_title('Clinical information')
            ecog_options=['Not recorded','0 — Fully active','1 — Restricted strenuous activity','2 — Ambulatory, self-care','3 — Limited self-care','4 — Completely disabled']
            ecog_old=str(old.get('c11',''))
            eco=st.selectbox('ECOG Performance Status',ecog_options,index=int(ecog_old)+1 if ecog_old in ['0','1','2','3','4'] else 0)
            notes=st.text_area('Comorbidities / Additional information',value=old.get('c10',''),height=105,placeholder='Enter clinical notes (optional)')
            with st.expander('Additional patient characteristics',expanded=False):
                extra={}
                other=[f for f in fields if f['key'] not in ('c2','c3','c10','c11')]
                for i in range(0,len(other),2):
                    cols=st.columns(2)
                    for j,c in enumerate(cols):
                        if i+j<len(other):
                            f=other[i+j]
                            with c:extra[f['key']]=clinical_field(f,old,pid+'_patient')
            save=st.form_submit_button('▣  Save draft',type='primary',use_container_width=False)
        if save:
            values=dict(old)
            values.update(extra)
            values.update({'c2':center,'c3':{'Not recorded':'','Female':'1','Male':'2'}[sex],'c11':eco[0] if eco!='Not recorded' else '','c10':notes})
            try:
                validate_values(fields,values);db.save_entry(pid,section,1,values);db.update_patient(pid,center=center);st.success('Patient information saved to '+db.BACKEND+'.')
            except Exception as e:st.error(f'Could not save: {e}')
        return
    with st.form('clinical_form_'+pid+'_'+section+'_'+str(episode)):
        values={}
        # Clinical detail fields in consistent two-column rows, preserving all workbook fields.
        for i in range(0,len(fields),2):
            cols=st.columns(2)
            for j,col in enumerate(cols):
                if i+j<len(fields):
                    f=fields[i+j]
                    with col:values[f['key']]=clinical_field(f,old,pid+'_'+section+'_'+str(episode))
        save=st.form_submit_button('▣  Save draft',type='primary')
    if save:
        try:
            validate_values(fields,values);db.save_entry(pid,section,episode,values)
            if section=='Diagnosis & TP53':db.update_patient(pid,diagnosis={'1':'MDS','2':'AML'}.get(values.get('c2',''),''))
            st.success('Section saved successfully in '+db.BACKEND+'.')
        except Exception as e:st.error('Could not save: '+str(e))


def timeline(pid):
    events=[];trend=[]
    for e in db.entries(pid):
        section=e['section'];d=e['data'];num=e['episode'];date='';title=section
        if section=='Patient details':date=d.get('c8','');title='Patient baseline'
        elif section=='Diagnosis & TP53':date=d.get('c3','');title='Molecular diagnosis'
        elif section=='Treatment & outcomes':date=d.get('c7','');title='First-line treatment and outcomes'
        elif section=='Treatment episode':date=d.get('date','');title=d.get('title') or 'Additional treatment'
        elif section=='Allogeneic transplant':date=d.get('c4','');title='Allogeneic SCT'
        elif section=='Molecular follow-up':
            date=d.get('c4','');title=d.get('c2') or 'Molecular reassessment'
            try:
                v=float(d.get('c10',''))
                if date and 0<=v<=100:trend.append({'Date':pd.to_datetime(date),'TP53 VAF (%)':v})
            except (ValueError,TypeError):pass
        events.append((date,title,section,num))
    section_title('Patient journey')
    if not events:st.markdown('<div class="tp-empty">No history yet. Save a patient section to create the first event.</div>',unsafe_allow_html=True)
    for date,title,section,num in sorted(events,key=lambda e:e[0] or '9999-12-31'):
        st.markdown(f'<div class="tp-timeline"><span class="tp-dot"></span><div class="tp-event">{esc(title)}</div><div class="tp-event-meta">{esc(date or "Date not recorded")} · {esc(section)} · Entry {num}</div></div>',unsafe_allow_html=True)
    if trend:
        section_title('TP53 VAF trend')
        st.line_chart(pd.DataFrame(trend).sort_values('Date').set_index('Date'))


def patient_workspace(pid):
    p=db.get_patient(pid)
    if not p:st.warning('Patient not found.');return
    name=st.session_state.section
    top(name,f'Patient / {pid}','Draft' if name in SECTION_MAP else 'Record',subtitle=f'{p["diagnosis"] or "Diagnosis not recorded"} · {p["center"] or "Center not recorded"}')
    if name in SECTION_MAP:form(pid,name)
    elif name=='Clinical Guidelines':
        section_title('Clinical reference materials')
        st.info('The workbook includes karyotype, TP53, and NGS guidelines. This section is reserved for approved reference material; no diagnostic recommendations are generated.')
    elif name=='Full Clinical History':timeline(pid)
    elif name=='Modification History':
        section_title('Record modification history')
        history=db.audit(pid)
        if not history:st.info('No changes recorded.')
        for item in history:
            with st.expander(f'{item["recorded_at"]}  ·  {item["section"]}  ·  {item["action"]}'):
                st.caption('This demo logs changes but does not yet identify individual researchers.')
                for label,key in [('Before','old_json'),('After','new_json')]:
                    if item.get(key):st.write(label);st.json(json.loads(item[key]))
    if name=='Treatment & Outcomes':
        line();section_title('Additional treatment episodes')
        st.caption('Add as many separate treatment lines as necessary.')
        existing=db.entries(pid,'Treatment episode')
        st.caption(f'{len(existing)} additional episodes saved')
        with st.expander('Add / edit treatment episode'):
            opt=st.selectbox('Treatment episode',[x['episode'] for x in existing]+['+ New treatment'],format_func=lambda z:'Treatment '+str(z) if isinstance(z,int) else z)
            ep=opt if isinstance(opt,int) else db.next_episode(pid,'Treatment episode');old=db.get_entry(pid,'Treatment episode',ep)
            with st.form('treat_extra_'+pid+'_'+str(ep)):
                drug=st.text_input('Treatment / regimen',value=old.get('title',''))
                dt=st.text_input('Start date (YYYY-MM-DD)',value=old.get('date',''))
                response=st.text_input('Clinical response',value=old.get('response',''))
                notes=st.text_area('Additional details',value=old.get('notes',''))
                ok=st.form_submit_button('Save treatment',type='primary')
            if ok:
                try:
                    if dt:datetime.strptime(dt,'%Y-%m-%d')
                    db.save_entry(pid,'Treatment episode',ep,dict(title=drug,date=dt,response=response,notes=notes));st.success('Treatment saved.')
                except Exception as e:st.error(str(e))


def patient_card(p,index):
    pid=p['patient_id'];diag=p['diagnosis'] or 'Not classified';center=p['center'] or 'Center not recorded'
    saved=db.entries(pid);assessments=len([x for x in saved if x['section']=='Molecular follow-up'])
    if 'transplant' in (p['diagnosis'] or '').lower():status='Transplanted'
    elif assessments:status='Follow-up'
    else:status='Draft'
    with st.container(border=True):
        c1,c2=st.columns([5,2],vertical_alignment='center')
        with c1:
            st.markdown(f'<div class="tp-card-title">♙ &nbsp; {esc(pid)}</div><div class="tp-card-meta">{esc(diag)} · {esc(center)}</div>',unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="text-align:right"><span class="tp-pill">{status}</span><div class="tp-card-meta">{assessments} molecular assessments</div></div>',unsafe_allow_html=True)
            if st.button('Open patient →',key='open_'+str(index)+'_'+pid,use_container_width=True):goto('Patient Workspace',pid,'Patient Information')


def registry():
    top('Patient Registry','Workspace / Patients','Research demo',subtitle='Search patients and view their clinical history')
    n,e=db.stats();centers=len(set(p['center'] for p in db.list_patients() if p['center']))
    a,b,c=st.columns(3);a.metric('Patients',n);b.metric('Saved assessments',e);c.metric('Centers',centers)
    q=st.text_input('Search patients',placeholder='Search by patient ID, diagnosis, or hospital...',label_visibility='collapsed')
    rows=db.list_patients(q)
    if not rows:st.info('No patients match that search.')
    for i,p in enumerate(rows):patient_card(p,i)


def dashboard():
    top('Research Dashboard','Workspace / Overview','Prototype',subtitle='TP53 registry overview and recent activity')
    n,e=db.stats();centers=len(set(p['center'] for p in db.list_patients() if p['center']))
    a,b,c=st.columns(3);a.metric('Patients',n);b.metric('Saved entries',e);c.metric('Centers',centers)
    section_title('Recent patients')
    for i,p in enumerate(db.list_patients()[:6]):patient_card(p,i)
    if st.button('Browse patient registry',type='primary'):goto('Patient Registry')


def create_patient():
    top('New Patient','Workspace / Register','Draft',subtitle='Register a fictional research ID, then complete clinical sections')
    section_title('Patient identification')
    with st.form('new_patient'):
        a,b=st.columns(2)
        with a:pid=st.text_input('Patient code',placeholder='DEMO-005')
        with b:center=st.text_input('Hospital / Center',placeholder='Research Center A')
        diagnosis=st.selectbox('Diagnosis',['Not recorded','MDS','AML'])
        ok=st.form_submit_button('Create patient record',type='primary')
    if ok:
        try:
            db.create_patient(pid.strip(),center,'' if diagnosis=='Not recorded' else diagnosis)
            goto('Patient Workspace',pid.strip(),'Patient Information')
        except Exception as e:st.error('Could not create patient: '+str(e))


def export_data():
    top('Export Research Data','Workspace / Export','CSV',subtitle='Download a structured dataset for statistical analysis')
    rows=[]
    for p in db.list_patients():
        entries=db.entries(p['patient_id'])
        if not entries:rows.append({'patient_id':p['patient_id'],'center':p['center'],'diagnosis':p['diagnosis']})
        for e in entries:rows.append({'patient_id':p['patient_id'],'center':p['center'],'diagnosis':p['diagnosis'],'section':e['section'],'episode':e['episode'],**e['data']})
    if rows:
        frame=pd.DataFrame(rows)
        st.download_button('⇩ Download CSV',frame.to_csv(index=False).encode('utf-8-sig'),'tp53_demo_export.csv','text/csv',type='primary')
        st.dataframe(frame,hide_index=True,use_container_width=True)
    else:st.info('No data to export.')

try:
    db.seed_demo()
except Exception as exc:
    st.warning('Sample records could not be initialized: '+str(exc))

if 'page' not in st.session_state:
    st.session_state.page='Patient Workspace'
if 'patient' not in st.session_state:
    examples=db.list_patients()
    st.session_state.patient=next((p['patient_id'] for p in examples if p['patient_id']=='DEMO-001'), examples[0]['patient_id'] if examples else None)
if 'section' not in st.session_state:
    st.session_state.section='Patient Information'
if st.session_state.page=='Patient Workspace' and not st.session_state.patient:
    st.session_state.page='New Patient'
show_sidebar()
page=st.session_state.page
if page=='Dashboard':dashboard()
elif page=='Patient Registry':registry()
elif page=='New Patient':create_patient()
elif page=='Patient Workspace':
    if st.session_state.patient:patient_workspace(st.session_state.patient)
    else:st.info('Choose a patient from Patient Registry.')
elif page=='Export Data':export_data()
st.markdown('<div class="tp-foot">TP53 Clinical Registry · Fictional data only · No authentication · Not for clinical use</div>',unsafe_allow_html=True)
