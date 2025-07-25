import streamlit as st
import pandas as pd
import altair as alt

# Page config
st.set_page_config(page_title="Cinema Customer Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("cinema_customers_expanded.csv")

    # Chuẩn hóa cột Type và loại bỏ non-member
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

    # Tùy chọn tương quan
    st.subheader("📈 Correlation Analysis")
    correlation_col = st.selectbox(
        "Compare Total Spending with:",
        options=["Age", "Movie_watched_month", "Snacks_popcorn"]
    )

# Filter data
df_filtered = df[
    (df['Type'].isin(selected_types)) &
    (df['Age'].between(*age_range)) &
    (df['Year'].between(*year_range))
].copy()

# Add fake date index
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

# Show DataFrame
with st.expander("📄 Show Raw Data"):
    st.dataframe(df_filtered.reset_index())

# Correlation Section
st.subheader(f"📈 Correlation: Total vs {correlation_col}")

if not df_filtered.empty:
    corr_chart = alt.Chart(df_filtered).mark_circle(size=60, opacity=0.6).encode(
        x=alt.X(correlation_col, title=correlation_col),
        y=alt.Y("Total", title="Total Spending"),
        tooltip=["Type", "Age", "Total"]
    )

    regression_line = corr_chart.transform_regression(correlation_col, "Total").mark_line(color="red")

    st.altair_chart(corr_chart + regression_line, use_container_width=True)
else:
    st.warning("No data available after filtering.")
