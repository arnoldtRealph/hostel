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

# Set seaborn style for professional charts
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# Set page config
st.set_page_config(page_title="Hostel Insident Verslag", layout="wide")

# Custom CSS for professional styling and mobile responsiveness
st.markdown("""
    <style>
        /* General layout */
        .stApp {
            background-color: #f5f7fa;
            font-family: 'Roboto', sans-serif;
            color: #333333;
            text-align: center;
        }
        [data-baseweb="baseweb"] {
            background-color: #f5f7fa !important;
        }

        /* Dark mode adjustments */
        [data-theme="dark"] .stApp, [data-theme="dark"] [data-baseweb="baseweb"] {
            background-color: #1a1d21 !important;
            color: #e0e0e0 !important;
        }
        [data-theme="dark"] .main .block-container {
            background-color: #2a2e34 !important;
            color: #e0e0e0 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }
        [data-theme="dark"] .stMarkdown, [data-theme="dark"] .stText, 
        [data-theme="dark"] h1, [data-theme="dark"] h2, [data-theme="dark"] h3 {
            color: #e0e0e0 !important;
        }

        /* Main content */
        .main .block-container {
            padding: 40px;
            background-color: #ffffff;
            border-radius: 16px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
        }
        .main .block-container:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }

        /* Headers */
        h1 {
            color: #1a3c34;
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 25px;
            text-align: center;
            letter-spacing: 0.5px;
        }
        h2 {
            color: #2e5a52;
            font-size: 2rem;
            font-weight: 600;
            margin-top: 30px;
            margin-bottom: 20px;
            border-bottom: 3px solid #e0e6ed;
            padding-bottom: 8px;
            text-align: center;
        }
        h3 {
            color: #2e5a52;
            font-size: 1.5rem;
            font-weight: 500;
            margin-bottom: 15px;
            text-align: center;
        }

        /* Input labels */
        .input-label {
            color: #2e5a52;
            font-size: 1.2rem;
            font-weight: 500;
            margin-bottom: 10px;
            display: block;
            text-align: center;
        }
        [data-theme="dark"] .input-label {
            color: #e0e0e0 !important;
        }

        /* Buttons */
        .stButton>button, .stDownloadButton>button {
            background-color: #28b463;
            color: #ffffff !important;
            border: none;
            border-radius: 10px;
            padding: 12px 20px;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
            max-width: 250px;
            width: 100%;
            margin: 10px auto;
            box-shadow: 0 3px 6px rgba(0,0,0,0.1);
            text-align: center;
            display: block;
        }
        .stButton>button:hover, .stDownloadButton>button:hover {
            background-color: #155e4f;
            transform: translateY(-2px);
            box-shadow: 0 5px 10px rgba(0,0,0,0.2);
        }
        .stButton>button:active, .stDownloadButton>button:active {
            background-color: #124a40;
            transform: translateY(0);
        }
        .stButton>button:disabled, .stDownloadButton>button:disabled {
            background-color: #a0a9b2;
            color: #d3d3d3 !important;
            box-shadow: none;
        }

        /* Download button specific */
        .stDownloadButton>button {
            background-color: #007bff;
        }
        .stDownloadButton>button:hover {
            background-color: #0056b3;
        }
        .stDownloadButton>button:active {
            background-color: #004085;
        }

        /* Dataframe styling */
        .stDataFrame {
            border: 1px solid #e0e6ed;
            border-radius: 12px;
            overflow-x: auto;
            background-color: #ffffff;
            max-width: 1200px;
            margin: 0 auto;
        }
        .stDataFrame table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }
        .stDataFrame th {
            background-color: #e8ecef;
            color: #1a3c34;
            font-weight: 600;
            padding: 15px;
            text-align: left;
            font-size: 1rem;
            border-bottom: 2px solid #d3dbe3;
        }
        [data-theme="dark"] .stDataFrame th {
            background-color: #3a3f46;
            color: #e0e0e0;
            border-bottom: 2px solid #4a5059;
        }
        .stDataFrame td {
            padding: 15px;
            border-bottom: 1px solid #e0e6ed;
            color: #333333;
            font-size: 0.95rem;
        }
        [data-theme="dark"] .stDataFrame td {
            color: #e0e0e0;
            border-bottom: 1px solid #4a5059;
        }
        .stDataFrame tr:nth-child(even) {
            background-color: #f9fafc;
        }
        [data-theme="dark"] .stDataFrame tr:nth-child(even) {
            background-color: #2e3238;
        }
        .stDataFrame tr:hover {
            background-color: #e8ecef;
        }
        [data-theme="dark"] .stDataFrame tr:hover {
            background-color: #3a3f46;
        }

        /* Selectbox (dropdowns) */
        .stSelectbox {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 10px;
            padding: 12px;
            font-size: 1rem;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            max-width: 500px;
            width: 100%;
            margin: 10px auto;
            display: block;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        [data-theme="dark"] .stSelectbox {
            background-color: #2e3238;
            border: 1px solid #4a5059;
            color: #e0e0e0;
        }
        .stSelectbox:hover {
            border-color: #1a3c34;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .stSelectbox > div > div {
            min-height: 48px;
        }

        /* Text area */
        .stTextArea {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 10px;
            padding: 12px;
            font-size: 1rem;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            max-width: 500px;
            width: 100%;
            margin: 10px auto;
            display: block;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        [data-theme="dark"] .stTextArea {
            background-color: #2e3238;
            border: 1px solid #4a5059;
            color: #e0e0e0;
        }
        .stTextArea:hover {
            border-color: #1a3c34;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        /* Tabs */
        .stTabs {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #e8ecef;
            border-radius: 10px 10px 0 0;
            padding: 12px 24px;
            font-size: 1rem;
            color: #2e5a52;
            margin-right: 6px;
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #d3dbe3;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #1a3c34;
            color: #ffffff;
            font-weight: 600;
        }
        [data-theme="dark"] .stTabs [data-baseweb="tab"] {
            background-color: #2e3238;
            color: #e0e0e0;
        }
        [data-theme="dark"] .stTabs [data-baseweb="tab"]:hover {
            background-color: #3a3f46;
        }
        [data-theme="dark"] .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #155e4f;
            color: #ffffff;
        }

        /* Charts */
        .stPyplot {
            border-radius: 12px;
            padding: 15px;
            background-color: #ffffff;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            max-width: 700px;
            margin: 0 auto;
        }
        [data-theme="dark"] .stPyplot {
            background-color: #2e3238;
        }

        /* Separator */
        .custom-divider {
            border-top: 5px solid #e0e6ed;
            margin: 40px auto;
            max-width: 900px;
            border-radius: 2px;
        }
        [data-theme="dark"] .custom-divider {
            border-top: 5px solid #4a5059;
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
""", unsafe_allow_html=True)

