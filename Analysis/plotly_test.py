import plotly.graph_objs as go
import numpy as np
from ipywidgets import interact
from plotly import offline
offline.init_notebook_mode()


#%%

fig = go.FigureWidget()
scatt = fig.add_scatter()
fig
xs=np.linspace(0, 6, 100)

#%%
@interact(a=(1.0, 4.0, 0.01), b=(0, 10.0, 0.01), color=['red', 'green', 'blue'])
def update(a=3.6, b=4.3, color='blue'):
    with fig.batch_update():
        scatt.x=xs
        scatt.y=np.sin(a*xs-b)
        scatt.line.color=color
#%%
from plotly import offline
offline.init_notebook_mode()

offline.iplot([{"y": [1, 2, 1]}])
