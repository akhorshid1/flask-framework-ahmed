import requests
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect
from datetime import date
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, Range1d, HoverTool, CrosshairTool
from bokeh.embed import components

app = Flask(__name__)

apikey = 'U2BEMNCEBODUY397'

urlhead = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='
urldate = '&date='
urltail = '&apikey=' + apikey

    
monthago = date.today() + relativedelta(years=-1)
date = monthago.strftime("%Y-%m-%d")

def get_ticker(ticker):
     
    # Retrieve and process data:
    url = urlhead + ticker + urltail    
    
    try:
        page = requests.get(url)
        json = page.json()
    except ValueError:
        return pd.DataFrame()
    df = pd.DataFrame(json['Time Series (Daily)'])
    
    # New DataFrame to append values:
    df_1 = pd.DataFrame()
    close = np.asarray(df.iloc[3])
    
    df_1['date'] = pd.to_datetime(list(df))
    df_1['close'] = close
    
    # Last 30 days:
    df_1 = df_1[0:30]
    
    # Create a new column with dates and close as string:
    df_1['date_str'] = df_1['date'].map(lambda x: x.strftime("%Y-%m-%d"))
    
    return df_1

def bokehplot(df_1, ticker):
    """Create a time-series line plot in Bokeh."""
    p = figure(width=600, height=300, title=ticker.upper(), tools="")
    

    hover = HoverTool(tooltips = """
    <div>
    <table>
    <tr><td class="ttlab">Date:</td><td>@date_str</td></tr>
    <tr><td class="ttlab">Close:</td><td>@close</td></tr>
    </table>
    </div>
    """)
    
    hover.mode = 'vline'
    hover.line_policy = 'nearest'
    p.add_tools(hover)

    crosshair = CrosshairTool()
    crosshair.dimensions = 'height'
    crosshair.line_color = "#ffffff"
    p.add_tools(crosshair)

    dfcds = ColumnDataSource(df_1)
    p.line('date', 'close', source = dfcds, color="#44ddaa")

    p.xaxis.formatter=DatetimeTickFormatter(days=["%d %b"])
    p.x_range=Range1d(df_1['date'].min(), df_1['date'].max())

    p.toolbar.logo = None
    p.toolbar_location = None

    # Style plot
    p.background_fill_color = "#234567"
    p.border_fill_color = "#234567"
    p.title.text_color = "#ffffff"
    p.title.text_font_size = "1.25em"
    p.axis.major_label_text_color = "#ffffff"
    p.axis.major_label_text_font_size = "0.875em"
    p.axis.axis_line_color = "#ffffff"
    p.axis.major_tick_line_color = "#ffffff"
    p.axis.minor_tick_line_color = "#ffffff"
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_alpha = 0.5
    p.ygrid.grid_line_dash = [4, 6]
    p.outline_line_color = None
    p.yaxis.axis_label = "Closing price"
    p.yaxis.axis_label_text_color = "#ffffff"
    p.yaxis.axis_label_text_font_size = "1em"
    p.yaxis.axis_label_text_font_style = "normal"
    p.yaxis.axis_label_standoff = 12
    
    return p

def invalid():
    error = None
    with open("static/error.html") as err:
        error = err.read()
    return render_template(
        'index.html',
        bokeh_script="",
        bokeh_div=error)

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', bokeh_script="", bokeh_div="")
    else:
        tick = request.form['ticker_text']
        if not tick.isalpha():
            return invalid()
        ticker_df = get_ticker(tick)
        if ticker_df.empty:
            return invalid()
        
        fig = bokehplot(ticker_df, tick)
        script, div = components(fig)
        return render_template(
            'index.html',
            bokeh_script=script,
            bokeh_div=div)

if __name__ == '__main__':
    app.run(port=33507)
