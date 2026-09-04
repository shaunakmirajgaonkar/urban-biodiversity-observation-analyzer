from __future__ import annotations

from pathlib import Path
import base64

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from biodiversity_engine import (
    OBS_REQUIRED, HAB_REQUIRED, biodiversity_kpis, calculate_observation_risk,
    habitat_summary, monthly_trend, scenario_projection, species_summary,
    validate_habitats, validate_observations,
)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
ASSETS = ROOT / 'assets'

st.set_page_config(page_title='UrbanBioTrack | Biodiversity Observation Analyzer', page_icon='🌿', layout='wide', initial_sidebar_state='expanded')

st.markdown('''
<style>
:root { --ink:#16324f; --muted:#5f7185; --green:#16a66a; --mint:#e9f9f1; --blue:#2f80ed; --orange:#f2994a; --purple:#8b5cf6; --pink:#ef5da8; }
[data-testid="stAppViewContainer"] { background: linear-gradient(180deg,#f7fbff 0%,#f4fbf7 45%,#f7f9fc 100%); color:var(--ink); }
[data-testid="stHeader"] { background: rgba(255,255,255,.78); }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#ffffff 0%,#eefaf4 100%); border-right:1px solid #dfe8e3; }
.block-container { padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1600px; }
.smallcap { font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; color:#6c7d90; font-weight:700; }
.hero { background: linear-gradient(120deg,#ffffff 0%,#edfbf4 50%,#eef5ff 100%); border:1px solid #dbeee4; border-radius:24px; padding:1.25rem 1.45rem; box-shadow:0 12px 30px rgba(24,54,87,.06); }
.hero h1 { margin:.1rem 0 .25rem; font-size:2.1rem; color:#13395f; }
.hero p { margin:0; color:#60758a; }
.badge { display:inline-block; padding:.32rem .65rem; border-radius:999px; font-weight:800; font-size:.74rem; margin-right:.35rem; }
.b1 { background:#e3f8ec; color:#137b4b; } .b2{ background:#e8f0ff;color:#2764c0;} .b3{background:#fff0e2;color:#b65e12;} .b4{background:#f0e9ff;color:#7044be;}
.kpi { border-radius:18px; padding:1rem 1.05rem; border:1px solid rgba(0,0,0,.06); box-shadow:0 9px 24px rgba(24,54,87,.05); min-height:120px; }
.kpi h3{margin:0;font-size:.83rem;color:#617287}.kpi .v{font-size:1.8rem;font-weight:800;color:#153b61;margin:.35rem 0}.kpi .delta{font-size:.75rem;font-weight:700;color:#1f9961}
.card { background:#fff;border:1px solid #e1e9ef;border-radius:18px;padding:1rem 1.1rem;box-shadow:0 9px 24px rgba(31,55,78,.05); }
.section-title { font-size:1.15rem; font-weight:800; color:#163b61; margin:.1rem 0 .75rem; }
.insight { background:linear-gradient(135deg,#ecfbf2,#f4fbff); border:1px solid #d9ece1; border-radius:16px; padding:.9rem 1rem; }
div[data-testid="stMetric"] { background:#fff; padding:.7rem .8rem; border-radius:14px; border:1px solid #e3ebf0; }
.stButton button { border-radius:12px; border:1px solid #cae4d6; }
footer {visibility:hidden;}
</style>
''', unsafe_allow_html=True)

@st.cache_data

def load_default_data():
    obs = pd.read_csv(DATA/'sample_observations.csv')
    hab = pd.read_csv(DATA/'sample_habitats.csv')
    return obs, hab

with st.sidebar:
    st.markdown('<div class="smallcap">UrbanBioTrack</div><h2 style="margin:.15rem 0 .45rem;color:#174b35">🌿 Biodiversity Intelligence</h2><div style="color:#698078;font-size:.83rem">Local-first • Private • Explainable</div>', unsafe_allow_html=True)
    page = st.radio('Workspace', ['Overview','Observation Explorer','Species Intelligence','Habitat Intelligence','Seasonal Trends','Biodiversity Map','Scenario Lab','Data Quality','Reports','About'], label_visibility='collapsed')
    st.divider()
    st.markdown('**Local data source**')
    obs_file = st.file_uploader('Observations CSV', type=['csv'], key='obs')
    hab_file = st.file_uploader('Habitats CSV', type=['csv'], key='hab')
    if obs_file and hab_file:
        obs = pd.read_csv(obs_file); hab = pd.read_csv(hab_file)
    else:
        obs, hab = load_default_data()
    st.caption('No external APIs are required. Uploaded data stays in this local app session.')

