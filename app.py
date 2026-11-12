"""TP53 Clinical Registry — screenshot-inspired Streamlit interface.
Fictional data only. PostgreSQL on Supabase, or SQLite for disposable local tests.
All clinical Excel headings are preserved in field_schema.json.
"""
from __future__ import annotations
import html
import json
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="TP53 Clinical Registry", page_icon="✚", layout="wide", initial_sidebar_state="expanded")

CSS = r"""
<style>
:root {--ink:#1c1d20; --muted:#72757c; --border:#ededee; --rail:#fafafa; --blue:#087afa;}
html,body,[data-testid="stApp"] {font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; color:var(--ink)}
[data-testid="stAppViewContainer"] {background:#fff;}
header[data-testid="stHeader"] {background:transparent; height:0;}
#MainMenu, footer {visibility:hidden}
/* Full-width header from the approved screenshot */
.tp-global-header {position:fixed;top:0;left:0;right:0;height:88px;z-index:990;background:#fff;border-bottom:1px solid #ececee;display:flex;align-items:center;justify-content:space-between;padding:0 22px 0 12px;box-sizing:border-box;}
.tp-brandline {display:flex;gap:11px;align-items:center;}
.tp-cross {font-size:29px;color:#087cf6;font-weight:700;line-height:1;}
.tp-brandtitle {font-size:17px;font-weight:700;letter-spacing:-.3px;color:#1d1f24;}
.tp-brandsub {font-size:14px;color:#72757c;margin-top:3px;}
.tp-prototype {background:#dbf6e6;color:#078047;font-size:12px;font-weight:650;padding:6px 12px;border-radius:30px;}
/* Rail starts below top masthead */
[data-testid="stSidebar"] {width:236px!important;min-width:236px!important;max-width:236px!important;background:#fafafa!important;border-right:1px solid #ececee!important;}
[data-testid="stSidebarUserContent"] {padding:102px 7px 20px!important;}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap:.18rem!important;}
[data-testid="stSidebar"] hr {border-color:#e8e8ea;margin:13px 4px!important;}
[data-testid="stSidebar"] [data-testid="stButton"] button {border:0!important;box-shadow:none!important;min-height:34px!important;background:transparent!important;border-radius:8px!important;text-align:left!important;justify-content:flex-start!important;width:100%;padding:6px 12px!important;font-size:12px!important;font-weight:500!important;color:#202126!important;}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {background:#eaeaec!important;}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {background:#ededee!important;font-weight:650!important;color:#171717!important;}
.tp-side-cap {font-size:12px;color:#77797e;margin:12px 4px 6px;letter-spacing:.01em;}
.tp-rail-bottom {color:#7e8288;font-size:11px;border-top:1px solid #e5e5e7;padding:14px 5px 0;margin-top:20px;}
/* Main matches screenshot's compact form spacing */
[data-testid="stAppViewContainer"] .block-container {max-width:1050px!important;padding:110px 20px 55px 16px!important;}
[data-testid="stVerticalBlock"] {gap:.52rem!important;}
[data-testid="stForm"] {border:0!important;padding:0!important;margin:0!important;}
[data-testid="stForm"] [data-testid="stVerticalBlock"] {gap:.56rem!important;}
[data-testid="stHorizontalBlock"] {gap:.65rem!important;}
[data-testid="stWidgetLabel"] label {font-size:14px!important;font-weight:500!important;color:#65676d!important;}
[data-testid="stTextInput"] input {border:1px solid #d6d7da!important;border-radius:25px!important;min-height:38px!important;padding:7px 16px!important;background:#fff!important;color:#252529!important;}
[data-testid="stTextArea"] textarea {border:1px solid #d6d7da!important;border-radius:9px!important;background:#fff!important;min-height:80px;}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {border:1px solid #d6d7da!important;border-radius:25px!important;background:#fff!important;min-height:38px!important;}
[data-testid="stRadio"] [role="radiogroup"] {gap:18px!important;}
[data-testid="stRadio"] label {font-size:15px!important;}
[data-testid="stRadio"] input {accent-color:#141414!important;}
[data-testid="stFormSubmitButton"] {display:flex;justify-content:flex-end;border-top:1px solid #f0f0f1;padding-top:18px;margin-top:15px;}
[data-testid="stFormSubmitButton"] button {background:#101010!important;border:1px solid #101010!important;color:#fff!important;border-radius:26px!important;padding:8px 19px!important;font-weight:600!important;min-height:38px!important;}
[data-testid="stFormSubmitButton"] button:hover {background:#333!important;border-color:#333!important;}
[data-testid="stExpander"] {border:1px solid #e8e8ea;border-radius:11px;}
[data-testid="stMetric"] {border:1px solid #ededee;border-radius:12px;padding:15px;background:#fff}
[data-testid="stMetricLabel"] {color:#75797e!important;}
.tp-crumb {font-size:14px;color:#74767a;margin-bottom:5px;}
.tp-title-row {display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:15px;}
.tp-title {font-size:21px;letter-spacing:-.25px;font-weight:700;color:#1b1c20;}
.tp-draft {border-radius:18px;background:#f1f1f2;padding:5px 10px;color:#3d3f43;font-size:12px;font-weight:600;white-space:nowrap;}
.tp-section-title {font-size:14px;font-weight:650;color:#252529;margin:12px 0 9px;}
.tp-rule {border:0;border-top:1px solid #ededee;margin:16px 0 18px;}
.tp-hint {color:#888b90;font-size:12px;margin-top:6px;}
.tp-cardhead {font-size:14px;font-weight:700;color:#20232a;}
.tp-cardsub {font-size:12px;color:#767981;margin-top:8px;}
.tp-listcard {border:1px solid #e3e4e7;border-radius:16px;padding:15px;margin:8px 0 3px;background:#fff;}
.tp-chip {border-radius:16px;background:#f0f0f0;padding:5px 11px;font-size:11px;font-weight:600;color:#34383e;}
.tp-timeline {border-left:2px solid #ebebee;margin-left:10px;padding:0 0 20px 20px;position:relative;}
.tp-timeline:before {content:'';position:absolute;width:9px;height:9px;border-radius:50%;background:#fff;border:2px solid #277de1;left:-7px;top:3px;}
.tp-timeline-title {font-size:14px;font-weight:650;color:#26292c;}
.tp-timeline-date {font-size:12px;color:#83868d;margin-top:4px;}
.tp-footer {margin-top:27px;border-top:1px solid #ededee;padding-top:12px;font-size:11px;color:#94979d;}
@media (max-width:700px){.tp-global-header{height:76px}.tp-brandtitle{font-size:14px}.tp-brandsub{font-size:11px}[data-testid="stAppViewContainer"] .block-container{padding-top:100px!important;}}
</style>
"""
st.markdown(CSS,unsafe_allow_html=True)
st.markdown('''<div class="tp-global-header"><div class="tp-brandline"><div class="tp-cross">✚</div><div><div class="tp-brandtitle">TP53 Clinical Registry</div><div class="tp-brandsub">Research data management</div></div></div><span class="tp-prototype">◉ Prototype</span></div>''',unsafe_allow_html=True)

