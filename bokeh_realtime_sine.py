from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource
from bokeh.io import curdoc
import numpy as np

source = ColumnDataSource(dict(x=[], y=[], avg=[]))

fig = Figure()
fig.line(source=source, x='x', y='y', line_width=2, alpha=.85, color='red')
fig.line(source=source, x='x', y='avg', line_width=2, alpha=.85, color='blue')

# prepare some data
ct = 0
sine_sum = 0


def update_data():
    global ct, sine_sum
    ct += 1
    sine = np.sin(ct)
    sine_sum += sine
    new_data = dict(x=[ct], y=[sine], avg=[sine_sum/ct])
    source.stream(new_data, 100)

# show the results
curdoc().add_root(fig)
curdoc().add_periodic_callback(update_data, 100)