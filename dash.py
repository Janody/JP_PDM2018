import visualisation as vs
import pandas as pd
import numpy as np
from bokeh.models import Select, ColumnDataSource
from bokeh.models.widgets import Panel, Tabs, CheckboxGroup
from bokeh.io import output_file, show, push_notebook, output_notebook
from bokeh.plotting import figure
from bokeh.layouts import layout, row, column, widgetbox


class Plot(object):
    def  __init__(self, name, debtot, debhor, heatmap):
        self.name = name
        self.debtot = debtot #plot des débits totaux sur la période
        self.debhor = debhor #plot des débits horaires moyens
        self.heatmap = heatmap #plot des heatmaps


def genSources(df):
    data = df.copy()
    source = ColumnDataSource(data=data) #débits bruts


    if 'Date' in data.columns:
        datam = data.copy()
        dfmoy = datam.groupby(datam['Date'].dt.hour)
        source2 = ColumnDataSource(data = dfmoy) #débits moyens


    return source, source2


def genPlots(df, user, type):

    source1, source2 = genSources(df)

    if user == "pietons":
        deb1, deb2 = vs.pedplot(source1, source2)
        hm = vs.ped_heatmap(df)

    elif user =="vehicules":
        deb1,deb2 = vs.vehplot(source1, source2)
        hm = vs.veh_heatmap(df)

    elif user =="swisscom":
        deb1,deb2=vs.scplot(source1, source2)
        hm = vs.sc_heatmap(df)

    elif user =="tl":
        deb1, deb2 = vs.tlplot(source1, source2)
        hm = None

    plots = Plot(user,deb1,deb2,hm)

    if type == "debits":
        out = [plots.debtot, plots.debhor]
    elif type == "heatmap":
        out = plots.heatmap

    return out

def genAll(dfped, dfveh, dfsc,dftl):
    sourceped, moyped = genSources(dfped)
    sourceveh, moyveh = genSources(dfveh)
    sourcesc, moysc = genSources(dfsc)
    sourcetl,moytl = genSources(dftl)

    tot = pd.DataFrame(dfped.Total + dftl.Total + np.multiply(dfveh.Total,1.1))
    tot['Date'] = dfped.Date

    sourcetot,moytot = genSources(tot)

    deb1 = vs.totplots(sourceped, sourceveh, sourcesc, sourcetl, sourcetot)
    deb2 = vs.totplotsmoy(moyped, moyveh, moysc, moytl, moytot)

    out = [deb1, deb2]

    return out


def genStats(dfped, dfveh, dfswiss, dftl):

    output_file("trafic.html")

    #graphiques

    piet1, piet2 = genPlots(dfped,"pietons","debits")
    veh1, veh2 = genPlots(dfveh, "vehicules", "debits")
    sc1, sc2 = genPlots(dfswiss, "swisscom", "debits")
    tl1, tl2 = genPlots(dftl, "tl", "debits")
    tot1, tot2 = genAll(dfped, dfveh, dfswiss,dftl)

    hmp = genPlots(dfped,"pietons","heatmap")
    hmv = genPlots(dfveh, "vehicules", "heatmap")
    hms = genPlots(dfswiss, "swisscom", "heatmap")

    p_grid = row(piet1, piet2)
    v_grid = row(veh1,veh2)
    s_grid = row(sc1,sc2)
    tl_grid = row(tl1,tl2)
    tot_grid = row(tot1,tot2)
    hm_grid = column(hmp, hmv, hms)

    #tabs
    tab1 = Panel(child=p_grid, title="Piétons")
    tab2 = Panel(child=v_grid, title="Voitures")
    tab3 = Panel(child=s_grid, title="Swisscom")
    tab4 = Panel(child=tl_grid, title="TL")
    tab5 = Panel(child=tot_grid, title="Total")
    tab6 = Panel(child=hm_grid, title="Heatmaps")

    tabs = Tabs(tabs=[tab1, tab2, tab3, tab4, tab5, tab6])

    show(tabs)

    return None