try:
    import db
    db.init()
    db.seed_demo()
except Exception as exc:
    st.error("The app could not connect to its database. Confirm your Supabase DATABASE_URL in Streamlit Secrets and the packages in requirements.txt.")
    st.code(f"{type(exc).__name__}: {exc}")
    st.stop()

SCHEMA=json.loads((Path(__file__).parent/'field_schema.json').read_text(encoding='utf-8'))['sections']
MENU=[('Patient Information','♙'),('Molecular Diagnosis','⌁'),('Treatment & Outcomes','◇'),('Allogeneic SCT','♡'),('Molecular Follow-up','▧'),('Clinical Guidelines','▤')]
MAPPING={'Patient Information':'Patient details','Molecular Diagnosis':'Diagnosis & TP53','Treatment & Outcomes':'Treatment & outcomes','Allogeneic SCT':'Allogeneic transplant','Molecular Follow-up':'Molecular follow-up'}


def safe(txt): return html.escape(str(txt or ''))
def section_heading(s):st.markdown(f'<div class="tp-section-title">{safe(s)}</div>',unsafe_allow_html=True)
def divider():st.markdown('<hr class="tp-rule">',unsafe_allow_html=True)
def go(page,section=None,pid=None):
    st.session_state.view=page
    if section is not None:st.session_state.section=section
    if pid is not None:st.session_state.patient=pid
    st.rerun()

