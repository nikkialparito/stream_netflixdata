# -*- coding: utf-8 -*-
"""Netflix-streamlit.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1XQUgViJ9mFtz_A_kp0QuHfWdeNKPLhRk
"""

!pip install streamlit==1.28.1

pip install plotly

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="Netflix Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

df_reshaped = pd.read_csv('netflix_titles.csv')

with st.sidebar:
    st.title('🏂 Netflix Dashboard')

    # Access the 'release_year' column instead of 'year'
    release_year = list(df_reshaped.release_year.unique())[::-1]

    release_year = st.selectbox('Select a year', release_year, index=len(release_year)-1)
    # Access the 'release_year' column instead of 'year'
    df_release_year = df_reshaped[df_reshaped.release_year == release_year]
    df_release_year_sorted = df_release_year.sort_values(by="release_year", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        )
    # height=300
    return heatmap

# Choropleth Map for Netflix Content by Country
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="country names",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(input_df[input_column].dropna())),
                               scope="world",
                               labels={input_column: 'Number of Titles'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

# Calculate Difference in Number of Titles Over Years
def calculate_title_difference(input_df, input_year):
    selected_year_data = input_df[input_df['release_year'] == input_year].groupby('country').size().reset_index(name='title_count')
    previous_year_data = input_df[input_df['release_year'] == input_year - 1].groupby('country').size().reset_index(name='title_count')
    merged_data = pd.merge(selected_year_data, previous_year_data, on='country', how='left', suffixes=('_current', '_previous'))
    merged_data['title_difference'] = merged_data['title_count_current'].sub(merged_data['title_count_previous'], fill_value=0)
    return merged_data.sort_values(by="title_difference", ascending=False)

def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']

  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })

  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)

  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

# Donut Chart for Netflix Content Distribution
def make_donut(input_response, input_text, input_color):
    color_map = {
        'blue': ['#29b5e8', '#155F7A'],
        'green': ['#27AE60', '#12783D'],
        'orange': ['#F39C12', '#875A12'],
        'red': ['#E74C3C', '#781F16']
    }
    chart_color = color_map.get(input_color, ['#29b5e8', '#155F7A'])

    source = pd.DataFrame({
        "Category": ['', input_text],
        "Percentage": [100 - input_response, input_response]
    })

    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="Percentage",
        color=alt.Color("Category:N", scale=alt.Scale(domain=[input_text, ''], range=chart_color), legend=None)
    ).properties(width=130, height=130)

    text = plot.mark_text(align='center', color=chart_color[0], fontSize=18, fontWeight=700).encode(text=alt.value(f'{input_response} %'))

    return plot + text

def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

col = st.columns((1.5, 4.5, 2), gap='medium')

# Display Gains/Losses in Netflix Titles by Year
import streamlit as st
import pandas as pd

# ... (other code) ...

# Load your dataframe here
df = pd.read_csv('netflix_titles.csv')

# Define the calculate_title_difference function
def calculate_title_difference(input_df, input_year):
    selected_year_data = input_df[input_df['release_year'] == input_year].groupby('country').size().reset_index(name='title_count')
    previous_year_data = input_df[input_df['release_year'] == input_year - 1].groupby('country').size().reset_index(name='title_count')
    merged_data = pd.merge(selected_year_data, previous_year_data, on='country', how='left', suffixes=('_current', '_previous'))
    merged_data['title_difference'] = merged_data['title_count_current'].sub(merged_data['title_count_previous'], fill_value=0)
    return merged_data.sort_values(by="title_difference", ascending=False)


st.markdown('#### Gains/Losses')
df_title_difference_sorted = calculate_title_difference(df, release_year) # Call the newly defined function

if not df_title_difference_sorted.empty:
    top_country = df_title_difference_sorted.iloc[0]
    st.metric(label=top_country['country'], value=top_country['title_count_current'], delta=top_country['title_difference'])
    bottom_country = df_title_difference_sorted.iloc[-1]
    st.metric(label=bottom_country['country'], value=bottom_country['title_count_current'], delta=bottom_country['title_difference'])

st.markdown('#### Total Titles')
choropleth = make_choropleth(df, 'country', 'show_id', 'plasma')
st.plotly_chart(choropleth, use_container_width=True)

heatmap_data = df.groupby(['release_year', 'country']).size().reset_index(name='title_count')
heatmap = make_heatmap(heatmap_data, 'release_year', 'country', 'title_count', 'plasma')
st.altair_chart(heatmap, use_container_width=True)

st.markdown('#### Top Countries')
top_countries_df = df['country'].value_counts().reset_index()
top_countries_df.columns = ['Country', 'Title Count']
st.dataframe(top_countries_df, hide_index=True)

with st.expander('About', expanded=True):
    st.write('''
        - Data: Netflix dataset
        - :orange[**Most Content-Producing Countries**]: Top countries by number of Netflix titles
        - :orange[**Content Trends**]: Distribution of titles across different years
        ''')