import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Cinema Customer Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("cinema_customers_expanded.csv")

    
    df['Type'] = df['Type'].astype(str).str.strip().str.lower()

    df = df[~df['Type'].str.contains('non.?member', regex=True)]

    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')

    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🎯 Filters")
type_options = df['Type'].unique().tolist()
type_filter = st.sidebar.multiselect("Select member type", type_options, default=type_options)

year_range = st.sidebar.slider("Select year range", int(df['Year'].min()), int(df['Year'].max()), (1, 5))

age_range = st.sidebar.slider("Select age range", int(df['Age'].min()), int(df['Age'].max()), (18, 60))

# Apply filters
df_filtered = df[
    (df['Type'].isin(type_filter)) &
    (df['Year'].between(*year_range)) &
    (df['Age'].between(*age_range))
]

# KPI Metrics
st.title("🍿 Cinema Customer Dashboard")
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", len(df_filtered))
col2.metric("Avg Monthly Movies", f"{df_filtered['Movie_watched_month'].mean():.2f}")
col3.metric("Avg Total Spending", f"${df_filtered['Total'].mean():,.0f}")

# Bar chart by Member Type
st.subheader("💳 Spending by Member Type")
type_group = df_filtered.groupby("Type")["Total"].mean().sort_values(ascending=False)
st.bar_chart(type_group)

# Age vs Total spending
st.subheader("🧓 Age vs Total Spending")
st.scatter_chart(df_filtered[['Age', 'Total']])

# Data preview
with st.expander("📄 Show Data Table"):
    st.dataframe(df_filtered)