def top(title,patient=None,badge='Draft'):
    crumb=f'Patient / {safe(patient)}' if patient else 'Workspace'
    st.markdown(f'<div class="tp-crumb">{crumb}</div><div class="tp-title-row"><div class="tp-title">{safe(title)}</div><span class="tp-draft">{safe(badge)}</span></div>',unsafe_allow_html=True)

# Initialize the screenshot's first screen: patient record with all clinical tabs visible.
if 'view' not in st.session_state:st.session_state.view='record'
if 'section' not in st.session_state:st.session_state.section='Patient Information'
if 'patient' not in st.session_state:
    all_patients=db.list_patients()
    st.session_state.patient=(next((p['patient_id'] for p in all_patients if p['patient_id']=='DEMO-001'),all_patients[0]['patient_id'] if all_patients else None))
if st.session_state.view=='record' and not st.session_state.patient:st.session_state.view='new'

with st.sidebar:
    st.markdown('<div class="tp-side-cap">WORKSPACE</div>',unsafe_allow_html=True)
    if st.button('▦  Dashboard',key='nav_dashboard',type='primary' if st.session_state.view=='dashboard' else 'secondary',use_container_width=True):go('dashboard')
    if st.button('♧  Patient Registry',key='nav_registry',type='primary' if st.session_state.view=='registry' else 'secondary',use_container_width=True):go('registry')
    st.divider()
    st.markdown('<div class="tp-side-cap">PATIENT RECORD</div>',unsafe_allow_html=True)
    for name,icon in MENU:
        active=st.session_state.view=='record' and st.session_state.section==name
        if st.button(f'{icon}  {name}',key='nav_'+name,type='primary' if active else 'secondary',use_container_width=True):
            if st.session_state.patient:go('record',section=name)
            else:go('registry')
    st.divider()
    if st.button('＋  New Patient',key='nav_new',use_container_width=True):go('new')
    if st.button('◷  Clinical Timeline',key='nav_timeline',use_container_width=True):go('timeline')
    if st.button('⇩  Export Data',key='nav_export',use_container_width=True):go('export')
    st.markdown('<div class="tp-rail-bottom">♢ Fictional data only · No clinical use</div>',unsafe_allow_html=True)


def widget(field,values,prefix):
    key=field['key'];label=' '.join(field['label'].split()); low=label.lower();current=str(values.get(key,'') or '')
    input_key=f'{prefix}_{key}'
    yesno=('yes=1' in low or 'no=0' in low or 'available=1' in low or '(yes=1' in low)
    if low.startswith('diagnosis'):
        opts={'':'Not recorded','1':'MDS','2':'AML'}
    elif 'donor matching' in low:
        opts={'':'Not recorded','0':'Haploidentical','1':'10/10','2':'9/10','3':'8/10'}
    elif 'allelic state' in low:
        opts={'':'Not recorded','1':'Monoallelic','2':'Biallelic','9':'N/A'}
    elif yesno:
        opts={'':'Not recorded','0':'No','1':'Yes','9':'N/A'}
    else:opts=None
    if opts:
        if current not in opts:opts[current]=current
        return st.selectbox(label,list(opts),index=list(opts).index(current),format_func=lambda x:opts[x],key=input_key)
    if any(word in low for word in ['karyotype','mutation','immunophenotype','regimen','conditioning','comorbid','annotation','notes','specific drugs','cause of death']):
        return st.text_area(label,current,key=input_key,height=76)
    return st.text_input(label,current,key=input_key,placeholder='YYYY-MM-DD' if 'date of' in low else 'Optional')


def other_fields(old,fields,exclude,prefix):
    result={};rest=[f for f in fields if f['key'] not in exclude]
    with st.expander(f'Additional workbook fields ({len(rest)})',expanded=False):
        st.caption('All original Excel fields remain available; leave unknown values empty.')
        for i in range(0,len(rest),2):
            cols=st.columns(2)
            for j,c in enumerate(cols):
                if i+j<len(rest):
                    f=rest[i+j]
                    with c:result[f['key']]=widget(f,old,prefix)
    return result


def save_data(pid,sect,episode,data,center=None,diagnosis=None):
    try:
        for k,v in data.items():
            if 'vaf' in k.lower() and v:
                f=float(v)
                if not 0<=f<=100:raise ValueError('VAF must be 0–100%.')
        db.save_entry(pid,sect,episode,data)
        if center is not None or diagnosis is not None:db.update_patient(pid,center=center,diagnosis=diagnosis)
        st.success('Saved to '+db.BACKEND+'. You can reopen this patient from Patient Registry.')
    except Exception as e:st.error('Could not save: '+str(e))


