import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Cinema Customer Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("cinema_customers_expanded.csv")
    df = df[df['Type'].str.lower() != 'non member']  # Loại bỏ non-member
    df = df.dropna()
    df[['Movie_watched_month', 'Snacks_popcorn', 'Total']] = df[['Movie_watched_month', 'Snacks_popcorn', 'Total']].apply(pd.to_numeric, errors='coerce')
    return df

def format_with_commas(number):
    return f"{number:,}"

def create_metric_chart(df, column, color, height=150):
    return st.area_chart(df[[column]], color=color, height=height)

def display_metric(col, title, value, df, column, color):
    with col:
        with st.container(border=True):
            st.metric(title, format_with_commas(value))
            create_metric_chart(df, column, color)

# Load and prepare data
df = load_data()

# Sidebar filters
with st.sidebar:
    st.header("⚙️ Settings")
    type_options = sorted(df['Type'].unique())
    selected_types = st.multiselect("Member Type", type_options, default=type_options)

    age_min, age_max = int(df['Age'].min()), int(df['Age'].max())
    age_range = st.slider("Age Range", age_min, age_max, (age_min, age_max))

    year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
    year_range = st.slider("Years with Cinema", year_min, year_max, (year_min, year_max))

    time_frame = st.selectbox("Display Mode", ["Daily", "Cumulative"])

# Filter data
df_filtered = df[
    (df['Type'].isin(selected_types)) &
    (df['Age'].between(*age_range)) &
    (df['Year'].between(*year_range))
].copy()

# Add daily index for plotting (fake daily just to simulate time)
df_filtered['DATE'] = pd.date_range(start='2023-01-01', periods=len(df_filtered), freq='D')
df_filtered.set_index('DATE', inplace=True)

# Cumulative data
df_cumulative = df_filtered.copy()
for col in ['Movie_watched_month', 'Snacks_popcorn', 'Total']:
    df_cumulative[col] = df_cumulative[col].cumsum()

# Display
st.title("🍿 Cinema Customer Dashboard")

st.subheader("Key Metrics")
cols = st.columns(3)

metrics = [
    ("Monthly Movies", "Movie_watched_month", "#29b5e8"),
    ("Snacks Purchased", "Snacks_popcorn", "#D45B90"),
    ("Total Spending ($)", "Total", "#FF9F36")
]

df_display = df_cumulative if time_frame == "Cumulative" else df_filtered

for col, (title, column, color) in zip(cols, metrics):
    total_value = df_display[column].iloc[-1] if time_frame == "Cumulative" else df_display[column].sum()
    display_metric(col, title, total_value, df_display, column, color)

# Data preview
with st.expander("📄 Show Raw Data"):
    st.dataframe(df_filtered.reset_index())
