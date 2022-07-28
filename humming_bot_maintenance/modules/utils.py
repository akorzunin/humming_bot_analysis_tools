import ipywidgets as widgets
from IPython.display import display


def get_filled_df_from_local(locals_):
    local_df = locals_["df"]
    filled_df = local_df.loc[local_df["end_reason"] == "filled"]
    return filled_df.reset_index(drop=1)

def get_filled_df(df):
    filled_df = df.loc[df["end_reason"] == "filled"]
    return filled_df.reset_index(drop=1)

def setup_ui(df):
    out = widgets.Output()
    out.layout.width = "5000px"
    with out:
        display(df)
    return out


import plotly

plotly.offline.init_notebook_mode()
from plotly.offline import iplot


def plot_fig(fig):
    out = widgets.Output()
    fig.update_layout(
        width=1200,
        height=700,
    )
    with out:
        iplot(fig)
        return out