def patient_info(pid):
    patient=db.get_patient(pid);old=db.get_entry(pid,'Patient details');fields=SCHEMA['Patient details']
    section_heading('Patient identification')
    with st.form('info_'+pid):
        a,b=st.columns(2)
        with a:st.text_input('Patient code',pid,disabled=True)
        with b:center=st.text_input('Hospital / Center',value=old.get('c2') or patient['center'])
        sex_opts=['Not recorded','Female','Male'];s={'1':1,'2':2}.get(str(old.get('c3','')),0)
        sex=st.radio('Biological sex',sex_opts,index=s,horizontal=True)
        divider();section_heading('Clinical information')
        ecog_opts=['Not recorded','0 — Fully active','1 — Restricted strenuous activity','2 — Ambulatory, self-care','3 — Limited self-care','4 — Completely disabled']
        ecog_value=str(old.get('c11',''))
        index=int(ecog_value)+1 if ecog_value in ('0','1','2','3','4') else 0
        ecog=st.selectbox('ECOG Performance Status',ecog_opts,index=index)
        notes=st.text_area('Comorbidities / Additional information',value=old.get('c10',''),height=90,placeholder='Enter clinical notes (optional)')
        extra=other_fields(old,fields,{'c2','c3','c10','c11'},pid+'_info')
        submitted=st.form_submit_button('▣  Save draft')
    if submitted:
        data={**old,**extra,'c2':center,'c3':{'Not recorded':'','Female':'1','Male':'2'}[sex], 'c10':notes,'c11':'' if ecog=='Not recorded' else ecog[0]}
        save_data(pid,'Patient details',1,data,center=center)


def generic_section(pid,display):
    sect=MAPPING[display];old=db.get_entry(pid,sect);fields=SCHEMA[sect]
    title={'Molecular Diagnosis':'Baseline diagnosis & molecular results','Treatment & Outcomes':'Treatment and clinical response','Allogeneic SCT':'Transplant details'}.get(display,display)
    section_heading(title)
    with st.form('form_'+display+'_'+pid):
        data={}
        # Leading Excel variables visible, all remaining variables accessible in an expander.
        lead={'Diagnosis & TP53':12,'Treatment & outcomes':12,'Allogeneic transplant':9}[sect]
        for i in range(0,min(lead,len(fields)),2):
            cols=st.columns(2)
            for j,c in enumerate(cols):
                if i+j<len(fields):
                    f=fields[i+j]
                    with c:data[f['key']]=widget(f,old,pid+'_'+sect)
        data.update(other_fields(old,fields,{f['key'] for f in fields[:lead]},pid+'_'+sect+'_extra'))
        sent=st.form_submit_button('▣  Save draft')
    if sent:
        diag=None
        if sect=='Diagnosis & TP53':diag={'1':'MDS','2':'AML'}.get(data.get('c2',''),'')
        save_data(pid,sect,1,{**old,**data},diagnosis=diag)
    if display=='Treatment & Outcomes':
        divider();section_heading('Additional treatment lines')
        treatments=db.entries(pid,'Treatment episode')
        options=[r['episode'] for r in treatments]+['＋ Add new treatment']
        choice=st.selectbox('Treatment entry',options,format_func=lambda x: f'Treatment {x}' if isinstance(x,int) else x)
        ep=choice if isinstance(choice,int) else db.next_episode(pid,'Treatment episode')
        prev=db.get_entry(pid,'Treatment episode',ep)
        with st.form('tx_'+pid+'_'+str(ep)):
            a,b=st.columns(2)
            with a:reg=st.text_input('Treatment / regimen',value=prev.get('title',''))
            with b:start=st.text_input('Start date (YYYY-MM-DD)',value=prev.get('date',''))
            response=st.text_input('Response',value=prev.get('response',''))
            text=st.text_area('Notes',value=prev.get('notes',''))
            submitted=st.form_submit_button('▣  Save treatment')
        if submitted:
            try:
                if start:datetime.strptime(start,'%Y-%m-%d')
                db.save_entry(pid,'Treatment episode',ep,{'title':reg,'date':start,'response':response,'notes':text});st.success('Treatment saved.')
            except Exception as e:st.error(str(e))


