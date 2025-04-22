import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. Load Data ---
@st.cache_data
def load_data():
    overall = pd.read_csv('data/mw_overall.csv')
    style = pd.read_csv('data/style_based_features.csv')
    total = pd.read_csv('data/total_data.csv')
    mw_pw = pd.read_csv('data/mw_pw.csv')
    mw_pw_profiles = pd.read_csv('data/mw_pw_profiles.csv')
    return overall, style, total, mw_pw, mw_pw_profiles

overall_df, style_df, total_df, mw_pw_df, mw_pw_profiles_df = load_data()

# --- 2. Sidebar Debug Info ---
st.sidebar.title("🛠️ Debug Info")
st.sidebar.write("**CWD:**", os.getcwd())
st.sidebar.write("**Files:**", os.listdir("."))
st.sidebar.write("**Data Folder:**", os.listdir("data"))

# Display columns of all datasets for reference
st.sidebar.subheader("🧾 Columns in mw_overall.csv")
st.sidebar.write(overall_df.columns.tolist())

st.sidebar.subheader("🧾 Columns in style_based_features.csv")
st.sidebar.write(style_df.columns.tolist())

st.sidebar.subheader("🧾 Columns in total_data.csv")
st.sidebar.write(total_df.columns.tolist())

st.sidebar.subheader("🧾 Columns in mw_pw.csv")
st.sidebar.write(mw_pw_df.columns.tolist())

st.sidebar.subheader("🧾 Columns in mw_pw_profiles.csv")
st.sidebar.write(mw_pw_profiles_df.columns.tolist())

# --- 3. Batting Performance Analysis ---
st.header("1. Player Batting Performance")
batting_stats = ['runs_scored', 'balls_faced', 'fours_scored', 'sixes_scored']
selected_batting_stat = st.selectbox("Select Stat for Batting", batting_stats)

df_batting = total_df.groupby('name')[selected_batting_stat].sum().reset_index()
fig_batting = px.bar(
    df_batting,
    x='name', y=selected_batting_stat,
    labels={'name': 'Player', selected_batting_stat: f'Total {selected_batting_stat.capitalize()}'},
    title=f"Player {selected_batting_stat.capitalize()} Performance"
)
st.plotly_chart(fig_batting, use_container_width=True)

# --- 4. Bowling Performance Analysis ---
st.header("2. Player Bowling Performance")
bowling_stats = ['wickets_taken', 'runs_conceded', 'balls_bowled', 'maidens']
selected_bowling_stat = st.selectbox("Select Stat for Bowling", bowling_stats)

df_bowling = total_df.groupby('name')[selected_bowling_stat].sum().reset_index()
fig_bowling = px.bar(
    df_bowling,
    x='name', y=selected_bowling_stat,
    labels={'name': 'Player', selected_bowling_stat: f'Total {selected_bowling_stat.capitalize()}'},
    title=f"Player {selected_bowling_stat.capitalize()} Performance"
)
st.plotly_chart(fig_bowling, use_container_width=True)

# --- 5. Player vs Team Comparison ---
st.header("3. Player vs Team Comparison")
teams = total_df['opposition_team'].unique()
selected_team = st.selectbox("Select Team for Player vs Team Comparison", teams)

# Filter data for selected team
df_team = total_df[total_df['opposition_team'] == selected_team]
df_team_stats = df_team.groupby('name').agg(
    runs_scored=('runs_scored', 'sum'),
    balls_faced=('balls_faced', 'sum')
).reset_index()

fig_team = px.bar(
    df_team_stats,
    x='name', y='runs_scored',
    labels={'name': 'Player', 'runs_scored': 'Runs Scored'},
    title=f"Player Runs Scored Against {selected_team}"
)
st.plotly_chart(fig_team, use_container_width=True)

# --- 6. Dismissal Patterns ---
st.header("4. Player Dismissal Patterns")
dismissal_types = ['bowled', 'caught', 'run out', 'stumped']
selected_dismissal_type = st.selectbox("Select Dismissal Type", dismissal_types)

df_dismissals = mw_pw_df[mw_pw_df[selected_dismissal_type] > 0]
df_dismissals_stats = df_dismissals.groupby('name_x')[selected_dismissal_type].sum().reset_index()

fig_dismissals = px.bar(
    df_dismissals_stats,
    x='name_x', y=selected_dismissal_type,
    labels={'name_x': 'Player', selected_dismissal_type: f'{selected_dismissal_type.capitalize()} Count'},
    title=f"Dismissals of Players (by {selected_dismissal_type.capitalize()})"
)
st.plotly_chart(fig_dismissals, use_container_width=True)

# --- 7. Style-Based Performance Analysis ---
st.header("5. Player Style Profile")
selected_player = st.selectbox("Select Player", style_df['name'].unique())

df_player = style_df[style_df['name'] == selected_player]
if df_player.empty:
    st.write(f"No style data available for {selected_player}.")
else:
    feature_cols = [col for col in df_player.columns if 'against' in col and col != 'name']
    selected_feats = st.multiselect("Select Features to Plot", options=feature_cols, default=feature_cols[:5])
    
    if selected_feats:
        df_melt = df_player.melt(
            id_vars='name',
            value_vars=selected_feats,
            var_name='feature',
            value_name='value'
        )
        fig_style = px.bar(
            df_melt,
            x='feature', y='value',
            labels={'feature': 'Bowling Type', 'value': 'Performance'},
            title=f"{selected_player}'s Performance Against Different Bowling Types"
        )
        st.plotly_chart(fig_style, use_container_width=True)
    else:
        st.info("Please select at least one feature to display.")
