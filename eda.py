import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstores", page_icon=":bar_chart:", layout="wide")

st.title(" :bar_chart: Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

f1 = st.file_uploader(":file_folder: Upload a file", type=(['csv','txt','xlsx','xls']))
if f1 is not None:
    filename = f1.name
    st.write(filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
    
    df = pd.read_excel("superstore.xls", engine="xlrd")    

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"]) 

# creating the min and max date
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input('Start Date', startDate))

with col2:
    date1 = pd.to_datetime(st.date_input('End Date', endDate))

st.sidebar.header('Choose your filter: ') 
# Crete for Region 
region = st.sidebar.multiselect('pick your region', df['Region'].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]    

# Create for state
state = st.sidebar.multiselect('Pick your State', df2['State'].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]   

# create for city
city =st.sidebar.multiselect('Pick your City', df3['City'].unique())   
#filter the data based on region, state and city

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df['Region'].isin(region)]
elif not region and not city:
    filtered_df = df[df['State'].isin(state)]   
elif state and city:
    filtered_df = df3[df['State'].isin(state) & df3['City'].isin(city)]
elif region and city:
    filtered_df = df3[df['Region'].isin(region) & df3['City'].isin(city)]
elif region and state:
    filtered_df = df3[df['Region'].isin(region) & df3['State'].isin(state)]
elif city:
    filtered_df = df3[df3['City'].isin(city)]
else:
    filtered_df = df3[df3['Reion'].isin(region) & df3['State'].isin(state) & df3['City'].isin(city)]  

category_df = filtered_df.groupby(by = ['Category'], as_index=False)['Sales'].sum()

with col1:
    st.subheader('Category wise sales')
    fig = px.bar(category_df, x='Category', y = 'Sales', text=['${:,.2f}'.format(x)for x in category_df['Sales']],
                 template= 'seaborn')
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader('Region wise sales')
    fig = px.pie(filtered_df, values='Sales', names='Region',hole=0.5)
    fig.update_traces(text = filtered_df['Region'], textposition= 'outside')
    st.plotly_chart(fig, use_container_width=True)

#stopped at min 32
cl1, cl2 = st.columns(2)
with cl1:
    with st.expander('Category_viewData'):
        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data',data = csv, file_name = "Category.csv", mime = 'text/csv',
                           help= 'click here to download the data as cvs file')

with cl2:
    with st.expander('Region_viewData'):
        region = filtered_df.groupby(by='Region',as_index= False)['Sales'].sum()
        st.write(region.style.background_gradient(cmap='Blues'))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data',data = csv, file_name = "region.csv", mime = 'text/csv',
                           help= 'click here to download the data as cvs file')
        
filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M') 
st.subheader('Time series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y : %b'))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = 'month_year', y = 'Sales', labels = {'Sales': "Amount"}, height = 500, width = 1000, template = 'gridon')
st.plotly_chart(fig2, use_container_width=True)

with st.expander('View Data of Time Series:'):
    st.write(linechart.T.style.background_gradient(cmap='blues'))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data = csv, file_name= "Timeseries.csv", mime= 'text/csv')

# creating a tree map based pn region, category, sub-category
st.subheader('hierachical view of sales using Treemap')
fig3 = px.treemap(filtered_df, path=["Region","Category","Sub-Category"],values='Sales',hover_data=['Sales'],
                  color='Sub-Category')
fig3.update_layout(width=800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns(2)
with chart1:
    st.subheader('Segment Wise Sales')
    fig = px.pie(filtered_df, values='Sales', names = 'Segment', template='plotly_dark')
    fig.update_traces(text = filtered_df['Segment'],textposition = 'inside')
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category Wise Sales')
    fig = px.pie(filtered_df, values='Sales', names = 'Category', template='plotly_dark')
    fig.update_traces(text = filtered_df['Category'],textposition = 'inside')
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(':point_right: Month wise Sub-Category Sales Summery')
with st.expander("Summery_Table"):
    df_sample = df[0:5][['Region', 'State','City','Category','Sales','Profit','Quantity']]
    fig = ff.create_table(df_sample,colorscale='cividis')
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('Month wise Sub-Category Table')
    filtered_df['month'] = filtered_df['Order Date'].dt.month_name()
    sub_category_year = pd.pivot_table(data = filtered_df,values = 'Sales', index = ['Sub-Category'],columns='month')
    st.write(sub_category_year.style.background_gradient(cmap='Blues'))

#create a scattered plot

