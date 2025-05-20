import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import pytz
from docx import Document
from docx.shared import Inches
import io
from matplotlib.ticker import MaxNLocator
from github import Github
import logging

# Configure logging for Streamlit Cloud logs (not UI)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set seaborn style for professional charts
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# Set page config
st.set_page_config(page_title="Hostel Insident Verslag", layout="wide")

# Custom CSS for futuristic and professional styling
st.markdown("""
    <style>
        /* General layout */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            font-family: 'Orbitron', sans-serif;
            color: #e2e8f0;
            text-align: center;
        }
        [data-baseweb="baseweb"] {
            background: transparent !important;
        }

        /* Main content */
        .main .block-container {
            padding: 40px;
            background: rgba(15, 23, 42, 0.9);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 229, 255, 0.2);
            margin-bottom: 30px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
            backdrop-filter: blur(10px);
        }
        .main .block-container:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0, 229, 255, 0.3);
        }

        /* Headers */
        h1 {
            color: #00e5ff;
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 25px;
            text-align: center;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
        }
        h2 {
            color: #38bdf8;
            font-size: 2.2rem;
            font-weight: 600;
            margin-top: 30px;
            margin-bottom: 20px;
            border-bottom: 3px solid #0ea5e9;
            padding-bottom: 8px;
            text-align: center;
        }
        h3 {
            color: #38bdf8;
            font-size: 1.6rem;
            font-weight: 500;
            margin-bottom: 15px;
            text-align: center;
        }

        /* Input labels */
        .input-label {
            color: #38bdf8;
            font-size: 1.2rem;
            font-weight: 500;
            margin-bottom: 10px;
            display: block;
            text-align: center;
        }

        /* Buttons */
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(45deg, #0ea5e9, #38bdf8);
            color: #ffffff !important;
            border: none;
            border-radius: 12px;
            padding: 12px 20px;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            max-width: 250px;
            width: 100%;
            margin: 10px auto;
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.5);
            text-align: center;
            display: block;
        }
        .stButton>button:hover, .stDownloadButton>button:hover {
            background: linear-gradient(45deg, #0284c7, #0ea5e9);
            transform: translateY(-2px);
            box-shadow: 0 0 20px rgba(14, 165, 233, 0.7);
        }
        .stButton>button:active, .stDownloadButton>button:active {
            background: linear-gradient(45deg, #0369a1, #0284c7);
            transform: translateY(0);
        }
        .stButton>button:disabled, .stDownloadButton>button:disabled {
            background: #475569;
            color: #94a3b8 !important;
            box-shadow: none;
        }

        /* Delete button */
        .stButton>button.delete-button {
            background: linear-gradient(45deg, #ef4444, #f87171);
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.5);
        }
        .stButton>button.delete-button:hover {
            background: linear-gradient(45deg, #dc2626, #ef4444);
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.7);
        }
        .stButton>button.delete-button:active {
            background: linear-gradient(45deg, #b91c1c, #dc2626);
        }

        /* Download button */
        .stDownloadButton>button {
            background: linear-gradient(45deg, #10b981, #34d399);
        }
        .stDownloadButton>button:hover {
            background: linear-gradient(45deg, #059669, #10b981);
        }
        .stDownloadButton>button:active {
            background: linear-gradient(45deg, #047857, #059669);
        }

        /* Dataframe styling */
        .stDataFrame {
            border: 1px solid #0ea5e9;
            border-radius: 12px;
            overflow-x: auto;
            background: rgba(30, 41, 59, 0.8);
            max-width: 1200px;
            margin: 0 auto;
        }
        .stDataFrame table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }
        .stDataFrame th {
            background: #1e293b;
            color: #38bdf8;
            font-weight: 600;
            padding: 15px;
            text-align: left;
            font-size: 1rem;
            border-bottom: 2px solid #0ea5e9;
        }
        .stDataFrame td {
            padding: 15px;
            border-bottom: 1px solid #334155;
            color: #e2e8f0;
            font-size: 0.95rem;
        }
        .stDataFrame tr:nth-child(even) {
            background: rgba(51, 65, 85, 0.3);
        }
        .stDataFrame tr:hover {
            background: rgba(14, 165, 233, 0.2);
        }

        /* Selectbox */
        .stSelectbox {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid #0ea5e9;
            border-radius: 10px;
            padding: 12px;
            font-size: 1rem;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            max-width: 500px;
            width: 100%;
            margin: 10px auto;
            display: block;
            box-shadow: 0 0 10px rgba(14, 165, 233, 0.3);
        }
        .stSelectbox:hover {
            border-color: #38bdf8;
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.5);
        }
        .stSelectbox > div > div {
            min-height: 48px;
            color: #00e5ff !important;
            background: rgba(15, 23, 42, 0.9);
        }
        .stSelectbox [data-baseweb="select"] ul {
            background: #1e293b !important;
            border: 1px solid #0ea5e9 !important;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 229, 255, 0.2);
        }
        .stSelectbox [data-baseweb="select"] li {
            color: #e2e8f0 !important;
            padding: 10px;
            transition: background 0.2s ease;
        }
        .stSelectbox [data-baseweb="select"] li:hover {
            background: #0ea5e9 !important;
            color: #ffffff !important;
        }
        .stSelectbox [data-baseweb="select"] li[aria-selected="true"] {
            background: #38bdf8 !important;
            color: #ffffff !important;
            font-weight: 600;
        }

        /* Text area */
        .stTextArea {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid #0ea5e9;
            border-radius: 10px;
            padding: 12px;
            font-size: 1rem;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            max-width: 500px;
            width: 100%;
            margin: 10px auto;
            display: block;
            box-shadow: 0 0 10px rgba(14, 165, 233, 0.3);
            color: #e2e8f0;
        }
        .stTextArea:hover {
            border-color: #38bdf8;
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.5);
        }

        /* Tabs */
        .stTabs {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            background: #1e293b;
            border-radius: 10px 10px 0 0;
            padding: 12px 24px;
            font-size: 1rem;
            color: #38bdf8;
            margin-right: 6px;
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background: #334155;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #0ea5e9;
            color: #ffffff;
            font-weight: 600;
        }

        /* Charts */
        .stPyplot {
            border-radius: 12px;
            padding: 15px;
            background: rgba(15, 23, 42, 0.9);
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.3);
            max-width: 700px;
            margin: 0 auto;
        }

        /* Separator */
        .custom-divider {
            border-top: 5px solid #0ea5e9;
            margin: 40px auto;
            max-width: 900px;
            border-radius: 2px;
        }

        /* Notification */
        .notification-container > div {
            background: rgba(239, 68, 68, 0.2) !important;
            border: 2px solid #ef4444 !important;
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
        }
        .notification-container > div > h4 {
            color: #f87171 !important;
            text-shadow: 0 0 5px rgba(239, 68, 68, 0.5);
        }
        .notification-container > div > p {
            color: #e2e8f0 !important;
        }

        /* Mobile optimization */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 12px;
            }
            h1 {
                font-size: 2.2rem;
                margin-bottom: 20px;
            }
            h2 {
                font-size: 1.8rem;
                margin-top: 20px;
                margin-bottom: 15px;
            }
            h3 {
                font-size: 1.4rem;
                margin-bottom: 12px;
            }
            .input-label {
                font-size: 1.1rem;
                margin-bottom: 8px;
            }
            .stButton>button, .stDownloadButton>button {
                padding: 10px 16px;
                font-size: 0.95rem;
                max-width: 200px;
                margin: 8px auto;
                border-radius: 8px;
            }
            .stSelectbox, .stTextArea {
                font-size: 0.95rem;
                padding: 10px;
                max-width: 90%;
                margin: 8px auto;
                border-radius: 8px;
            }
            .stDataFrame {
                max-width: 100%;
                font-size: 0.9rem;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 10px 16px;
                font-size: 0.95rem;
                margin-bottom: 5px;
                border-radius: 8px;
                flex: 1 1 auto;
                text-align: center;
            }
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Load and preprocess learner data
@st.cache_data
def load_learner_data():
    try:
        df = pd.read_csv("learner_list.csv")
        df.columns = df.columns.str.strip()
        df['Learner_Full_Name'] = (df['Leerder van'].fillna('') + ' ' + df['Leerner se naam'].fillna('')).str.strip()
        df = df.rename(columns={
            'BLOK': 'Block',
            'Opvoeder betrokke': 'Teacher',
            'Wat het gebeur': 'Incident',
            'Kategorie': 'Category'
        })
        df['Learner_Full_Name'] = df['Learner_Full_Name'].replace('', 'Onbekend2999')
        df['Block'] = df['Block'].fillna('Onbekend2999')
        df['Teacher'] = df['Teacher'].fillna('Onbekend2999')
        df['Incident'] = df['Incident'].fillna('Onbekend2999')
        df['Category'] = pd.to_numeric(df['Category'], errors='coerce').fillna(1).astype(int).astype(str)
        return df[['Learner_Full_Name', 'Block', 'Teacher', 'Incident', 'Category']]
    except FileNotFoundError:
        logger.warning("learner_list.csv not found. Returning empty DataFrame.")
        return pd.DataFrame(columns=['Learner_Full_Name', 'Block', 'Teacher', 'Incident', 'Category'])

# Load or initialize incident log
def load_incident_log():
    try:
        df = pd.read_csv("incident_log.csv")
        df.columns = df.columns.str.strip()
        column_mapping = {
            'BLOK': 'Block',
            'Opvoeder betrokke': 'Teacher',
            'Wat het gebeur': 'Incident',
            'Kategorie': 'Category',
            'Leerder Naam': 'Learner_Full_Name',
            'Kommentaar': 'Comment',
            'Datum': 'Date'
        }
        df = df.rename(columns=column_mapping)
        expected_columns = ['Learner_Full_Name', 'Block', 'Teacher', 'Incident', 'Category', 'Comment', 'Date']
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 'Onbekend2999' if col != 'Date' else pd.NaT
        df['Category'] = pd.to_numeric(df['Category'], errors='coerce').fillna(1).astype(int).astype(str)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        return df[expected_columns]
    except (FileNotFoundError, pd.errors.EmptyDataError):
        logger.warning("incident_log.csv not found or empty. Returning empty DataFrame.")
        return pd.DataFrame(columns=['Learner_Full_Name', 'Block', 'Teacher', 'Incident', 'Category', 'Comment', 'Date'])

# Save incident to log
def save_incident(learner_full_name, block, teacher, incident, category, comment):
    if not all([learner_full_name != 'Kies', block != 'Kies', teacher != 'Kies', incident != 'Kies', category != 'Kies', comment]):
        logger.warning("Incomplete incident fields, saving skipped.")
        st.warning("Alle velde moet ingevul wees om die insident te stoor.")
        return load_incident_log()
        
    incident_log = load_incident_log()
    sa_tz = pytz.timezone('Africa/Johannesburg')
    new_incident = pd.DataFrame({
        'Learner_Full_Name': [learner_full_name],
        'Block': [block],
        'Teacher': [teacher],
        'Incident': [incident],
        'Category': [category],
        'Comment': [comment],
        'Date': [datetime.now(sa_tz).date()]
    })
    incident_log = pd.concat([incident_log, new_incident], ignore_index=True)
    incident_log.to_csv("incident_log.csv", index=False)
    logger.info("Incident saved locally to incident_log.csv")
    
    # Push to GitHub
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("arnoldtRealph/insident")
        with open("incident_log.csv", "rb") as file:
            content = file.read()
        repo_path = "incident_log.csv"
        try:
            contents = repo.get_contents(repo_path, ref="master")
            repo.update_file(
                path=repo_path,
                message="Updated incident_log.csv with new incident",
                content=content,
                sha=contents.sha,
                branch="master"
            )
            st.success("Incident log updated on GitHub!")
        except:
            repo.create_file(
                path=repo_path,
                message="Created incident_log.csv with new incident",
                content=content,
                branch="master"
            )
            st.success("Incident log created on GitHub!")
    except Exception as e:
        st.error(f"Kon nie na GitHub stoot nie: {e}")
        logger.error(f"GitHub push failed: {str(e)}")
    
    return incident_log

# Remove incident from log
def remove_incident(display_index):
    incident_log = load_incident_log()
    internal_index = display_index - 1
    if internal_index in incident_log.index:
        incident_log = incident_log.drop(internal_index).reset_index(drop=True)
        incident_log.to_csv("incident_log.csv", index=False)
        logger.info(f"Incident at index {display_index} removed locally")
        
        # Push to GitHub
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("arnoldtRealph/insident")
            with open("incident_log.csv", "rb") as file:
                content = file.read()
            repo_path = "incident_log.csv"
            try:
                contents = repo.get_contents(repo_path, ref="master")
                repo.update_file(
                    path=repo_path,
                    message="Updated incident_log.csv after removing incident",
                    content=content,
                    sha=contents.sha,
                    branch="master"
                )
                st.success("Incident log updated on GitHub!")
            except:
                repo.create_file(
                    path=repo_path,
                    message="Created incident_log.csv after removing incident",
                    content=content,
                    branch="master"
                )
                st.success("Incident log created on GitHub!")
        except Exception as e:
            st.error(f"Kon nie na GitHub stoot nie: {e}")
            logger.error(f"GitHub push failed: {str(e)}")
        
        return incident_log
    else:
        logger.warning(f"Invalid index {display_index} for removal")
        st.warning(f"Ongeldige indeks {display_index} vir verwydering.")
    return incident_log

# Generate Word document for all incidents
def generate_word_report(df):
    doc = Document()
    doc.add_heading('Hostel Insident Verslag', 0)

    doc.add_heading('Insident Besonderhede', level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.cell(0, i).text = {
            'Learner_Full_Name': 'Leerder Naam',
            'Block': 'Blok',
            'Teacher': 'Toesighouer',
            'Incident': 'Insident',
            'Category': 'Kategorie',
            'Comment': 'Kommentaar',
            'Date': 'Datum'
        }.get(col, col)
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, col in enumerate(df.columns):
            cells[i].text = str(row[col]) if col != 'Date' else row[col].strftime("%Y-%m-%d") if pd.notnull(row[col]) else 'Onbekend2999'

    doc.add_heading('Insident Analise', level=1)

    # Bar chart: Incidents by Category
    fig, ax = plt.subplots(figsize=(4, 2.5))
    category_counts = df['Category'].value_counts().sort_index()
    sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette='Blues')
    ax.set_title('Insidente volgens Kategorie', pad=10, fontsize=12, weight='bold')
    ax.set_xlabel('Kategorie', fontsize=10)
    ax.set_ylabel('Aantal', fontsize=10)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout(pad=1.0)
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    doc.add_picture(img_stream, width=Inches(3.5))

    # Bar chart: Incidents by Block
    if 'Block' in df.columns:
        fig, ax = plt.subplots(figsize=(4, 2.5))
        block_counts = df['Block'].value_counts()
        sns.barplot(x=block_counts.index, y=block_counts.values, ax=ax, palette='Blues')
        ax.set_title('Insidente volgens Blok', pad=10, fontsize=12, weight='bold')
        ax.set_xlabel('Blok', fontsize=10)
        ax.set_ylabel('Aantal', fontsize=10)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.tick_params(axis='x', rotation=45, labelsize=9)
        plt.tight_layout(pad=1.0)
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        doc.add_picture(img_stream, width=Inches(3.5))
    else:
        doc.add_paragraph('Geen Blok-data beskikbaar vir analise nie.')

    doc_stream = io.BytesIO()
    doc.save(doc_stream)
    doc_stream.seek(0)
    return doc_stream

# Load data
learner_df = load_learner_data()
incident_log = load_incident_log()

# Main content
with st.container():
    st.title("HOSTEL INSIDENT VERSLAG")
    st.subheader("Hoërskool Saul Damon Hostel")

# Initialize session state for sanction notifications
if 'sanction_popups' not in st.session_state:
    st.session_state.sanction_popups = {}

# Compute sanctions based on incident counts
if not incident_log.empty:
    tally_df = incident_log.pivot_table(
        index='Learner_Full_Name',
        columns='Category',
        values='Incident',
        aggfunc='count',
        fill_value=0
    )
    for cat in ['1', '2', '3', '4']:
        if cat not in tally_df.columns:
            tally_df[cat] = 0
    tally_df = tally_df[['1', '2', '3', '4']].reset_index()

    sanctions = []
    for _, row in tally_df.iterrows():
        learner = row['Learner_Full_Name']
        if row['1'] > 5:
            sanctions.append({
                'Learner': learner,
                'Category': '1',
                'Count': int(row['1']),
                'Sanction': 'Waarskuwing en ouerberaad met hosteltoesighouer.'
            })
        if row['2'] > 3:
            sanctions.append({
                'Learner': learner,
                'Category': '2',
                'Count': int(row['2']),
                'Sanction': 'Tydelike verbod op hostelaktiwiteite.'
            })
        if row['3'] > 2:
            sanctions.append({
                'Learner': learner,
                'Category': '3',
                'Count': int(row['3']),
                'Sanction': 'Ouers moet afspraak maak met hostelbestuur.'
            })
        if row['4'] >= 1:
            sanctions.append({
                'Learner': learner,
                'Category': '4',
                'Count': int(row['4']),
                'Sanction': 'Verwysing na dissiplinêre komitee.'
            })

    sanctions_df = pd.DataFrame(sanctions)

    for _, row in sanctions_df.iterrows():
        key = f"{row['Learner']}_{row['Category']}"
        if key not in st.session_state.sanction_popups:
            st.session_state.sanction_popups[key] = True

    st.markdown('<div class="notification-container">', unsafe_allow_html=True)
    any_notifications = False
    for _, row in sanctions_df.iterrows():
        key = f"{row['Learner']}_{row['Category']}"
        if st.session_state.sanction_popups.get(key, False):
            any_notifications = True
            st.markdown(
                f"""
                <div style='padding: 15px; border-radius: 8px;'>
                    <h4 style='margin: 0;'>SANKSIEMELDING</h4>
                    <p style='margin: 5px 0; font-size: 0.9rem;'>
                        Leerder <strong>{row['Learner']}</strong> het {row['Count']} Kategorie {row['Category']} insidente. 
                        Sanksie: {row['Sanction']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Opgelos", key=f"sanction_resolve_{key}"):
                st.session_state.sanction_popups[key] = False
                st.rerun()
    if not any_notifications:
        st.markdown(
            """
            <div style='background: rgba(34, 197, 94, 0.2); padding: 15px; border-radius: 8px; border: 2px solid #34d399;'>
                <p style='margin: 0; font-size: 0.9rem;'>Geen aktiewe sanksiemeldings nie.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# Report new incident
st.header("Rapporteer Nuwe Insident")
with st.container():
    st.markdown('<div class="input-label">Leerder Naam</div>', unsafe_allow_html=True)
    learner_full_name = st.selectbox("", options=['Kies'] + sorted(learner_df['Learner_Full_Name'].unique()), key="learner_full_name")
    
    st.markdown('<div class="input-label">Blok</div>', unsafe_allow_html=True)
    block = st.selectbox("", options=['Kies'] + sorted(learner_df['Block'].unique()), key="block")
    
    st.markdown('<div class="input-label">Toesighouer</div>', unsafe_allow_html=True)
    teacher = st.selectbox("", options=['Kies'] + sorted(learner_df['Teacher'].unique()), key="teacher")
    
    st.markdown('<div class="input-label">Insident</div>', unsafe_allow_html=True)
    incident = st.selectbox("", options=['Kies'] + sorted(learner_df['Incident'].unique()), key="incident")
    
    st.markdown('<div class="input-label">Kategorie</div>', unsafe_allow_html=True)
    category = st.selectbox("", options=['Kies', '1', '2', '3', '4'], key="category")
    
    st.markdown('<div class="input-label">Kommentaar</div>', unsafe_allow_html=True)
    comment = st.text_area("", placeholder="Tik hier...", key="comment")
    
    if st.button("Stoor Insident"):
        incident_log = save_incident(learner_full_name, block, teacher, incident, category, comment)
        st.success("Insident suksesvol gestoor!")

# Incident log display
st.header("Insident Log")
if not incident_log.empty:
    # Create a display DataFrame with 1-based index
    display_log = incident_log.copy()
    display_log.index = display_log.index + 1
    st.dataframe(
        display_log,
        use_container_width=True,
        column_config={
            "Learner_Full_Name": st.column_config.TextColumn("Leerder Naam", width="medium"),
            "Block": st.column_config.TextColumn("Blok", width="small"),
            "Teacher": st.column_config.TextColumn("Toesighouer", width="medium"),
            "Incident": st.column_config.TextColumn("Insident", width="medium"),
            "Category": st.column_config.TextColumn("Kategorie", width="small"),
            "Comment": st.column_config.TextColumn("Kommentaar", width="large"),
            "Date": st.column_config.DateColumn("Datum", width="medium", format="YYYY-MM-DD")
        }
    )
    
    # Remove incident section
    st.subheader("Verwyder Insident")
    incident_index = st.number_input("Voer die indeks van die insident in om te verwyder", min_value=1, max_value=len(incident_log), step=1)
    if st.button("Verwyder Insident", key="remove_incident", help="Klik om die geselekteerde insident te verwyder"):
        incident_log = remove_incident(incident_index)
        st.success(f"Insident by indeks {incident_index} suksesvol verwyder!")
        st.rerun()
    
    st.download_button(
        label="Laai Verslag af as Word",
        data=generate_word_report(incident_log),
        file_name="hostel_insident_verslag.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
else:
    st.write("Geen insidente in die log nie.")

# Today's incidents
st.header("Vandag se Insidente")
today = datetime.now(pytz.timezone('Africa/Johannesburg')).date()
today_incidents = incident_log[incident_log['Date'] == today]
if not today_incidents.empty:
    st.write(f"Totale Insidente Vandag: {len(today_incidents)}")
    fig, ax = plt.subplots(figsize=(4, 2.5))
    category_counts = today_incidents['Category'].value_counts().sort_index()
    sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax, palette='Blues')
    ax.set_title('Insidente volgens Kategorie (Vandag)', pad=10, fontsize=12, weight='bold')
    ax.set_xlabel('Kategorie', fontsize=10)
    ax.set_ylabel('Aantal', fontsize=10)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout(pad=1.0)
    st.pyplot(fig)
    plt.close()
else:
    st.write("Geen insidente vandag gerapporteer nie.")