# Load and preprocess learner data
@st.cache_data
def load_learner_data():
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

# Load or initialize incident log
def load_incident_log():
    try:
        df = pd.read_csv("incident_log.csv")
        df.columns = df.columns.str.strip()
        # Standardize column names
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
        # Ensure all expected columns exist
        expected_columns = ['Learner_Full_Name', 'Block', 'Teacher', 'Incident', 'Category', 'Comment', 'Date']
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 'Onbekend2999' if col != 'Date' else pd.NaT
        df['Category'] = pd.to_numeric(df['Category'], errors='coerce').fillna(1).astype(int).astype(str)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        return df[expected_columns]
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['Learner_Full_Name', 'Block', 'Teacher', 'Incident', 'Category', 'Comment', 'Date'])

# Save incident to log
def save_incident(learner_full_name, block, teacher, incident, category, comment):
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
    return incident_log

# Clear a single incident
def clear_incident(index):
    incident_log = load_incident_log()
    if index in incident_log.index:
        incident_log = incident_log.drop(index)
        incident_log.to_csv("incident_log.csv", index=False)
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

    # Bar chart: Incidents by Block (only if Block column exists)
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
                <div style='background-color: #ffe6e6; padding: 15px; border-radius: 8px; border: 2px solid #cc0000;'>
                    <h4 style='color: #cc0000; margin: 0;'>SANKSIEMELDING</h4>
                    <p style='color: #333; margin: 5px 0; font-size: 0.9rem;'>
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
            <div style='background-color: #e6f3e6; padding: 15px; border-radius: 8px; border: 2px solid #28b463;'>
                <p style='color: #333; margin: 0; font-size: 0.9rem;'>Geen aktiewe sanksiemeldings nie.</p>
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
        if all([learner_full_name != 'Kies', block != 'Kies', teacher != 'Kies', incident != 'Kies', category != 'Kies', comment]):
            incident_log = save_incident(learner_full_name, block, teacher, incident, category, comment)
            st.success("Insident suksesvol gestoor!")
        else:
            st.error("Vul asseblief alle velde in en voer kommentaar in.")

# Incident log display
st.header("Insident Log")
if not incident_log.empty:
    st.dataframe(
        incident_log,
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