obs_errors = validate_observations(obs)
hab_errors = validate_habitats(hab)

if obs_errors or hab_errors:
    st.error('Data validation needs attention before analytics can run.')
    for e in obs_errors + hab_errors: st.write('•', e)
    st.stop()

obs_scored = calculate_observation_risk(obs)
hab_scored = habitat_summary(hab)
species = species_summary(obs_scored)
trend = monthly_trend(obs_scored)
kpis = biodiversity_kpis(obs_scored, hab_scored)

st.markdown('''<div class="hero">
<div><span class="badge b1">LOCAL-FIRST</span><span class="badge b2">CITIZEN SCIENCE</span><span class="badge b3">EXPLAINABLE</span><span class="badge b4">URBAN NATURE</span></div>
<h1>Urban Biodiversity Observation Analyzer</h1>
<p>Track local biodiversity change through citizen observations, habitat signals, images and seasonality — with transparent analytics and review-ready insights.</p>
</div>''', unsafe_allow_html=True)

if page == 'Overview':
    st.write('')
    if (ASSETS/'nature_header.svg').exists():
        st.image(str(ASSETS/'nature_header.svg'), use_container_width=True)
    cols = st.columns(5)
    k = [('Observations',kpis['observations'],'+ live records'),('Unique species',kpis['species'],'catalogued locally'),('Habitats',kpis['habitats'],'sampled areas'),('Contributors',kpis['contributors'],'unique observer IDs'),('Images',kpis['images'],'evidence files')]
    fills = ['#effbf4','#eef5ff','#fff4ea','#f4efff','#fff0f5']
    for idx,(c,(lab,val,delta)) in enumerate(zip(cols,k)):
        with c: st.markdown(f'<div class="kpi" style="background:{fills[idx]}"><h3>{lab}</h3><div class="v">{val:,}</div><div class="delta">{delta}</div></div>',unsafe_allow_html=True)
    st.write('')
    a,b = st.columns([1.45,1])
    with a:
        st.markdown('<div class="card"><div class="section-title">📈 Observation activity over time</div>',unsafe_allow_html=True)
        if not trend.empty:
            fig = px.line(trend, x='month', y='observations', color='species_category', markers=True, template='plotly_white')
            fig.update_layout(height=355, margin=dict(l=10,r=10,t=20,b=10), legend_title_text='Category')
            fig.update_yaxes(title='Observations'); fig.update_xaxes(title='Month')
            st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
        st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="card"><div class="section-title">🧬 Species category mix</div>',unsafe_allow_html=True)
        cat = obs_scored.groupby('species_category').size().reset_index(name='observations').sort_values('observations',ascending=False)
        fig = px.pie(cat,names='species_category',values='observations',hole=.55,template='plotly_white')
        fig.update_layout(height=355,margin=dict(l=5,r=5,t=15,b=5),legend_title_text='')
        st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
        st.markdown('</div>',unsafe_allow_html=True)
    c,d = st.columns([1,1.2])
    with c:
        st.markdown('<div class="card"><div class="section-title">🏆 Most observed species</div>',unsafe_allow_html=True)
        top = species.head(7)[['species_common_name','species_category','observations','attention_score']]
        st.dataframe(top,hide_index=True,use_container_width=True,column_config={'attention_score':st.column_config.NumberColumn('Attention',format='%.1f')})
        st.markdown('</div>',unsafe_allow_html=True)
    with d:
        st.markdown('<div class="card"><div class="section-title">🌳 Habitat support vs pressure</div>',unsafe_allow_html=True)
        hfig = px.scatter(hab_scored,x='biodiversity_support_score',y='pressure_score',size='area_hectares',color='habitat_type',hover_name='habitat_name',template='plotly_white')
        hfig.add_vline(x=60,line_dash='dot'); hfig.add_hline(y=50,line_dash='dot')
        hfig.update_layout(height=325,margin=dict(l=10,r=10,t=20,b=10),xaxis_title='Biodiversity support score',yaxis_title='Pressure score')
        st.plotly_chart(hfig,use_container_width=True,config={'displayModeBar':False})
        st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="insight">💡 <b>Reading the dashboard:</b> attention scores are screening signals for where observations or habitat conditions may deserve review; they are not ecological health certificates.</div>',unsafe_allow_html=True)

