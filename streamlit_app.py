import streamlit as st 
import pandas as pd
from datetime import datetime
from app.databaseconnection import database_query
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode


todays_date = datetime.now().date()
st.set_page_config(layout="wide")
# try: df = pd.DataFrame(database_query('select * from cleaned_data'))

# conn = st.connection("mysql", type="sql")
# df = conn.query('select * from all_time_listings')
df = pd.DataFrame(database_query('select * from all_time_listings'))
print(df.shape)
df.columns = ['Title', 'Department', 'Location', 'Salary', 'Closing Date', 'UID', 'URL', 'Full Text', 'scraped_date']
df['Salary'] = df['Salary'].fillna('0')
df['Salary_int'] = df['Salary'].str.replace(',', '').astype(int)
df['Salary'] = df['Salary'].str.replace('£', '').str.replace(',','').astype(int)
df['Closing Date filter'] = pd.to_datetime(df['Closing Date'])

max_sal = df['Salary_int'].max()

st.sidebar.title('Filters')
st.sidebar.subheader('Exclude closed jobs?')
closing_date_selector = st.sidebar.checkbox('Exclude', value=False)
st.sidebar.subheader('Job Title')
job_title_input = st.sidebar.text_input('Search for a job title').lower()
st.sidebar.subheader('Department')
department_input = st.sidebar.text_input('Search for a department').lower()
# st.sidebar.subheader('Date posted')
# date_input = st.sidebar.date_input('Search for a date posted')
st.sidebar.subheader('All text in ad')
all_text_input = st.sidebar.text_input('Search all text in ad for a keyword').lower()
st.sidebar.subheader('Location')
location_input = st.sidebar.text_input('Search for a location').lower()
st.sidebar.subheader('Salary range slider')
salary_range = st.sidebar.slider('Salary range', 0, max_sal, (0, max_sal))

if st.sidebar.button('Clear Filters'):
    job_title_input = ''
    department_input = ''
    all_text_input = ' '
    location_input = ''


# df = df[df['Title'].str.lower().str.contains(job_title_input) & df['Department'].str.lower().str.contains(department_input) &  
#         df['Location'].str.lower().str.contains(location_input) & df['Salary_int'].between(salary_range[0], salary_range[1])]
if closing_date_selector == False:
        df = df[
        df['Title'].str.lower().str.contains(job_title_input) 
        & 
        df['Department'].str.lower().str.contains(department_input) 
        & 
        df['Full Text'].str.lower().str.contains(all_text_input) 
        & df['Location'].str.lower().str.contains(location_input)
        & df['Salary_int'].between(salary_range[0], salary_range[1])
        ]
else:
        df = df[
        df['Title'].str.lower().str.contains(job_title_input) 
        & 
        df['Department'].str.lower().str.contains(department_input) 
        & 
        df['Full Text'].str.lower().str.contains(all_text_input) 
        & df['Location'].str.lower().str.contains(location_input)
        & df['Salary_int'].between(salary_range[0], salary_range[1])
        & (df['Closing Date filter'] >= pd.to_datetime(todays_date))
        ]

job_texts_containing_data = df.shape[0]
phrase_line = ''
if len(all_text_input)> 0:
        phrase_line = f'''Showing ads which contain the word "{all_text_input}"'''
else:
     phrase_line = ''

df = df.drop('Full Text', axis=1)
df = df.drop('UID', axis=1)
df = df.drop('Salary_int', axis=1)
df = df.drop('scraped_date', axis=1)
df = df.drop('Closing Date filter', axis=1)
number_of_vacancies = df.shape[0]
different_departments = df['Department'].nunique()
job_titles = df['Title'].nunique()
job_titles_containing_data = df['Title'].str.contains(job_title_input).sum()

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("URL",
                    headerName="URL",
                    cellRenderer=JsCode(
                        """
                        class UrlCellRenderer {
                                init(params) {
                                this.eGui = document.createElement('a');
                                this.eGui.innerText = 'Link';
                                this.eGui.setAttribute('href', params.value);
                                this.eGui.setAttribute('style', "text-decoration:none");
                                this.eGui.setAttribute('target', "_blank");
                                        }
                                getGui() {
                                return this.eGui;
                                        }
                                }       
                        """))
gb.configure_default_column(min_column_width=100)
gridOptions = gb.build()

st.write(f''' \n Some headline stats from the data: 
        
        Number of vacancies: {number_of_vacancies} 
        Across {different_departments} departments
        A range of {job_titles} job titles
        {phrase_line}  
         ''')
output_df = df[['Title', 'Department','Location', 'Salary', 'Closing Date', 'URL']]
AgGrid(output_df, gridOptions=gridOptions, height=600, allow_unsafe_jscode=True, allow_unsafe_html=True, width='100%')
