import geopandas
import contextily as cx
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point
from matplotlib.widgets import Slider, CheckButtons, RadioButtons
import os

if __name__ == '__main__':
    cwd = os.getcwd()
    Data = pd.read_pickle(cwd + r'\Boston_Commute.pkl')
    Data = geopandas.GeoDataFrame(Data)
    Targets = pd.read_pickle(cwd + r'\Target_Destinations.pkl')
    Targets = geopandas.GeoDataFrame(Targets)
    V = geopandas.read_file(cwd + r"\MA_Data\TOWNSSURVEY_POLY.shp")
    MA = V.to_crs(epsg=3857)

    # Setup
    fig, ax = plt.subplots(figsize=(8,6))
    plt.rc('text', usetex=True)
    fig.suptitle(r'{\huge Commutes around}' +'\n' + \
                 r'{\huge Boston}' + '\n' + \
                 'Dashed lines are town boundaries' + '\n' + \
                 'Solid lines are roads/highways',
                 x=0.02, y=0.9, horizontalalignment='left')
    ax.set(ylim=(5.18*1e6, 5.26*1e6), xlim=(-7.98*1e6, -7.90*1e6),
           xticklabels=[], yticklabels=[])
    ax.set_title('Click for town name', fontsize=8)

    global col
    col = 'time_to_W'

    Ann = ax.annotate('Last Town Selected:\nNone Selected Yet',
                      (0.02,0.3), xycoords='figure fraction', fontsize=14)

    A = Data.plot(column='time_to_W', cmap='hot_r', ax=ax, 
                  markersize=300, legend=True, legend_kwds={'shrink': 0.8},
                  alpha=0.05)
    B = MA.geometry.boundary.plot(color=None, edgecolor='b',
                              linewidth=1, linestyle=':',
                              alpha=0.5, ax=ax)
    w = cx.add_basemap(ax, source=cx.providers.Stamen.TonerLines)
    w = cx.add_basemap(ax, source=cx.providers.Stamen.Terrain)
    # w = cx.add_basemap(ax, source=cx.providers.Stamen.Toner)
    Targets.plot(marker='x', color='g', markersize=300, linewidths=3, ax=ax)

    fig.get_axes()[0].set_position([0.28, 0.2, 0.6, 0.75])
    fig.get_axes()[1].set_position([0.91, 0.2, 0.05, 0.75])

    # Sliders
    def update(val):
        # Get rid of old coloring
        v = ax.get_children()
        for i in v:
            if 'matplotlib.collections.PathCollection' in str(type(i)):
                i.remove()
        # Get rid of old colorbar, which is on its own axis
        Q = fig.get_axes()
        for i in Q:
            if 'colorbar' in i.get_label():
                i.remove()
        Data[(Data['time_to_W'] < W_Slider.val) & \
             (Data['time_to_NR'] < NR_Slider.val) & \
             (Data['time_to_SS'] < SS_Slider.val)].plot(
                column=col, cmap='hot_r', legend=True,
                markersize=300, legend_kwds={'shrink': 0.8},
                ax=ax, alpha=0.05)
        # Reshape ax to its pre-shrunk (for colorbar) size
        z = fig.get_axes()
        for i in z:
            if i.get_label() == '':
                i.set_position([0.28, 0.2, 0.6, 0.75])
            elif 'colorbar' in i.get_label():
                i.set_position([0.91, 0.2, 0.05, 0.75])
        Targets.plot(marker='x', color='g', markersize=300,
                     linewidths=3, ax=ax)
        fig.canvas.draw_idle()

    ax_W_Slider = plt.axes([0.25, 0.13, 0.65, 0.03],
                           facecolor='b', label='Slider1')
    W_Slider = Slider(ax_W_Slider, 'Max time to Westborough', 5, 100,
                      valinit=100, valstep=1)
    W_Slider.on_changed(update)

    ax_NR_Slider = plt.axes([0.25, 0.09, 0.65, 0.03],
                            facecolor='b', label='Slider2')
    NR_Slider = Slider(ax_NR_Slider, 'Max time to N. Reading', 5, 100,
                      valinit=100, valstep=1)
    NR_Slider.on_changed(update)

    ax_SS_Slider = plt.axes([0.25, 0.05, 0.65, 0.03],
                            facecolor='b', label='Slider3')
    SS_Slider = Slider(ax_SS_Slider, 'Max time to S. Station', 5, 100,
                      valinit=100, valstep=1)
    SS_Slider.on_changed(update)

    # Radio buttons
    ax_Radio = plt.axes([0.02, 0.43, 0.2, 0.15], facecolor='w', label='radio')
    Radio_bottom = ax_Radio.bbox.extents[1]
    Radio_top = ax_Radio.bbox.extents[-1]
    Radio_0_coord = (Radio_top - Radio_bottom) / 3 + Radio_bottom
    Radio_2_coord = 2*(Radio_top - Radio_bottom) / 3 + Radio_bottom
    ax_Radio.set_title('Color by\nminutes to...', fontsize=12, loc='left')
    radio = RadioButtons(ax_Radio, ('Westborough',
                                    'North Reading',
                                    'South Station'), active=0)
    def change_colors(label):
        global col
        if label == 'Westborough':
            col = 'time_to_W'
        elif label == 'North Reading':
            col = 'time_to_NR'
        elif label == 'South Station':
            col = 'time_to_SS'
        update(0)

    radio.on_clicked(change_colors)

    def click(event):
        if event.inaxes==ax_Radio:
            global col
            if label == 'Westborough':
                col = 'time_to_W'
            elif label == 'North Reading':
                col = 'time_to_NR'
            elif label == 'South Station':
                col = 'time_to_SS'
            if event.y < Radio_0_coord:
                radio.set_active(0)
            elif event.y > Radio_0_coord and event.y < Radio_2_coord:
                radio.set_active(1)
            else:
                radio.set_active(2)
        elif event.inaxes==ax:
            p = Point((event.xdata, event.ydata))
            for i in range(len(MA)):
                if MA.iloc[i]['geometry'].contains(p):
                    town = MA.iloc[i]['TOWN'].lower()
                    town = town[0].upper() + town[1:]

            Ann.set_text('Last Town Selected:\n'+town)
            fig.canvas.draw_idle()
    cid = Ann.figure.canvas.mpl_connect('button_press_event', click)
    
    plt.show()