import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from docx import Document
import pytz
import io
from github import Github
import os

# Set page config
st.set_page_config(page_title="Insident Verslag", layout="wide")

# Formal CSS styling with navy blue, white, and gray
st.markdown("""
    <style>
        .stApp {
            background-color: #E6ECEF;
            font-family: 'Arial', sans-serif;
            color: #4A4A4A;
            text-align: center;
        }
        .main .block-container {
            padding: 20px;
            background-color: #FFFFFF;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 1200px;
            margin: 20px auto;
        }
        h1 {
            color: #003087;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 20px;
        }
        h2 {
            color: #003087;
            font-size: 1.8rem;
            font-weight: 600;
            margin: 20px 0;
        }
        .stButton>button, .stDownloadButton>button {
            background-color: #003087;
            color: #FFFFFF;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 1rem;
            margin: 10px auto;
            display: block;
            width: 200px;
        }
        .stButton>button:hover, .stDownloadButton>button:hover {
            background-color: #00215E;
        }
        .stSelectbox, .stTextArea {
            max-width: 400px;
            margin: 10px auto;
        }
        .stDataFrame {
            border: 1px solid #4A4A4A;
            border-radius: 8px;
            max-width: 100%;
            margin: 0 auto;
        }
        .stDataFrame th {
            background-color: #003087;
            color: #FFFFFF;
        }
        .stDataFrame td {
            color: #4A4A4A;
        }
        .input-label {
            color: #003087;
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 8px;
            display: block;
        }
        .stAlert {
            background-color: #E6ECEF;
            color: #4A4A4A;
            border: 1px solid #003087;
            border-radius: 8px;
        }
        @media (max-width: 768px) {
            .main .block-container {
                padding: 15px;
                margin: 10px;
            }
            h1 {
                font-size: 2rem;
            }
            h2 {
                font-size: 1.6rem;
            }
            .stButton>button, .stDownloadButton>button {
                width: 180px;
                font-size: 0.9rem;
            }
            .stSelectbox, .stTextArea {
                max-width: 90%;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Load learner data
@st.cache_data
def load_learner_data():
    try:
        df = pd.read_csv("learner_list.csv")
        df.columns = df.columns.str.strip()
        df['Learner_Full_Name'] = df['Leerder van'].fillna('') + ' ' + df['Leerner se naam'].fillna('')
        df['Learner_Full_Name'] = df['Learner_Full_Name'].str.strip()
        
        # Verify expected columns
        expected_columns = ['Leerder van', 'Leerner se naam', 'Geslag', 'BLOK', 'Opvoeder betrokke', 'Wat het gebeur', 'Kategorie']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            # Silently handle missing columns
            pass
        
        # Rename columns to match internal usage
        df = df.rename(columns={
            'BLOK': 'Class',  # Updated to map BLOK to Class
            'Opvoeder betrokke': 'Teacher',
            'Wat het gebeur': 'Incident',
            'Kategorie': 'Category',
            'Geslag': 'Gender'
        }, errors='ignore')
        
        # Ensure required columns exist
        for col in ['Class', 'Teacher', 'Incident', 'Category', 'Gender', 'Learner_Full_Name']:
            if col not in df.columns:
                df[col] = 'Onbekend'
        
        df['Learner_Full_Name'] = df['Learner_Full_Name'].replace('', 'Onbekend')
        df['Class'] = df['Class'].fillna('Onbekend')
        df['Teacher'] = df['Teacher'].fillna('Onbekend')
        df['Incident'] = df['Incident'].fillna('Onbekend')
        df['Category'] = pd.to_numeric(df['Category'], errors='coerce').fillna(1).astype(int).astype(str)
        df['Gender'] = df['Gender'].fillna('Onbekend')
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['Learner_Full_Name', 'Class', 'Teacher', 'Incident', 'Category', 'Gender'])

# Load or initialize incident log
@st.cache_data
def load_incident_log():
    try:
        df = pd.read_csv("incident_log.csv")
        df['Category'] = pd.to_numeric(df['Category'], errors='coerce').fillna(1).astype(int).astype(str)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['Learner_Full_Name', 'Class', 'Teacher', 'Incident', 'Category', 'Comment', 'Date'])

# Save incident to log and sync with GitHub
def save_incident(learner_full_name, class_, teacher, incident, category, comment):
    incident_log = load_incident_log()
    sa_tz = pytz.timezone('Africa/Johannesburg')
    try:
        category = str(int(float(category)))
    except ValueError:
        category = '1'
    new_incident = pd.DataFrame({
        'Learner_Full_Name': [learner_full_name],
        'Class': [class_],
        'Teacher': [teacher],
        'Incident': [incident],
        'Category': [category],
        'Comment': [comment],
        'Date': [datetime.now(sa_tz).date()]
    })
    incident_log = pd.concat([incident_log, new_incident], ignore_index=True)
    incident_log.to_csv("incident_log.csv", index=False)
    update_incident_log_in_github()  # Sync with GitHub after saving
    return incident_log

# Function to update incident_log.csv in GitHub
def update_incident_log_in_github():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("arnoldtRealph/insident")
        with open("incident_log.csv", "rb") as file:
            content = file.read()
        repo_path = "incident_log.csv"
        try:
            contents = repo.get_contents(repo_path, ref="main")
            repo.update_file(
                path=repo_path,
                message=f"Updated incident_log.csv at {datetime.now(pytz.timezone('Africa/Johannesburg')).strftime('%Y-%m-%d %H:%M:%S')}",
                content=content,
                sha=contents.sha,
                branch="main"
            )
        except:
            repo.create_file(
                path="incident_log.csv",
                message="Initial commit of incident_log.csv",
                content=content,
                branch="main"
            )
    except Exception:
        # Silently handle errors to avoid UI clutter
        pass

# Generate learner-specific Word report
def generate_learner_report(df, learner_full_name, period, start_date, end_date):
    doc = Document()
    doc.add_heading(f'Insident Verslag vir {learner_full_name}', 0)
    doc.add_paragraph(f'Tydperk: {period}')
    doc.add_paragraph(f'Datum Reeks: {start_date.strftime("%Y-%m-%d")} tot {end_date.strftime("%Y-%m-%d")}')

    doc.add_heading('Insident Besonderhede', level=1)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.cell(0, i).text = {
            'Learner_Full_Name': 'Leerder Naam',
            'Class': 'Blok',
            'Teacher': 'Onderwyser',
            'Incident': 'Insident',
            'Category': 'Kategorie',
            'Comment': 'Kommentaar',
            'Date': 'Datum'
        }.get(col, col)
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, col in enumerate(df.columns):
            if col == 'Date':
                cells[i].text = row[col].strftime("%Y-%m-%d")
            else:
                cells[i].text = str(row[col])

    doc_stream = io.BytesIO()
    doc.save(doc_stream)
    doc_stream.seek(0)
    return doc_stream

# Load data
learner_df = load_learner_data()
incident_log = load_incident_log()

# Update GitHub with the initial incident log (if it exists)
if os.path.exists("incident_log.csv"):
    update_incident_log_in_github()

# Main content
with st.container():
    st.title("HOËRSKOOL SAUL DAMON")
    st.subheader("INSIDENT VERSLAG")

    # Report New Incident Section
    st.header("Rapporteer Nuwe Insident")
    with st.container():
        st.markdown('<div class="input-label">Leerder Naam</div>', unsafe_allow_html=True)
        learner_full_name = st.selectbox("", options=['Kies'] + sorted(learner_df['Learner_Full_Name'].unique()), key="learner_full_name")
        
        st.markdown('<div class="input-label">Blok</div>', unsafe_allow_html=True)
        class_ = st.selectbox("", options=['Kies'] + sorted(learner_df['Class'].unique()), key="class")
        
        st.markdown('<div class="input-label">Onderwyser</div>', unsafe_allow_html=True)
        teacher = st.selectbox("", options=['Kies'] + sorted(learner_df['Teacher'].unique()), key="teacher")
        
        st.markdown('<div class="input-label">Insident</div>', unsafe_allow_html=True)
        incident = st.selectbox("", options=['Kies'] + sorted(learner_df['Incident'].unique()), key="incident")
        
        st.markdown('<div class="input-label">Kategorie</div>', unsafe_allow_html=True)
        category = st.selectbox("", options=['Kies'] + sorted(learner_df['Category'].unique(), key=lambda x: int(x)), key="category")
        
        st.markdown('<div class="input-label">Kommentaar</div>', unsafe_allow_html=True)
        comment = st.text_area("", placeholder="Tik hier...", key="comment")
        
        if st.button("Stoor Insident"):
            if learner_full_name != 'Kies' and class_ != 'Kies' and teacher != 'Kies' and incident != 'Kies' and category != 'Kies' and comment:
                incident_log = save_incident(learner_full_name, class_, teacher, incident, category, comment)
                st.success("Insident suksesvol gestoor!")
                st.rerun()  # Refresh to update incident log
            else:
                st.error("Vul asseblief alle velde in en voer kommentaar in.")

    # Incident Log Section
    st.header("Insident Log")
    if not incident_log.empty:
        rows_per_page = 20
        total_rows = len(incident_log)
        total_pages = (total_rows + rows_per_page - 1) // rows_per_page

        if 'incident_log_page' not in st.session_state:
            st.session_state.incident_log_page = 1

        with st.form(key="pagination_form", clear_on_submit=False):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                submit_prev = st.form_submit_button("Vorige", disabled=(st.session_state.incident_log_page <= 1))
            with col2:
                page_options = list(range(1, total_pages + 1))
                selected_page = st.selectbox("Bladsy", options=page_options, index=st.session_state.incident_log_page - 1, key="incident_log_page_select")
            with col3:
                submit_next = st.form_submit_button("Volgende", disabled=(st.session_state.incident_log_page >= total_pages))

            if submit_prev:
                st.session_state.incident_log_page = max(1, st.session_state.incident_log_page - 1)
                st.rerun()
            if submit_next:
                st.session_state.incident_log_page = min(total_pages, st.session_state.incident_log_page + 1)
                st.rerun()
            if selected_page != st.session_state.incident_log_page:
                st.session_state.incident_log_page = selected_page
                st.rerun()

        start_idx = (st.session_state.incident_log_page - 1) * rows_per_page
        end_idx = min(start_idx + rows_per_page, total_rows)

        display_df = incident_log.iloc[start_idx:end_idx].copy()
        display_df.index = range(start_idx + 1, min(end_idx + 1, total_rows + 1))

        st.dataframe(
            display_df,
            height=600,
            use_container_width=True,
            column_config={
                "Learner_Full_Name": st.column_config.TextColumn("Leerder Naam", width="medium"),
                "Class": st.column_config.TextColumn("Blok", width="small"),
                "Teacher": st.column_config.TextColumn("Onderwyser", width="medium"),
                "Incident": st.column_config.TextColumn("Insident", width="medium"),
                "Category": st.column_config.TextColumn("Kategorie", width="small"),
                "Comment": st.column_config.TextColumn("Kommentaar", width="large"),
                "Date": st.column_config.DateColumn("Datum", width="medium", format="YYYY-MM-DD")
            }
        )
        st.write(f"Wys {start_idx + 1} tot {end_idx} van {total_rows} insidente")
    else:
        st.write("Geen insidente in die log nie.")

    # Generate Learner Report Section
    st.header("Genereer Leerder Verslag")
    with st.container():
        st.markdown('<div class="input-label">Kies Leerder vir Verslag</div>', unsafe_allow_html=True)
        learner_report_name = st.selectbox("", options=['Kies'] + sorted(incident_log['Learner_Full_Name'].unique()), key="learner_report_name")
        
        st.markdown('<div class="input-label">Kies Tydperk</div>', unsafe_allow_html=True)
        report_period = st.selectbox("", options=['Daagliks', 'Weekliks', 'Maandelik', 'Kwartaalliks'], key="report_period")

        sa_tz = pytz.timezone('Africa/Johannesburg')
        today = datetime.now(sa_tz).date()

        if report_period == 'Daagliks':
            start_date = today
            end_date = today
        elif report_period == 'Weekliks':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif report_period == 'Maandelik':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        else:  # Kwartaalliks
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            start_date = today.replace(month=quarter_start_month, day=1)
            end_date = (start_date + timedelta(days=92)).replace(day=1) - timedelta(days=1)

        st.write(f"Verslag Datum Reeks: {start_date.strftime('%Y-%m-%d')} tot {end_date.strftime('%Y-%m-%d')}")

        if st.button("Genereer Verslag"):
            if learner_report_name != 'Kies':
                learner_incidents = incident_log[
                    (incident_log['Learner_Full_Name'] == learner_report_name) &
                    (incident_log['Date'] >= start_date) &
                    (incident_log['Date'] <= end_date)
                ]
                if not learner_incidents.empty:
                    report_stream = generate_learner_report(learner_incidents, learner_full_name=learner_report_name, period=report_period, start_date=start_date, end_date=end_date)
                    st.success(f"Verslag vir {learner_report_name} suksesvol gegenereer!")
                    st.download_button(
                        label="Laai Verslag af",
                        data=report_stream,
                        file_name=f"insident_verslag_{learner_report_name}_{report_period.lower()}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error(f"Geen insidente gevind vir {learner_report_name} in die geselekteerde tydperk.")
            else:
                st.error("Kies asseblief 'n leerder.")