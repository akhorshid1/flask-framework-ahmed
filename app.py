import requests
import pandas as pd
from flask import Flask, render_template, request, redirect
from datetime import date
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, \
    Range1d, HoverTool, CrosshairTool
from bokeh.embed import components

app = Flask(__name__)

apikey = "p6zssrRQ9n4wG-fJWErU"

urlhead = "https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker="
urldate = "&date.gte="
urlcols = "&qopts.columns="
urltail = "&api_key=" + apikey

monthago = date.today() + relativedelta(months=-1)
date = monthago.strftime("%Y-%m-%d")

cols = "date,adj_close"

def get_ticker(ticker):
    """Retrieve and process Quandl data for given ticker symbol.

    Retrieves the last month of closing price data for the given ticker
    symbol. Returns a pandas DataFrame.
    """
#    url = urlhead + ticker + urldate + date + urlcols + cols + urltail
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker=AAPL&date.gte=2018-02-18&qopts.columns=date,adj_close&api_key=p6zssrRQ9n4wG-fJWErU'

    try:
        page = requests.get(url)
        json = page.json()
    except ValueError:
        return pd.DataFrame()
    df = pd.DataFrame(json['datatable']['data'], columns=['date','adj_close'])
    df['date'] = pd.to_datetime(df['date'])
    df['date_str'] = df['date'].map(lambda x: x.strftime("%Y-%m-%d"))
    df['close_str'] = df['adj_close'].map(lambda x: '{:,.2f}'.format(x))
    
    return df

def bokehplot(df, ticker):
    """Create a time-series line plot in Bokeh."""
    p = figure(width=600, height=300, title=ticker.upper(), tools="")

    hover = HoverTool(tooltips = """
    <div>
    <table>
    <tr><td class="ttlab">Date:</td><td>@date_str</td></tr>
    <tr><td class="ttlab">Close:</td><td>@close_str</td></tr>
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

    dfcds = ColumnDataSource(df)
    p.line('date', 'adj_close', source = dfcds, color="#44ddaa")

    p.xaxis.formatter=DatetimeTickFormatter(days=["%d %b"])
    p.x_range=Range1d(df['date'].min(), df['date'].max())

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
