import requests
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, \
    Range1d, HoverTool, CrosshairTool

apikey = "E456SMCHeyee8d_sF4Sv"

urlhead = "https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker="
urldate = "&date.gte="
urlcols = "&qopts.columns="
urltail = "&api_key=" + apikey

monthago = date.today() + relativedelta(months=-1)
date = monthago.strftime("%Y%m%d")

cols = "date,close"

def plot_ticker(ticker):
    # Retrieve and process data
    url = urlhead + ticker + urldate + date + urlcols + cols + urltail
    page = requests.get(url)
    json = page.json()
    df = pd.DataFrame(json['datatable']['data'], columns=['date','close'])
    df['date'] = pd.to_datetime(df['date'])
    df['date_str'] = df['date'].map(lambda x: x.strftime("%Y-%m-%d"))
    dfcds = ColumnDataSource(df)
    
    # Create Bokeh plot
    p = figure(width=600, height=300, title=ticker.upper(), tools="")

    hover = HoverTool(tooltips = [
        ('Date', '@date_str'),
        ('Close', '@close')
    ])
    hover.mode = 'vline'
    hover.line_policy = 'nearest'
    p.add_tools(hover)

    crosshair = CrosshairTool()
    crosshair.dimensions = 'height'
    p.add_tools(crosshair)

    p.line('date', 'close', source = dfcds)

    p.xaxis.formatter=DatetimeTickFormatter(days=["%d %b"])
    p.x_range=Range1d(df['date'].min(), df['date'].max())

    p.toolbar.logo = None
    p.toolbar_location = None

    return p

output_notebook()
fig = plot_ticker('goog')
show(fig)

