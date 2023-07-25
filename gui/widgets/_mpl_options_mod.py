"""
Module that provides a GUI-based editor for Matplotlib's figure options.


Licensed under the terms of the MIT License
see the Matplotlib licenses directory for a copy of the license
---------------------------------------------------------------

Copyright © 2009 Pierre Raybaut

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

# matplotlib 3.7.2 source code modification;
# File modified: ..\matplotlib\backends\qt_editor\figureoptions.py

from itertools import chain
from matplotlib import cbook, cm, colors as mcolors, markers, image as mimage, patches
from matplotlib.backends.qt_compat import QtGui
from matplotlib.backends.qt_editor import _formlayout
from matplotlib.dates import DateConverter, num2date

LINESTYLES = {'-': 'Solid',
              '--': 'Dashed',
              '-.': 'DashDot',
              ':': 'Dotted',
              'None': 'None',
              }

DRAWSTYLES = {
    'default': 'Default',
    'steps-pre': 'Steps (Pre)', 'steps': 'Steps (Pre)',
    'steps-mid': 'Steps (Mid)',
    'steps-post': 'Steps (Post)'}

MARKERS = markers.MarkerStyle.markers


def figure_edit(axes, parent=None):
    """Edit matplotlib figure options"""
    sep = (None, None)  # separator

    # Get / General
    def convert_limits(lim, converter):
        """Convert axis limits for correct input editors."""
        if isinstance(converter, DateConverter):
            return map(num2date, lim)
        # Cast to builtin floats as they have nicer reprs.
        return map(float, lim)

    axis_map = axes._axis_map
    axis_limits = {
        name: tuple(convert_limits(
            getattr(axes, f'get_{name}lim')(), axis.converter
        ))
        for name, axis in axis_map.items()
    }
    if 'labelsize' in axes.xaxis._major_tick_kw:                #modification v
        _ticksize = int(axes.xaxis._major_tick_kw['labelsize'])
    else:
        _ticksize = 10.0                                        #modification ^
    general = [
        ('Title', axes.get_title()),
        ('Title size', axes.title.get_fontsize()),       #modification v
        ('Label size', axes.xaxis.label.get_fontsize()),
        ('Tick size', _ticksize),
        ('Grid', axes.xaxis._major_tick_kw['gridOn']),   #modification ^
        sep,
        *chain.from_iterable([
            (
                (None, f"<b>{name.title()}-Axis</b>"),
                ('Min', axis_limits[name][0]),
                ('Max', axis_limits[name][1]),
                ('Label', axis.get_label().get_text()),
                ('Scale', [axis.get_scale(),
                           'linear', 'log', 'symlog', 'logit']),
                sep,
            )
            for name, axis in axis_map.items()
        ]),
        #('(Re-)Generate automatic legend', False),      #source commented <
    ]

    # Save the converter and unit data
    axis_converter = {
        name: axis.converter
        for name, axis in axis_map.items()
    }
    axis_units = {
        name: axis.get_units()
        for name, axis in axis_map.items()
    }

    # Get / Legend                                           #modification v
    old_legend = axes.get_legend()
    has_legend = old_legend is not None
    if has_legend:
        _draggable = old_legend._draggable is not None
        #_ncols = old_legend._ncols
        _fontsize = old_legend._fontsize
        _frameon = old_legend.get_frame_on()
        _shadow = old_legend.shadow
        _fancybox = type(old_legend.legendPatch.get_boxstyle()) == patches.BoxStyle.Round
        _framealpha = old_legend.get_frame().get_alpha()
    else:
        _draggable = False
        #_ncols = 1
        _fontsize = 10.0
        _frameon = True
        _shadow = False
        _fancybox = True
        _framealpha = 0.8
    legend = [
        ('Display', True),
        ('Draggable', _draggable),
        #('Columns', _ncols),
        ('Font size', _fontsize),
        ('Frame', _frameon),
        ('Shadow', _shadow),
        ('FancyBox', _fancybox),
        ('Alpha', _framealpha)
    ]                                                        #modification ^

    # Get / Curves
    labeled_lines = []
    for line in axes.get_lines():
        label = line.get_label()
        if label == '_nolegend_':
            continue
        labeled_lines.append((label, line))
    curves = []

    def prepare_data(d, init):
        """
        Prepare entry for FormLayout.

        *d* is a mapping of shorthands to style names (a single style may
        have multiple shorthands, in particular the shorthands `None`,
        `"None"`, `"none"` and `""` are synonyms); *init* is one shorthand
        of the initial style.

        This function returns an list suitable for initializing a
        FormLayout combobox, namely `[initial_name, (shorthand,
        style_name), (shorthand, style_name), ...]`.
        """
        if init not in d:
            d = {**d, init: str(init)}
        # Drop duplicate shorthands from dict (by overwriting them during
        # the dict comprehension).
        name2short = {name: short for short, name in d.items()}
        # Convert back to {shorthand: name}.
        short2name = {short: name for name, short in name2short.items()}
        # Find the kept shorthand for the style specified by init.
        canonical_init = name2short[d[init]]
        # Sort by representation and prepend the initial value.
        return ([canonical_init] +
                sorted(short2name.items(),
                       key=lambda short_and_name: short_and_name[1]))

    for label, line in labeled_lines:
        color = mcolors.to_hex(
            mcolors.to_rgba(line.get_color(), line.get_alpha()),
            keep_alpha=True)
        ec = mcolors.to_hex(
            mcolors.to_rgba(line.get_markeredgecolor(), line.get_alpha()),
            keep_alpha=True)
        fc = mcolors.to_hex(
            mcolors.to_rgba(line.get_markerfacecolor(), line.get_alpha()),
            keep_alpha=True)
        curvedata = [
            ('Label', label),
            ('Include legend', has_legend and line.get_label()[0] != "_"), #modification <
            sep,
            (None, '<b>Line</b>'),
            ('Line style', prepare_data(LINESTYLES, line.get_linestyle())),
            ('Draw style', prepare_data(DRAWSTYLES, line.get_drawstyle())),
            ('Width', line.get_linewidth()),
            ('Color (RGBA)', color),
            sep,
            (None, '<b>Marker</b>'),
            ('Style', prepare_data(MARKERS, line.get_marker())),
            ('Size', line.get_markersize()),
            ('Face color (RGBA)', fc),
            ('Edge color (RGBA)', ec)]
        curves.append([curvedata, label, ""])
    # Is there a curve displayed?
    has_curve = bool(curves)

    # Get ScalarMappables.
    labeled_mappables = []
    for mappable in [*axes.images, *axes.collections]:
        label = mappable.get_label()
        if label == '_nolegend_' or mappable.get_array() is None:
            continue
        labeled_mappables.append((label, mappable))
    mappables = []
    cmaps = [(cmap, name) for name, cmap in sorted(cm._colormaps.items())]
    for label, mappable in labeled_mappables:
        cmap = mappable.get_cmap()
        if cmap not in cm._colormaps.values():
            cmaps = [(cmap, cmap.name), *cmaps]
        low, high = mappable.get_clim()
        mappabledata = [
            ('Label', label),
            ('Colormap', [cmap.name] + cmaps),
            ('Min. value', low),
            ('Max. value', high),
        ]
        if hasattr(mappable, "get_interpolation"):  # Images.
            interpolations = [
                (name, name) for name in sorted(mimage.interpolations_names)]
            mappabledata.append((
                'Interpolation',
                [mappable.get_interpolation(), *interpolations]))
        mappables.append([mappabledata, label, ""])
    # Is there a scalarmappable displayed?
    has_sm = bool(mappables)

    datalist = [(general, "Axes", "")]
    if curves:
        datalist.append((curves, "Curves", ""))
    datalist.append((legend, "Legend", ""))
    if mappables:
        datalist.append((mappables, "Images, etc.", ""))

    def apply_callback(data):
        """A callback to apply changes."""
        orig_limits = {
            name: getattr(axes, f"get_{name}lim")()
            for name in axis_map
        }

        general = data.pop(0)
        curves = data.pop(0) if has_curve else []
        legend = data.pop(0) if has_curve else []
        mappables = data.pop(0) if has_sm else []
        if data:
            raise ValueError("Unexpected field")

        title = general.pop(0)
        axes.set_title(title)
        titlesize = general.pop(0)         #modification v
        axes.title.set_fontsize(titlesize)
        labelsize = general.pop(0)
        ticksize = general.pop(0)
        grid = general.pop(0)
        axes.grid(grid)                    #modification ^
        #generate_legend = general.pop()   #source commented <

        for i, (name, axis) in enumerate(axis_map.items()):
            axis_min = general[4*i]
            axis_max = general[4*i + 1]
            axis_label = general[4*i + 2]
            axis_scale = general[4*i + 3]
            if axis.get_scale() != axis_scale:
                getattr(axes, f"set_{name}scale")(axis_scale)

            axis._set_lim(axis_min, axis_max, auto=False)
            axis.set_label_text(axis_label)
            axis.label.set_size(labelsize)           #modification <
            axis.set_tick_params(labelsize=ticksize) #modification <

            # Restore the unit data
            axis.converter = axis_converter[name]
            axis.set_units(axis_units[name])

        # Set / Curves
        for index, curve in enumerate(curves):
            line = labeled_lines[index][1]
            (label, leg, linestyle, drawstyle, linewidth, color,           #modification v
             marker, markersize, markerfacecolor, markeredgecolor) = curve
            if leg:
                while label[0]=="_":
                    label = label[1:]
                line.set_label(label)
            else:
                line.set_label(f"_child{index}")                           #modification ^
            line.set_linestyle(linestyle)
            line.set_drawstyle(drawstyle)
            line.set_linewidth(linewidth)
            rgba = mcolors.to_rgba(color)
            line.set_alpha(None)
            line.set_color(rgba)
            if marker != 'none':
                line.set_marker(marker)
                line.set_markersize(markersize)
                line.set_markerfacecolor(markerfacecolor)
                line.set_markeredgecolor(markeredgecolor)

        # Set / Legend                                          #modification v
        (leg_display, leg_draggable, leg_fontsize, leg_frameon,
         leg_shadow, leg_fancybox, leg_framealpha, ) = legend  #leg_ncols
        
        old_legend = axes.get_legend()
        labels0 = [line.get_label()[0] for line in axes.get_lines()]
        if leg_display and len(labels0) != labels0.count("_"):
            new_legend = axes.legend(#ncol=leg_ncols,
                                     fontsize=float(leg_fontsize),
                                     frameon=leg_frameon,
                                     shadow=leg_shadow,
                                     framealpha=leg_framealpha,
                                     fancybox=leg_fancybox)
            new_legend.set_draggable(leg_draggable)
        elif old_legend:
            old_legend.remove()                                 #modification ^
        
        # Set ScalarMappables.
        for index, mappable_settings in enumerate(mappables):
            mappable = labeled_mappables[index][1]
            if len(mappable_settings) == 5:
                label, cmap, low, high, interpolation = mappable_settings
                mappable.set_interpolation(interpolation)
            elif len(mappable_settings) == 4:
                label, cmap, low, high = mappable_settings
            mappable.set_label(label)
            mappable.set_cmap(cmap)
            mappable.set_clim(*sorted([low, high]))

        # re-generate legend, if checkbox is checked           #source commented v
        #if generate_legend:
        #    draggable = None
        #    ncols = 1
        #    if axes.legend_ is not None:
        #        old_legend = axes.get_legend()
        #        draggable = old_legend._draggable is not None
        #        ncols = old_legend._ncols
        #    new_legend = axes.legend(ncols=ncols)
        #    if new_legend:
        #        new_legend.set_draggable(draggable)           #source commented ^

        # Redraw
        figure = axes.get_figure()
        figure.canvas.draw()
        for name in axis_map:
            if getattr(axes, f"get_{name}lim")() != orig_limits[name]:
                figure.canvas.toolbar.push_current()
                break

    figOptions = _formlayout.fedit(
        datalist,parent=parent,apply=apply_callback) #modification <
    return figOptions                                #modification <
    #_formlayout.fedit(
    #    datalist, title="Figure options", parent=parent,
    #    icon=QtGui.QIcon(
    #        str(cbook._get_data_path('images', 'qt4_editor_options.svg'))),
    #    apply=apply_callback)                          #source commented <



###############################################################################

# Monkey-patch original figureoptions
from matplotlib.backends.qt_editor import figureoptions
figureoptions.figure_edit = figure_edit

###############################################################################