elif page == 'Observation Explorer':
    st.markdown('<div class="section-title">🔎 Observation Explorer</div>',unsafe_allow_html=True)
    f1,f2,f3 = st.columns(3)
    with f1: category = st.multiselect('Species category',sorted(obs_scored.species_category.unique()),default=sorted(obs_scored.species_category.unique()))
    with f2: season = st.multiselect('Season',sorted(obs_scored.season.unique()),default=sorted(obs_scored.season.unique()))
    with f3: band = st.multiselect('Attention band',['Low','Moderate','High','Critical'],default=['Low','Moderate','High','Critical'])
    view = obs_scored[obs_scored.species_category.isin(category)&obs_scored.season.isin(season)&obs_scored.risk_band.astype(str).isin(band)]
    st.write(f'**{len(view):,}** matching observations')
    st.dataframe(view.sort_values('attention_score',ascending=False),hide_index=True,use_container_width=True,column_config={'attention_score':st.column_config.ProgressColumn('Attention score',min_value=0,max_value=100,format='%.1f')})
    fig = px.scatter(view,x='observed_at',y='attention_score',color='species_category',size='image_count',hover_name='species_common_name',template='plotly_white')
    fig.update_layout(height=360,xaxis_title='Date',yaxis_title='Attention score')
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})

elif page == 'Species Intelligence':
    st.markdown('<div class="section-title">🦋 Species Intelligence</div>',unsafe_allow_html=True)
    s1,s2 = st.columns([1.3,1])
    with s1:
        fig = px.bar(species.head(15).sort_values('observations'),x='observations',y='species_common_name',color='species_category',orientation='h',template='plotly_white')
        fig.update_layout(height=520,xaxis_title='Observation count',yaxis_title='')
        st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    with s2:
        sel = st.selectbox('Inspect species',species.species_common_name.tolist())
        row = species[species.species_common_name==sel].iloc[0]
        st.metric('Observations',int(row.observations)); st.metric('Total abundance',int(row.total_abundance)); st.metric('Attention',float(row.attention_score))
        st.write(f"**Category:** {row.species_category}")
        st.write(f"**Average confidence:** {row.avg_confidence:.1f}%")
        st.write(f"**Average habitat quality:** {row.avg_habitat_quality:.1f}/100")
        st.write(f"**Average disturbance:** {row.avg_disturbance:.1f}/100")
        st.markdown('<div class="insight">Use species-level signals to focus verification and habitat review, not to infer population viability from observation counts alone.</div>',unsafe_allow_html=True)
    st.dataframe(species,hide_index=True,use_container_width=True)

elif page == 'Habitat Intelligence':
    st.markdown('<div class="section-title">🌳 Habitat Intelligence</div>',unsafe_allow_html=True)
    fig = px.bar(hab_scored.sort_values('biodiversity_support_score'),x='biodiversity_support_score',y='habitat_name',color='habitat_type',orientation='h',template='plotly_white')
    fig.update_layout(height=450,xaxis_title='Support score',yaxis_title='Habitat')
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    st.dataframe(hab_scored.sort_values('pressure_score',ascending=False),hide_index=True,use_container_width=True)

elif page == 'Seasonal Trends':
    st.markdown('<div class="section-title">🌦️ Seasonal & Monthly Trends</div>',unsafe_allow_html=True)
    seasonal = obs_scored.groupby(['season','species_category']).size().reset_index(name='observations')
    fig = px.density_heatmap(seasonal,x='season',y='species_category',z='observations',text_auto=True,color_continuous_scale='YlGn',template='plotly_white')
    fig.update_layout(height=400)
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    st.dataframe(seasonal.sort_values('observations',ascending=False),hide_index=True,use_container_width=True)