def followup(pid):
    section_heading('Molecular assessments')
    previous=db.entries(pid,'Molecular follow-up')
    choices=[r['episode'] for r in previous]+['＋ Add new assessment']
    selected=st.selectbox('Assessment',choices,format_func=lambda x: f'Assessment {x}' if isinstance(x,int) else x)
    ep=selected if isinstance(selected,int) else db.next_episode(pid,'Molecular follow-up')
    old=db.get_entry(pid,'Molecular follow-up',ep);fields=SCHEMA['Molecular follow-up']
    with st.form('follow_'+pid+'_'+str(ep)):
        timepoint=st.text_input('Clinical time point',old.get('c2',''),placeholder='e.g. At relapse / Post-treatment')
        a,b=st.columns(2)
        with a:date=st.text_input('Date of assessment',old.get('c4',''),placeholder='YYYY-MM-DD')
        with b:vaf=st.text_input('TP53 VAF (%)',old.get('c10',''),placeholder='0–100')
        mutation=st.text_area('TP53 molecular finding',old.get('c9',''),height=82)
        data=other_fields(old,fields,{'c2','c4','c9','c10'},pid+'_follow_'+str(ep))
        ok=st.form_submit_button('▣  Save assessment')
    if ok:
        try:
            if date:datetime.strptime(date,'%Y-%m-%d')
            if vaf and not 0<=float(vaf)<=100:raise ValueError('VAF must be between 0 and 100.')
            save_data(pid,'Molecular follow-up',ep,{**old,**data,'c2':timepoint,'c4':date,'c9':mutation,'c10':vaf})
        except Exception as e:st.error('Could not save assessment: '+str(e))


def timeline(pid):
    events=[];vaf=[]
    for e in db.entries(pid):
        s,d=e['section'],e['data'];when='';name=s
        if s=='Patient details':when=d.get('c8','');name='Patient baseline'
        elif s=='Diagnosis & TP53':when=d.get('c3','');name='Diagnosis and molecular testing'
        elif s=='Treatment & outcomes':when=d.get('c7','');name='First-line treatment'
        elif s=='Treatment episode':when=d.get('date','');name=d.get('title','Additional treatment')
        elif s=='Allogeneic transplant':when=d.get('c4','');name='Allogeneic SCT'
        elif s=='Molecular follow-up':
            when=d.get('c4','');name=d.get('c2','Molecular reassessment')
            try:
                if when and d.get('c10','')!='':vaf.append({'Date':pd.to_datetime(when),'TP53 VAF (%)':float(d['c10'])})
            except (TypeError,ValueError):pass
        events.append((str(when),name,s,e['episode']))
    section_heading('Patient journey')
    if not events:st.info('No events saved yet.')
    for when,name,section,episode in sorted(events,key=lambda x:x[0] or '9999'):
        st.markdown(f'<div class="tp-timeline"><div class="tp-timeline-title">{safe(name)}</div><div class="tp-timeline-date">{safe(when or "Date not recorded")} · {safe(section)} · Entry {episode}</div></div>',unsafe_allow_html=True)
    if vaf:
        section_heading('TP53 VAF over time')
        st.line_chart(pd.DataFrame(vaf).sort_values('Date').set_index('Date'))
    section_heading('Record modification history')
    for ev in db.audit(pid)[:40]:
        with st.expander(f"{ev['recorded_at']} · {ev['section']} · {ev['action']}"):
            st.caption('This prototype does not record individual users.')
            if ev.get('old_json'):st.code(ev['old_json'],language='json')
            if ev.get('new_json'):st.code(ev['new_json'],language='json')


def guidelines():
    section_heading('Clinical reference material from workbook')
    st.caption('Reference guidance below comes from the source workbook; clinical judgment and approved protocols remain necessary.')
    for name,desc in [('Karyotype','Definitions of complex and monosomal karyotype'),('TP53','Notes on allelic state and study limitations'),('NGS','Reporting and classification instructions')]:
        with st.expander(f'{name} guidelines — {desc}'):
            path=Path(__file__).parent/'guidelines.json'
            source=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
            lines=source.get(name,[])
            if lines:
                for text in lines:st.write(text)
            else:st.write('Guideline source content unavailable.')


