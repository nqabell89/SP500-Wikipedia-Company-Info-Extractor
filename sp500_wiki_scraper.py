import pandas as pd
import html5lib
from bs4 import BeautifulSoup
import requests

# In two lines of code, instantly scrape the entire S&P500 List from Wikipedia into a Pandas DataFrame;
ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
df = ticker_list[0]

# Drop a few unwanted columns of data;
df.drop(columns = ['SEC filings', 'Date first added', 'Founded'], inplace = True)

# Fill out CIK codes by converting to string then adding in 0's up to 10 digits.
df.CIK = df.CIK.astype(str)
df['CIK'] = df['CIK'].str.zfill(10)

# Rename columns;
df.rename(columns = {'Symbol':'TICKER', 'Security':'COMPANY', 'GICS Sector':'GICS_SECTOR',
                     'GICS Sub Industry':'GICS_INDUSTRY', 'Headquarters Location':'HQ'}, inplace = True)

# Use BeautifulSoup to scrape individual wikipedia page urls for each ticker;
request = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
df['WIKI_URL'] = ''
soup = BeautifulSoup(request.content)
main_table = soup.find(id='constituents')
table = main_table.find('tbody').findAll('tr')
table = table[1:]

base_url = 'https://en.wikipedia.org'
url_list = []
for item in table:
    url = base_url + str(item.findAll('a')[1]['href'])
    url_list.append(url)
    
df['WIKI_URL'] = url_list


# Define function to scrape the infobar on the right side of the company page, like "Products";
def products_extractor(url):

    output = 'none' # return none if field doesn't exist
    vcard_list = pd.read_html(url)
    df = vcard_list[0]
    
    if len(df.columns) == 2:
        df.columns = ['columns', 'data']
        # most output tables have 2 elements
    else:
        df.columns = ['columns', 'data', 'trash']
        df.drop(columns = 'trash', inplace = True)
        # sometimes the table output has 3 elements
    
    # some table cleaning is needed before transposing
    df.set_index(df['columns'], inplace = True)
    df.drop(columns = 'columns', inplace = True)
    df = df.transpose()
    
    # extract 'products' field from company profile card;
    if 'Products' in df.columns:
        output = df['Products'][0]
    
    return output

# Apply function to entire list of company urls and create new column for output;
df['PRODUCTS'] = df['WIKI_URL'].apply(products_extractor)