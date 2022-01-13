import pandas as pd
import numpy as np
import random
from datetime import datetime as dt
from bokeh.io import output_file, show
from bokeh.layouts import gridplot, layout
from bokeh.palettes import Category20
from bokeh.plotting import figure, curdoc
from bokeh.models import (ColumnDataSource, CDSView, RadioButtonGroup, GroupFilter, DataTable,
                          TableColumn, DateFormatter, CategoricalColorMapper, CheckboxGroup,
                          TextInput, Column, Row, Div, HoverTool, Slider, RangeSlider, MultiChoice, Select)
# Read the data:
data = pd.read_csv('avocado.csv')
# Format the Date variable to datetime and sort the data by Date:
data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
data.sort_values(by='Date', ascending=True, inplace=True)
# Create the month and year variables:
data['Month'] = pd.to_datetime(data['Date']).dt.month
data['Year'] = pd.to_datetime(data['Date']).dt.year

# INITIAL VARIABLES:
# Create a sorted list of ticker region:
tickers = sorted(list(data.region.unique()))
# Creat a sorted list of months:
month = sorted(list(data.Month.unique()))
# Creat a sorted list of years:
year = sorted(list(data.Year.unique()))
# Create a sorted list od type
t = sorted(list(data.type.unique()))

# WIDGETS:
# Initialize the ticker choice:
ticker_button = Select(title="Region", value=tickers[0], options=tickers)
# Initialize the year slider:
year_slider = Slider(start=year[0], end=year[-1], value=year[1], step=1, title='Year')
# Initialize the month range slider:
month_slider = RangeSlider(start=month[0], end=month[-1], value=month[:2], step=1, title='Month')
# Initialize the type:
type_select= Select(title="Type", value=t[0], options=t)


# Filter the initial data source:
df = data[(data['region']==ticker_button.value) & (data['Month'] >= month_slider.value[0]) & (data['Month'] <= month_slider.value[1]) & (data['Year'] == year_slider.value) & (data['type']==type_select.value)]
# Pass the filtered data source to the ColumnDataSource class:
source = ColumnDataSource(data =df)

# TABLE
# Creating the list of columns:
columns = [
        TableColumn(field="Date", title="Date", formatter=DateFormatter(format="%Y-%m-%d")),
        TableColumn(field="region", title="region"),
        TableColumn(field="AveragePrice", title="AveragePrice"),
        TableColumn(field="type", title="Type")
    ]
# Initializing the table:
table = DataTable(source=source, columns=columns, height=500)

# PLOT
def plot_function(tickers):
    # Getting some colors:
    colors = list(Category20.values())[17]
    random_colors = []
    for c in range(len(tickers)):
        random_colors.append(random.choice(colors))

    # Create the hovertool:
    TOOLTIPS = HoverTool(tooltips=[    ('Date', '$x{%Y-%m-%d}'),
                   ('AvgPrice', '$@{AveragePrice}'),
                   ('Total Volume', '$@{TotalVolume}'),
                   ('Total Bags', '$@{TotalBags}')],
                         formatters={'$x': 'datetime'})

    # Create the figure to store all the plot lines in:
    p = figure(x_axis_type='datetime', width=1000, height=500)

    # Loop through the tickers and colors and create plot line for each:
    for t, rc in zip(tickers, random_colors):
        view = CDSView(source=source, filters=[GroupFilter(column_name='region', group=t)])
        p.scatter(x='Date', y='AveragePrice', source=source, view=view, line_color=rc, line_width=4)
        p.line(x='Date', y='AveragePrice', source=source, view=view, line_color=rc, line_width=4)

    # Add the hovertool to the figure:
    p.add_tools(TOOLTIPS)
    return p
p = plot_function(tickers)

def text_function(attr, old, new):
    new_text = new
    old_text = old
    text_data = pd.read_json('text_data.json')

def filter_function():
    # Filter the data according to the widgets:
    new_src = data[(data['region']==ticker_button.value) & (data['Month'] >= month_slider.value[0]) & (data['Month'] <= month_slider.value[1]) & (data['Year'] == year_slider.value) & (data['type']==type_select.value)]

    # Replace the data in the current data source with the new data:
    source.data = new_src.to_dict('series')

def change_function(attr, old, new):
    filter_function()

ticker_button.on_change('value' ,change_function)
month_slider.on_change('value', change_function)
year_slider.on_change('value', change_function)
type_select.on_change('value', change_function)

# Header
title = Div(text='<h1 style="text-align: center">Avocado Average Price</h1>')

widgets_col = Column(month_slider, year_slider)
widgets_row = Row(widgets_col, ticker_button, type_select)
layout = layout([[title],
                 [widgets_row],
                 [p,table]])
curdoc().title = 'Avocado Average Price'
curdoc().add_root(layout)