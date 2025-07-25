import streamlit as st
import pandas as pd
import altair as alt

# Page config
st.set_page_config(page_title="Cinema Customer Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("cinema_customers_expanded.csv")
    df['Type'] = df['Type'].astype(str).str.strip().str.lower()
    df = df[~df['Type'].str.contains('non.?member', regex=True)]
    df['Type'] = df['Type'].str.title()
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

# Load data
df = load_data()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    type_options = sorted(df['Type'].unique())
    selected_types = st.multiselect("Member Type", type_options, default=type_options)

    age_range = st.slider("Age Range", int(df['Age'].min()), int(df['Age'].max()), (18, 60))
    year_range = st.slider("Years with Cinema", int(df['Year'].min()), int(df['Year'].max()), (1, 5))
    time_frame = st.selectbox("Display Mode", ["Daily", "Cumulative"])

    st.subheader("📈 Correlation Settings")
    x_axis = st.selectbox("Choose variable to compare with Total Spending", 
        options=["Age", "Year", "Movie_watched_month", "Snacks_popcorn", "Type"])

# Filter data
df_filtered = df[
    (df['Type'].isin(selected_types)) &
    (df['Age'].between(*age_range)) &
    (df['Year'].between(*year_range))
].copy()

df_filtered['DATE'] = pd.date_range(start='2023-01-01', periods=len(df_filtered), freq='D')
df_filtered.set_index('DATE', inplace=True)

# Cumulative
df_cumulative = df_filtered.copy()
for col in ['Movie_watched_month', 'Snacks_popcorn', 'Total']:
    df_cumulative[col] = df_cumulative[col].cumsum()

# Main
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

with st.expander("📄 Show Raw Data"):
    st.dataframe(df_filtered.reset_index())

# Correlation
st.subheader(f"📊 Total Spending vs {x_axis}")

if not df_filtered.empty:
    if x_axis in ["Age", "Year", "Movie_watched_month", "Snacks_popcorn"]:
        scatter = alt.Chart(df_filtered).mark_circle(size=60, opacity=0.5).encode(
            x=alt.X(x_axis, title=x_axis),
            y=alt.Y("Total", title="Total Spending"),
            tooltip=["Type", "Age", "Total"]
        )
        line = scatter.transform_regression(x_axis, "Total").mark_line(color='red')
        st.altair_chart(scatter + line, use_container_width=True)
    elif x_axis == "Type":
        bar = alt.Chart(df_filtered).mark_bar().encode(
            x=alt.X("Type", sort='-y'),
            y=alt.Y("mean(Total)", title="Avg Spending"),
            color="Type"
        )
        st.altair_chart(bar, use_container_width=True)
else:
    st.warning("No data after filtering.")
st.subheader("📈 Correlation Settings")
x_axis = st.selectbox(
    "Choose variable to compare with Total Spending", 
    options=["Age", "Year", "Movie_watched_month", "Snacks_popcorn", "Type"]
)

