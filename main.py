import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt
from datetime import datetime, timedelta
import calendar

# Set page configuration
st.set_page_config(
    page_title="AQI Dashboard",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .kpi-label {
        font-size: 1rem;
        font-weight: bold;
        color: #555;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .kpi-unit {
        font-size: 0.9rem;
        color: #777;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_aqi_category(aqi_value):
    """Return AQI category and color based on value"""
    if aqi_value <= 50:
        return "Good", "#00e400"
    elif aqi_value <= 100:
        return "Moderate", "#ffff00"
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive Groups", "#ff7e00"
    elif aqi_value <= 200:
        return "Unhealthy", "#ff0000"
    elif aqi_value <= 300:
        return "Very Unhealthy", "#99004c"
    else:
        return "Hazardous", "#7e0023"

def generate_sample_data():
    """Generate sample AQI data if user doesn't upload a file"""
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
    pollutants = ["PM2.5", "PM10", "O3", "NO2", "SO2", "CO"]
    
    # Generate dates for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    for city in cities:
        for date in dates:
            for pollutant in pollutants:
                # Generate random AQI value with some trend
                base_aqi = np.random.randint(30, 180)
                # Add some weekly pattern
                day_of_week = date.weekday()
                weekday_factor = 1.2 if day_of_week < 5 else 0.8  # Higher on weekdays
                
                # Add city-specific baseline
                city_factor = {
                    "New York": 1.1,
                    "Los Angeles": 1.3,
                    "Chicago": 0.9,
                    "Houston": 1.0,
                    "Phoenix": 1.2
                }[city]
                
                # Add pollutant-specific factor
                pollutant_factor = {
                    "PM2.5": 1.2,
                    "PM10": 1.1,
                    "O3": 1.0,
                    "NO2": 0.9,
                    "SO2": 0.8,
                    "CO": 0.7
                }[pollutant]
                
                aqi = int(base_aqi * weekday_factor * city_factor * pollutant_factor)
                
                data.append({
                    "Date": date,
                    "City": city,
                    "Pollutant": pollutant,
                    "AQI": aqi
                })
    
    return pd.DataFrame(data)

def preprocess_data(df):
    """Preprocess the uploaded data"""
    # Ensure Date column is datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    
    # Check if required columns exist
    required_columns = ['Date', 'City', 'AQI']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        st.stop()
    
    return df

# Sidebar for data upload and filters
st.sidebar.markdown("## Data Input")

# Option to upload data or use sample data
data_option = st.sidebar.radio(
    "Choose data source:",
    ["Upload CSV", "Use Sample Data"]
)

if data_option == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload AQI data (CSV)", type="csv")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df = preprocess_data(df)
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            st.stop()
    else:
        st.info("Please upload a CSV file or select 'Use Sample Data'")
        st.stop()
else:
    df = generate_sample_data()

# Filters
st.sidebar.markdown("## Filters")

# Date range filter
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
else:
    df_filtered = df.copy()

# City filter
available_cities = sorted(df['City'].unique())
selected_cities = st.sidebar.multiselect(
    "Select Cities",
    available_cities,
    default=available_cities[:3] if len(available_cities) > 3 else available_cities
)

if selected_cities:
    df_filtered = df_filtered[df_filtered['City'].isin(selected_cities)]

# Pollutant filter (if available)
if 'Pollutant' in df.columns:
    available_pollutants = sorted(df['Pollutant'].unique())
    selected_pollutants = st.sidebar.multiselect(
        "Select Pollutants",
        available_pollutants,
        default=available_pollutants[:1] if available_pollutants else []
    )
    
    if selected_pollutants:
        df_filtered = df_filtered[df_filtered['Pollutant'].isin(selected_pollutants)]

# AQI range filter
min_aqi = int(df['AQI'].min())
max_aqi = int(df['AQI'].max())

aqi_range = st.sidebar.slider(
    "AQI Range",
    min_value=min_aqi,
    max_value=max_aqi,
    value=(min_aqi, max_aqi)
)

df_filtered = df_filtered[(df_filtered['AQI'] >= aqi_range[0]) & (df_filtered['AQI'] <= aqi_range[1])]

# Option to download filtered data
if not df_filtered.empty:
    csv = df_filtered.to_csv(index=False)
    st.sidebar.download_button(
        label="Download Filtered Data",
        data=csv,
        file_name="filtered_aqi_data.csv",
        mime="text/csv"
    )

# Main dashboard
st.markdown("<h1 class='main-header'>Air Quality Index Dashboard</h1>", unsafe_allow_html=True)

# KPI Cards
if not df_filtered.empty and selected_cities:
    # Get the most recent date in the filtered data
    latest_date = df_filtered['Date'].max()
    latest_data = df_filtered[df_filtered['Date'] == latest_date]
    
    # Calculate KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    # KPI 1: Current AQI for first selected city
    with kpi1:
        city_latest = latest_data[latest_data['City'] == selected_cities[0]]
        if not city_latest.empty:
            current_aqi = int(city_latest['AQI'].mean())
            category, color = get_aqi_category(current_aqi)
            
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Current AQI - {selected_cities[0]}</div>
                <div class='kpi-value' style='color:{color}'>{current_aqi}</div>
                <div class='kpi-unit'>{category}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # KPI 2: Highest AQI in selected period
    with kpi2:
        highest_aqi = int(df_filtered['AQI'].max())
        highest_city = df_filtered[df_filtered['AQI'] == highest_aqi]['City'].values[0]
        highest_date = df_filtered[df_filtered['AQI'] == highest_aqi]['Date'].dt.date.values[0]
        category, color = get_aqi_category(highest_aqi)
        
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Highest AQI</div>
            <div class='kpi-value' style='color:{color}'>{highest_aqi}</div>
            <div class='kpi-unit'>{highest_city} on {highest_date}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # KPI 3: Lowest AQI in selected period
    with kpi3:
        lowest_aqi = int(df_filtered['AQI'].min())
        lowest_city = df_filtered[df_filtered['AQI'] == lowest_aqi]['City'].values[0]
        lowest_date = df_filtered[df_filtered['AQI'] == lowest_aqi]['Date'].dt.date.values[0]
        category, color = get_aqi_category(lowest_aqi)
        
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Lowest AQI</div>
            <div class='kpi-value' style='color:{color}'>{lowest_aqi}</div>
            <div class='kpi-unit'>{lowest_city} on {lowest_date}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # KPI 4: Most polluted city
    with kpi4:
        city_avg = df_filtered.groupby('City')['AQI'].mean().reset_index()
        most_polluted = city_avg.loc[city_avg['AQI'].idxmax()]
        avg_aqi = int(most_polluted['AQI'])
        category, color = get_aqi_category(avg_aqi)
        
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Most Polluted City</div>
            <div class='kpi-value' style='color:{color}'>{most_polluted['City']}</div>
            <div class='kpi-unit'>Avg AQI: {avg_aqi}</div>
        </div>
        """, unsafe_allow_html=True)

# Tabs for different visualizations
tabs = st.tabs(["AQI Trends", "City Comparison", "Calendar View"])

# Tab 1: AQI Trends (Line Chart with Plotly)
with tabs[0]:
    if not df_filtered.empty and selected_cities:
        st.subheader("AQI Trends Over Time")
        
        # Prepare data for line chart
        if 'Pollutant' in df_filtered.columns and selected_pollutants:
            # If pollutant filter is active, show trends for selected pollutant across cities
            trend_data = df_filtered[df_filtered['Pollutant'] == selected_pollutants[0]]
            line_data = trend_data.groupby(['Date', 'City'])['AQI'].mean().reset_index()
            
            fig = px.line(
                line_data,
                x="Date",
                y="AQI",
                color="City",
                title=f"AQI Trends for {selected_pollutants[0]}",
                labels={"AQI": "Air Quality Index", "Date": "Date"},
                line_shape="spline",
                render_mode="svg"
            )
        else:
            # If no pollutant filter, show overall AQI trends by city
            line_data = df_filtered.groupby(['Date', 'City'])['AQI'].mean().reset_index()
            
            fig = px.line(
                line_data,
                x="Date",
                y="AQI",
                color="City",
                title="Overall AQI Trends",
                labels={"AQI": "Air Quality Index", "Date": "Date"},
                line_shape="spline",
                render_mode="svg"
            )
        
        # Add AQI category thresholds
        fig.add_shape(type="line", x0=min_date, x1=max_date, y0=50, y1=50,
                    line=dict(color="green", width=1, dash="dash"))
        fig.add_shape(type="line", x0=min_date, x1=max_date, y0=100, y1=100,
                    line=dict(color="yellow", width=1, dash="dash"))
        fig.add_shape(type="line", x0=min_date, x1=max_date, y0=150, y1=150,
                    line=dict(color="orange", width=1, dash="dash"))
        fig.add_shape(type="line", x0=min_date, x1=max_date, y0=200, y1=200,
                    line=dict(color="red", width=1, dash="dash"))
        fig.add_shape(type="line", x0=min_date, x1=max_date, y0=300, y1=300,
                    line=dict(color="purple", width=1, dash="dash"))
        
        # Update layout
        fig.update_layout(
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one city to view AQI trends.")

# Tab 2: City Comparison (Bar Chart with Altair)
with tabs[1]:
    if not df_filtered.empty and selected_cities:
        st.subheader("AQI Comparison by City")
        
        # Prepare data for bar chart
        if 'Pollutant' in df_filtered.columns and selected_pollutants:
            # If pollutant filter is active, compare cities for each pollutant
            comparison_data = df_filtered[df_filtered['Pollutant'].isin(selected_pollutants)]
            bar_data = comparison_data.groupby(['City', 'Pollutant'])['AQI'].mean().reset_index()
            
            # Create Altair chart
            chart = alt.Chart(bar_data).mark_bar().encode(
                x=alt.X('City:N', title='City'),
                y=alt.Y('AQI:Q', title='Average AQI'),
                color=alt.Color('City:N', legend=None),
                column=alt.Column('Pollutant:N', title='Pollutant'),
                tooltip=['City', 'Pollutant', alt.Tooltip('AQI:Q', title='Avg AQI', format='.1f')]
            ).properties(
                width=alt.Step(80),  # width of each bar
                height=400
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            )
        else:
            # If no pollutant filter, show overall AQI comparison
            bar_data = df_filtered.groupby('City')['AQI'].mean().reset_index()
            
            # Create color scale based on AQI values
            color_scale = alt.Scale(
                domain=[0, 50, 100, 150, 200, 300, 500],
                range=['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#99004c', '#7e0023']
            )
            
            # Create Altair chart
            chart = alt.Chart(bar_data).mark_bar().encode(
                x=alt.X('City:N', title='City', sort='-y'),
                y=alt.Y('AQI:Q', title='Average AQI'),
                color=alt.Color('AQI:Q', scale=color_scale, legend=alt.Legend(title="AQI Level")),
                tooltip=['City', alt.Tooltip('AQI:Q', title='Avg AQI', format='.1f')]
            ).properties(
                width=alt.Step(80),  # width of each bar
                height=400
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            )
        
        st.altair_chart(chart, use_container_width=True)
        
        # Add a table with detailed statistics
        st.subheader("Detailed Statistics by City")
        stats_data = df_filtered.groupby('City')['AQI'].agg(['mean', 'min', 'max', 'std']).reset_index()
        stats_data.columns = ['City', 'Average AQI', 'Min AQI', 'Max AQI', 'Std Dev']
        stats_data = stats_data.round(1)
        
        st.dataframe(stats_data, use_container_width=True)
    else:
        st.info("Please select at least one city to view city comparisons.")

# Tab 3: Calendar View (Heatmap)
with tabs[2]:
    if not df_filtered.empty and selected_cities:
        st.subheader("AQI Calendar View")
        
        # City selector for calendar view
        calendar_city = st.selectbox(
            "Select City for Calendar View",
            selected_cities
        )
        
        # Filter data for selected city
        city_data = df_filtered[df_filtered['City'] == calendar_city]
        
        if not city_data.empty:
            # Prepare data for calendar view
            if 'Pollutant' in city_data.columns and selected_pollutants:
                # If pollutant filter is active, show calendar for selected pollutant
                calendar_data = city_data[city_data['Pollutant'] == selected_pollutants[0]]
                title = f"Daily AQI Levels for {calendar_city} - {selected_pollutants[0]}"
            else:
                # If no pollutant filter, show overall AQI calendar
                calendar_data = city_data
                title = f"Daily AQI Levels for {calendar_city}"
            
            # Aggregate by date
            daily_data = calendar_data.groupby('Date')['AQI'].mean().reset_index()
            
            # Extract year, month, day components
            daily_data['Year'] = daily_data['Date'].dt.year
            daily_data['Month'] = daily_data['Date'].dt.month
            daily_data['Day'] = daily_data['Date'].dt.day
            daily_data['MonthName'] = daily_data['Date'].dt.strftime('%B')
            
            # Create color scale based on AQI values
            color_scale = alt.Scale(
                domain=[0, 50, 100, 150, 200, 300, 500],
                range=['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#99004c', '#7e0023']
            )
            
            # Create calendar heatmap
            calendar_chart = alt.Chart(daily_data).mark_rect().encode(
                x=alt.X('Day:O', title='Day', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('MonthName:O', title='Month', sort=list(calendar.month_name)[1:]),
                color=alt.Color('AQI:Q', scale=color_scale, legend=alt.Legend(title="AQI Level")),
                tooltip=[
                    alt.Tooltip('Date:T', title='Date', format='%Y-%m-%d'),
                    alt.Tooltip('AQI:Q', title='AQI', format='.1f')
                ]
            ).properties(
                width=alt.Step(30),  # width of each cell
                height=alt.Step(30) * len(daily_data['MonthName'].unique()),
                title=title
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            ).configure_title(
                fontSize=16
            )
            
            st.altair_chart(calendar_chart, use_container_width=True)
            
            # Add explanation of AQI categories
            st.subheader("AQI Categories")
            categories = [
                {"range": "0-50", "category": "Good", "color": "#00e400", "description": "Air quality is satisfactory, and air pollution poses little or no risk."},
                {"range": "51-100", "category": "Moderate", "color": "#ffff00", "description": "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."},
                {"range": "101-150", "category": "Unhealthy for Sensitive Groups", "color": "#ff7e00", "description": "Members of sensitive groups may experience health effects. The general public is less likely to be affected."},
                {"range": "151-200", "category": "Unhealthy", "color": "#ff0000", "description": "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."},
                {"range": "201-300", "category": "Very Unhealthy", "color": "#99004c", "description": "Health alert: The risk of health effects is increased for everyone."},
                {"range": "301+", "category": "Hazardous", "color": "#7e0023", "description": "Health warning of emergency conditions: everyone is more likely to be affected."}
            ]
            
            # Create a DataFrame for the categories
            categories_df = pd.DataFrame(categories)
            
            # Display the categories as a styled table
            for i, row in categories_df.iterrows():
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown(f"<div style='background-color: {row['color']}; width: 50px; height: 20px; border-radius: 4px;'></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**{row['category']} ({row['range']})**: {row['description']}")
        else:
            st.info(f"No data available for {calendar_city} in the selected date range.")
    else:
        st.info("Please select at least one city to view the calendar.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.8rem;">
    AQI Dashboard | Created with Streamlit | Data last updated: {}
</div>
""".format(df['Date'].max().strftime('%Y-%m-%d')), unsafe_allow_html=True)