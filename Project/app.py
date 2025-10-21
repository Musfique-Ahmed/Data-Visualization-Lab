import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="FIFA 22 Players Analysis",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #1e1e1e;
    }
    .stMetric {
        background-color: #2d2d2d;
        padding: 10px;
        border-radius: 5px;
        border: 2px solid #3d3d3d;
    }
    h1 {
        color: #ff9800;
        text-align: center;
        font-weight: bold;
        padding: 20px;
        border: 3px solid #ff9800;
        border-radius: 10px;
        background-color: #2d2d2d;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('players_22_cleaned.csv')
    return df

# Load the data
df = load_data()

# Title
st.markdown("<h1>⚽ FIFA 22 Players Analysis</h1>", unsafe_allow_html=True)

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_value = df['value_eur'].mean() / 1_000_000
    st.metric("Average Value", f"{avg_value:.2f}M €")

with col2:
    avg_wage = df['wage_eur'].mean() / 1_000
    st.metric("Average Wage", f"{avg_wage:.2f}K €")

with col3:
    # Top player by value
    top_player_value = df.loc[df['value_eur'].idxmax()]
    st.metric("Top Player By Value", top_player_value['short_name'])
    st.caption(f"Value: {top_player_value['value_eur']/1_000_000:.0f}M €")

with col4:
    # Top player by wage
    top_player_wage = df.loc[df['wage_eur'].idxmax()]
    st.metric("Top Player By Wage", top_player_wage['short_name'])
    st.caption(f"Wage: {top_player_wage['wage_eur']/1_000:.0f}K €")

st.markdown("---")

# Second metrics row
col5, col6, col7, col8 = st.columns(4)

with col5:
    max_value = df['value_eur'].max() / 1_000_000
    st.metric("Max Value", f"{max_value:.0f}M €")

with col6:
    max_wage = df['wage_eur'].max() / 1_000
    st.metric("Max Wage", f"{max_wage:.0f}K €")

with col7:
    # Players by preferred foot
    right_foot = len(df[df['preferred_foot'] == 'Right'])
    st.metric("Right Footed Players", f"{right_foot:,}")

with col8:
    left_foot = len(df[df['preferred_foot'] == 'Left'])
    st.metric("Left Footed Players", f"{left_foot:,}")

st.markdown("---")

# Main content area
row1_col1, row1_col2 = st.columns([1, 2])

# Top 100 Clubs by Value
with row1_col1:
    st.subheader("Top 100 Clubs by Value")
    club_value = df.groupby('club_name')['value_eur'].sum().sort_values(ascending=False).head(100)
    club_value_df = pd.DataFrame({
        'Club': club_value.index,
        'Value': club_value.values / 1_000_000_000  # Convert to billions
    })
    
    fig_clubs = px.bar(
        club_value_df.head(20),
        y='Club',
        x='Value',
        orientation='h',
        title='Top 20 Clubs by Total Value',
        labels={'Value': 'Value (Billions €)', 'Club': ''},
        color='Value',
        color_continuous_scale='Viridis'
    )
    fig_clubs.update_layout(
        height=600,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_clubs, use_container_width=True)

# Player Distribution by Overall Rating and Potential
with row1_col2:
    col_hist1, col_hist2 = st.columns(2)
    
    with col_hist1:
        st.subheader("Player Distribution by Overall Rating")
        fig_overall = px.histogram(
            df,
            x='overall',
            nbins=30,
            title='Overall Rating Distribution',
            labels={'overall': 'Overall Rating', 'count': 'Number of Players'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_overall.update_layout(
            height=300,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_overall, use_container_width=True)
    
    with col_hist2:
        st.subheader("Player Distribution by Potential")
        fig_potential = px.histogram(
            df,
            x='potential',
            nbins=30,
            title='Potential Rating Distribution',
            labels={'potential': 'Potential (POT)', 'count': 'Number of Players'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_potential.update_layout(
            height=300,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_potential, use_container_width=True)
    
    # Players by Preferred Foot
    st.subheader("Players by Preferred Foot")
    foot_counts = df['preferred_foot'].value_counts()
    fig_foot = px.bar(
        x=foot_counts.index,
        y=foot_counts.values,
        title='Distribution by Preferred Foot',
        labels={'x': 'Preferred Foot', 'y': 'Number of Players'},
        color=foot_counts.index,
        color_discrete_map={'Right': '#1f77b4', 'Left': '#ff9800'}
    )
    fig_foot.update_layout(
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_foot, use_container_width=True)

st.markdown("---")

# Row 2: Age Distribution and Nationality Map
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Players Distribution by Age")
    # Create age groups
    df['age_group'] = pd.cut(df['age'], bins=[16, 20, 25, 30, 35, 50], 
                              labels=['16-20', '21-25', '26-30', '31-35', '36+'])
    age_counts = df.groupby('age_group').size().reset_index(name='count')
    
    fig_age = px.treemap(
        age_counts,
        path=['age_group'],
        values='count',
        title='Players by Age Groups',
        color='count',
        color_continuous_scale='RdYlGn'
    )
    fig_age.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    fig_age.update_traces(textinfo="label+value+percent parent")
    st.plotly_chart(fig_age, use_container_width=True)

with row2_col2:
    st.subheader("Players Distribution by Nationality")
    nationality_counts = df['nationality_name'].value_counts().reset_index()
    nationality_counts.columns = ['country', 'count']
    
    # Map country names to ISO codes for plotly
    fig_map = px.choropleth(
        nationality_counts.head(50),
        locations='country',
        locationmode='country names',
        color='count',
        hover_name='country',
        hover_data={'count': True},
        title='Top 50 Countries by Player Count',
        color_continuous_scale='Blues',
        labels={'count': 'Number of Players'}
    )
    fig_map.update_layout(
        height=500,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth',
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# Additional Statistics Section
st.header("📊 Additional Statistics")

col_stat1, col_stat2, col_stat3 = st.columns(3)

with col_stat1:
    st.subheader("Top 10 Leagues by Players")
    league_counts = df['league_name'].value_counts().head(10)
    fig_leagues = px.bar(
        x=league_counts.values,
        y=league_counts.index,
        orientation='h',
        labels={'x': 'Number of Players', 'y': 'League'},
        color=league_counts.values,
        color_continuous_scale='Bluered'
    )
    fig_leagues.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_leagues, use_container_width=True)

with col_stat2:
    st.subheader("Work Rate Distribution")
    work_rate_counts = df['work_rate'].value_counts().head(10)
    fig_workrate = px.pie(
        values=work_rate_counts.values,
        names=work_rate_counts.index,
        title='Top 10 Work Rate Patterns',
        hole=0.4
    )
    fig_workrate.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_workrate, use_container_width=True)

with col_stat3:
    st.subheader("Body Type Distribution")
    body_type_counts = df['body_type'].value_counts().head(10)
    fig_body = px.bar(
        x=body_type_counts.index,
        y=body_type_counts.values,
        labels={'x': 'Body Type', 'y': 'Number of Players'},
        color=body_type_counts.values,
        color_continuous_scale='Sunset'
    )
    fig_body.update_layout(
        height=400,
        showlegend=False,
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_body, use_container_width=True)

st.markdown("---")

# Sidebar with filters
st.sidebar.header("🔍 Filters")
st.sidebar.markdown("---")

# Position filter
positions = df['player_positions'].str.split(',').explode().str.strip().unique()
selected_position = st.sidebar.multiselect(
    "Select Position(s)",
    options=sorted([p for p in positions if pd.notna(p)]),
    default=[]
)

# Overall rating filter
min_overall, max_overall = st.sidebar.slider(
    "Overall Rating Range",
    int(df['overall'].min()),
    int(df['overall'].max()),
    (int(df['overall'].min()), int(df['overall'].max()))
)

# Age filter
min_age, max_age = st.sidebar.slider(
    "Age Range",
    int(df['age'].min()),
    int(df['age'].max()),
    (int(df['age'].min()), int(df['age'].max()))
)

# Apply filters button
if st.sidebar.button("Apply Filters"):
    filtered_df = df.copy()
    
    if selected_position:
        filtered_df = filtered_df[filtered_df['player_positions'].str.contains('|'.join(selected_position), na=False)]
    
    filtered_df = filtered_df[
        (filtered_df['overall'] >= min_overall) & 
        (filtered_df['overall'] <= max_overall) &
        (filtered_df['age'] >= min_age) & 
        (filtered_df['age'] <= max_age)
    ]
    
    st.sidebar.success(f"Filtered: {len(filtered_df)} players")
    
    # Display filtered data
    st.subheader("📋 Filtered Player Data")
    st.dataframe(
        filtered_df[['short_name', 'overall', 'potential', 'value_eur', 'wage_eur', 
                     'age', 'club_name', 'nationality_name']].head(50),
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>⚽ FIFA 22 Players Analysis Dashboard | Data Source: SoFIFA</p>
        <p>Created with Streamlit & Plotly | Total Players: {}</p>
    </div>
    """.format(len(df)),
    unsafe_allow_html=True
)



# streamlit run app.py