elif page == 'Biodiversity Map':
    st.markdown('<div class="section-title">📍 Biodiversity Observation Map</div>',unsafe_allow_html=True)
    mf1,mf2 = st.columns([1,2])
    with mf1: map_cat = st.multiselect('Category',sorted(obs_scored.species_category.unique()),default=sorted(obs_scored.species_category.unique()))
    with mf2: show_n = st.slider('Maximum points',20,500,min(250,len(obs_scored)))
    m = obs_scored[obs_scored.species_category.isin(map_cat)].head(show_n)
    fig = px.scatter_geo(m,lat='latitude',lon='longitude',color='species_category',size='image_count',hover_name='species_common_name',hover_data=['habitat_type','season','attention_score'],projection='natural earth',template='plotly_white')
    fig.update_geos(showland=True,landcolor='#eef8ef',showocean=True,oceancolor='#edf5ff',showcountries=True,countrycolor='#d7e0e7')
    fig.update_layout(height=610,margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
    st.caption('Coordinates are used only to visualize the locally supplied records. No external map tiles or geocoding APIs are called.')

elif page == 'Scenario Lab':
    st.markdown('<div class="section-title">🧪 Scenario Lab</div>',unsafe_allow_html=True)
    st.write('Explore how broad operational changes could shift the screening signal. This is a planning sandbox, not a predictive ecological model.')
    c1,c2,c3 = st.columns(3)
    with c1: disturbance = st.slider('Change in disturbance pressure',-30,30,0)
    with c2: habitat = st.slider('Change in habitat quality',-30,30,0)
    with c3: confidence = st.slider('Change in observation confidence',-30,30,0)
    result = scenario_projection(obs_scored,disturbance,habitat,confidence)
    a,b,c = st.columns(3)
    a.metric('Baseline attention',result['baseline'])
    b.metric('Projected attention',result['projected'],delta=round(result['projected']-result['baseline'],1))
    c.metric('Projected band',result['band'])
    st.markdown('<div class="insight">🌱 Scenario values are intentionally transparent adjustments to the screening signal so users can understand sensitivity without treating the result as a forecast.</div>',unsafe_allow_html=True)

elif page == 'Data Quality':
    st.markdown('<div class="section-title">✅ Data Quality Center</div>',unsafe_allow_html=True)
    checks = [
        ('Observation schema',not obs_errors,'Required fields present'),('Habitat schema',not hab_errors,'Required fields present'),
        ('Observation IDs unique',not obs.observation_id.duplicated().any(),'Primary key uniqueness'),('Habitat IDs unique',not hab.habitat_id.duplicated().any(),'Primary key uniqueness'),
        ('Coordinates present',obs.latitude.notna().all() and obs.longitude.notna().all(),'Latitude/longitude completeness'),('Dates parseable',pd.to_datetime(obs.observed_at,errors='coerce').notna().all(),'Observation date parsing'),
    ]
    for name,ok,detail in checks:
        st.success(f'PASS • {name} — {detail}') if ok else st.error(f'CHECK • {name} — {detail}')
    q = pd.DataFrame({'Dataset':['Observations','Habitats'],'Rows':[len(obs),len(hab)],'Columns':[len(obs.columns),len(hab.columns)],'Missing cells':[int(obs.isna().sum().sum()),int(hab.isna().sum().sum())]})
    st.dataframe(q,hide_index=True,use_container_width=True)

elif page == 'Reports':
    st.markdown('<div class="section-title">📄 Review-ready report</div>',unsafe_allow_html=True)
    high = obs_scored[obs_scored.risk_band.astype(str).isin(['High','Critical'])]
    st.write(f"The current dataset contains **{len(high)} observations** in High/Critical attention bands.")
    report = f'''URBAN BIODIVERSITY OBSERVATION ANALYZER\nGenerated locally\n\nObservations: {len(obs)}\nUnique species: {obs.species_common_name.nunique()}\nHabitats: {hab.habitat_id.nunique()}\nContributors: {obs.observer_id.nunique()}\nImages: {int(obs.image_count.sum())}\nAverage confidence: {obs.species_confidence_pct.mean():.1f}%\nHigh/Critical observation records: {len(high)}\n\nTop observation drivers:\n{high['attention_driver'].value_counts().to_string()}\n\nThis report is a screening artifact and should be reviewed with field observations and appropriate ecological expertise.'''
    st.download_button('⬇️ Download local text report',report,file_name='urban_biodiversity_report.txt',mime='text/plain')
    st.code(report,language='text')

elif page == 'About':
    st.markdown('<div class="section-title">🌿 About UrbanBioTrack</div>',unsafe_allow_html=True)
    img = ASSETS/'dashboard_preview.png'
    if img.exists(): st.image(str(img),use_container_width=True,caption='Local dashboard visual reference included in the project assets.')
    st.write('UrbanBioTrack is a fully local Streamlit analytics application for exploring citizen biodiversity observations, habitat conditions, seasonality and image-linked evidence.')
    st.markdown('**Privacy-first design:** no cloud APIs, no external databases, no map-token requirement and no automatic upload of observation records.')
    st.markdown('**Responsible use:** observation frequency can reflect effort, accessibility and reporting behavior; it should not be treated as a direct measure of true population size or ecological health.')