def patient_record():
    pid=st.session_state.patient
    p=db.get_patient(pid) if pid else None
    if not p:
        st.warning('No patient selected. Open Patient Registry or create a fictional patient.');return
    current=st.session_state.section
    top(current,pid)
    if current=='Patient Information':patient_info(pid)
    elif current=='Molecular Follow-up':followup(pid)
    elif current=='Clinical Guidelines':guidelines()
    else:generic_section(pid,current)


def patient_card(p,index):
    pid=p['patient_id'];events=db.entries(pid);follow=sum(1 for e in events if e['section']=='Molecular follow-up')
    is_sct=bool(db.get_entry(pid,'Allogeneic transplant').get('c4',''))
    status='Transplanted' if is_sct else ('Follow-up' if follow else 'Draft')
    with st.container(border=True):
        x,y=st.columns([3,1],vertical_alignment='center')
        with x:
            st.markdown(f'<div class="tp-cardhead">♙ &nbsp; {safe(pid)}</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="tp-cardsub">{safe(p["diagnosis"] or "Not classified")} · {safe(p["center"] or "Center not set")}</div>',unsafe_allow_html=True)
        with y:
            st.markdown(f'<div style="text-align:right"><span class="tp-chip">{safe(status)}</span></div>',unsafe_allow_html=True)
            st.caption(f'{follow} assessments')
            if st.button('Open →',key=f'open_{index}_{pid}'):
                go('record','Patient Information',pid)


def registry():
    top('Patient Registry',badge='Demo data')
    all_patients=db.list_patients();n,entries=db.stats()
    x,y,z=st.columns(3);x.metric('Patients',n);y.metric('Saved entries',entries);z.metric('Centers',len({p['center'] for p in all_patients if p['center']}))
    query=st.text_input('Search by ID, diagnosis or center',placeholder='Search by patient ID, diagnosis or center...',label_visibility='collapsed')
    rows=db.list_patients(query)
    if not rows:st.info('No matching patients.')
    for i,p in enumerate(rows):patient_card(p,i)


def dashboard():
    top('Dashboard',badge='Research demo')
    n,e=db.stats();patients=db.list_patients()
    a,b,c=st.columns(3);a.metric('Patients',n);b.metric('Saved entries',e);c.metric('Centers',len({p['center'] for p in patients if p['center']}))
    section_heading('Recent patient records')
    for i,p in enumerate(patients[:5]):patient_card(p,i)
    if st.button('View all patients →'):go('registry')


def new_patient():
    top('New Patient',badge='Draft')
    section_heading('Patient identification')
    with st.form('new_patient'):
        a,b=st.columns(2)
        with a:pid=st.text_input('Patient code',placeholder='DEMO-004')
        with b:center=st.text_input('Hospital / Center',placeholder='Demo center')
        diag=st.selectbox('Diagnosis',['Not recorded','MDS','AML'])
        ok=st.form_submit_button('＋  Create patient')
    if ok:
        try:
            db.create_patient(pid.strip(),center,'' if diag=='Not recorded' else diag)
            go('record','Patient Information',pid.strip())
        except Exception as e:st.error('Cannot create patient: '+str(e))


def export():
    top('Export data',badge='CSV')
    st.caption('Download research data entered in the registry. Fictional-data demo only.')
    rows=[]
    for patient in db.list_patients():
        pid=patient['patient_id'];es=db.entries(pid)
        if not es:rows.append({'patient_id':pid,'center':patient['center'],'diagnosis':patient['diagnosis']})
        for e in es:rows.append({'patient_id':pid,'center':patient['center'],'diagnosis':patient['diagnosis'],'section':e['section'],'episode':e['episode'],**e['data']})
    if rows:
        frame=pd.DataFrame(rows)
        st.download_button('⇩ Download CSV',frame.to_csv(index=False).encode('utf-8-sig'),'tp53_registry_export.csv','text/csv')
        st.dataframe(frame,use_container_width=True,hide_index=True)
    else:st.info('No saved data yet.')

view=st.session_state.view
if view=='record':patient_record()
elif view=='registry':registry()
elif view=='dashboard':dashboard()
elif view=='new':new_patient()
elif view=='timeline':
    pid=st.session_state.patient
    if pid:
        top('Patient history',pid,badge='Timeline');timeline(pid)
    else:st.info('Select a patient first.')
elif view=='export':export()
st.markdown('<div class="tp-footer">TP53 Clinical Registry · Fictional data only · No authentication · Not suitable for real clinical records</div>',unsafe_allow_html=True)
