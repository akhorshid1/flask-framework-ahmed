import requests
import quandl
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, Range1d, HoverTool, CrosshairTool

quandl.ApiConfig.api_key = "p6zssrRQ9n4wG-fJWErU"


# Define date month ago:
monthago = date.today() + relativedelta(months=-1)
monthago = monthago.strftime("%Y-%m-%d")
# Define date today:
today = date.today()
today = today.strftime("%Y-%m-%d")



def plot_ticker(ticker):
    # Retrieve and process data
    

    data = quandl.get_table('WIKI/PRICES', ticker = ticker, 
                        qopts = { 'columns': ['date', 'adj_close'] }, 
                        date = { 'gte': '2018-02-18', 'lte': today }, 
                        paginate=True)
    
    df = pd.DataFrame(data, columns=['date','adj_close'])

    df['date'] = pd.to_datetime(df['date'])
    df['date_str'] = df['date'].map(lambda x: x.strftime("%Y-%m-%d"))
    dfcds = ColumnDataSource(df)
    
    # Create Bokeh plot
    p = figure(width=600, height=300, title=ticker.upper(), tools="")

    hover = HoverTool(tooltips = [
        ('Date', '@date_str'),
        ('Close', '@adj_close')
    ])
    hover.mode = 'vline'
    hover.line_policy = 'nearest'
    p.add_tools(hover)

    crosshair = CrosshairTool()
    crosshair.dimensions = 'height'
    p.add_tools(crosshair)

    p.line('date', 'adj_close', source = dfcds)

    p.xaxis.formatter=DatetimeTickFormatter(days=["%d %b"])
    p.x_range=Range1d(df['date'].min(), df['date'].max())

    p.toolbar.logo = None
    p.toolbar_location = None

    return p

output_notebook()
fig = plot_ticker('AAPL')
show(fig)

