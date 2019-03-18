import requests
import quandl
import pandas as pd
from flask import Flask, render_template, request, redirect
from datetime import date
from dateutil.relativedelta import relativedelta

from bokeh.plotting import figure, show, output_notebook
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, Range1d, HoverTool, CrosshairTool
from bokeh.embed import components

app = Flask(__name__)

quandl.ApiConfig.api_key = "p6zssrRQ9n4wG-fJWErU"


# Define date month ago:
monthago = date.today() + relativedelta(months=-1)
monthago = monthago.strftime("%Y-%m-%d")
# Define date today:
today = date.today()
today = today.strftime("%Y-%m-%d")

def get_ticker(ticker):
    """Retrieve and process Quandl data for given ticker symbol.

    Retrieves the last month of closing price data for the given ticker
    symbol. Returns a pandas DataFrame.
    """
    # Retrieve and process data
    

    data = quandl.get_table('WIKI/PRICES', ticker = ticker, 
                        qopts = { 'columns': ['date', 'adj_close'] }, 
                        date = { 'gte': '2018-02-18', 'lte': today }, 
                        paginate=True)
    
    df = pd.DataFrame(data, columns=['date','adj_close'])

    df['date'] = pd.to_datetime(df['date'])
    df['date_str'] = df['date'].map(lambda x: x.strftime("%Y-%m-%d"))
#    dfcds = ColumnDataSource(df)
    
    return df
    

def bokehplot(df, ticker):
    """Create a time-series line plot in Bokeh."""
    p = figure(width=600, height=300, title=ticker.upper(), tools="")

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

    p.line('date', 'adj_close', source = df)

    p.xaxis.formatter=DatetimeTickFormatter(days=["%d %b"])
    p.x_range=Range1d(df['date'].min(), df['date'].max())

    p.toolbar.logo = None
    p.toolbar_location = None


#    # Style plot
#    p.background_fill_color = "#234567"
#    p.border_fill_color = "#234567"
#    p.title.text_color = "#ffffff"
#    p.title.text_font_size = "1.25em"
#    p.axis.major_label_text_color = "#ffffff"
#    p.axis.major_label_text_font_size = "0.875em"
#    p.axis.axis_line_color = "#ffffff"
#    p.axis.major_tick_line_color = "#ffffff"
#    p.axis.minor_tick_line_color = "#ffffff"
#    p.xgrid.grid_line_color = None
#    p.ygrid.grid_line_alpha = 0.5
#    p.ygrid.grid_line_dash = [4, 6]
#    p.outline_line_color = None
#    p.yaxis.axis_label = "Closing price"
#    p.yaxis.axis_label_text_color = "#ffffff"
#    p.yaxis.axis_label_text_font_size = "1em"
#    p.yaxis.axis_label_text_font_style = "normal"
#    p.yaxis.axis_label_standoff = 12
#    
#    return p

    
def invalid():
    error = None
    with open("static/error.html") as err:
        error = err.read()
    return render_template(
        'index.html',
        bokeh_script="",
        bokeh_div=error)

# Main HTML Interface:
    
@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', bokeh_script="", bokeh_div="")
    else:
        ticker = request.form['ticker_text']
        if not ticker.isalpha():
            return invalid()
        ticker_df = get_ticker(ticker)
        if ticker_df.empty:
            return invalid()
        fig = bokehplot(ticker_df, ticker)
        script, div = components(fig)
        return render_template(
            'index.html',
            bokeh_script=script,
            bokeh_div=div)

if __name__ == '__main__':
    app.run(port=33507)
