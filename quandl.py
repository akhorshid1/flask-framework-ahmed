import requests
import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, \
    Range1d, HoverTool, CrosshairTool

apikey = 'U2BEMNCEBODUY397'

urlhead = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='
urldate = '&date='
urltail = '&apikey=' + apikey

    
monthago = date.today() + relativedelta(years=-1)
date = monthago.strftime("%Y-%m-%d")


def plot_ticker(ticker):
    # Retrieve and process data:
    
    url = urlhead + ticker + urltail
    page = requests.get(url)
    json = page.json()
    df = pd.DataFrame(json['Time Series (Daily)'])
    
    # New DataFrame to append values:
    df_1 = pd.DataFrame()
    close = np.asarray(df.iloc[3])
    
    df_1['date'] = pd.to_datetime(list(df))
    df_1['close'] = close
    
    # Last 30 days:
    df_1 = df_1[0:30]
    
    # Create a new column with dates as string:
    df_1['date_str'] = df_1['date'].map(lambda x: x.strftime("%Y-%m-%d"))
    dfcds = ColumnDataSource(df_1)
    
    # Create Bokeh plot:
    p = figure(width=600, height=300, title=ticker.upper(), tools="")

    hover = HoverTool(tooltips = [
        ('Date', '@date_str'),
        ('Close', '@close')])
    
    hover.mode = 'vline'
    hover.line_policy = 'nearest'
    p.add_tools(hover)

    crosshair = CrosshairTool()
    crosshair.dimensions = 'height'
    p.add_tools(crosshair)

    p.line('date', 'close', source =  dfcds)

    p.xaxis.formatter=DatetimeTickFormatter(days=["%d %b"])
    p.x_range=Range1d(df_1['date'].min(), df_1['date'].max())

    p.toolbar.logo = None
    p.toolbar_location = None

    return p

output_notebook()
fig = plot_ticker('AAPL')
show(fig)


