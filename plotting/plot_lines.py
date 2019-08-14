# Std
import six
import pandas

# Mine
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class LinesPlotter():
    def __init__(self, plot_specs):
        self.plot_specs = plot_specs

    def plotInPath(self, plot_path_without_extension):
        footer_artist = setupPlot(self.plot_specs.setup_specs)

        # Plot lines
        for line_spec in self.plot_specs.lines_specs:
            plotLineSpec(line_spec)
        # Define legend
        lgd = plt.legend(loc="center left", fontsize="small", fancybox=True, shadow=True,
                         bbox_to_anchor=(1, 0.5))

        # Post-line-plot setup
        setupXTicks(self.plot_specs.setup_specs.extra_ticks)
        saveAndClearPlt(plot_path_without_extension, lgd, footer_artist)

def plotLineSpec(line_spec):
    x_data          = xDataForLineSpec(line_spec)
    y_data          = line_spec.df[line_spec.y_var]
    linewidth       = line_spec.linewidth
    linestyle       = line_spec.linestyle
    markersize      = line_spec.markersize
    marker          = line_spec.marker
    label           = line_spec.label
    color           = line_spec.color

    # Call plotting function
    plt.plot(x_data, y_data,
             linewidth = linewidth,
             linestyle = linestyle,
             markersize = markersize,
             marker = marker,
             label = label,
             color = color,
             )

def xDataForLineSpec(line_spec):
    # Check if its a column or the index
    if line_spec.x_var:
        x_data = line_spec.df[line_spec.x_var]
    else:
        # If no column is included, return the index
        index  = line_spec.df.index
        x_data = tryTimestampOrNumberForList(index)
    return x_data

def tryTimestampOrNumberForList(orig_index):
    # There's no way in python to ask if an object is a number, so we just try
    # to use it as a timestamp and if it fails then it's a number
    try:
        # For now, we just assume that if it's not an int, it's a timestamp that knows to respond to "year"
        final_index = [x.year for x in orig_index]
    except AttributeError:
        # If it can't respond to year, ask if it's a string
        # Get the first cell
        first_cell = orig_index[0]
        if isinstance(first_cell, six.string_types):
            # If it's a string, assume it's a timestamp and convert it to pandas datetime
            orig_index_datetime = pandas.to_datetime(orig_index)
            # Get the year from the timestamp
            final_index = [x.year for x in orig_index_datetime]
        else:
            # Assume it's a number and matplotlib can plot it
            final_index = orig_index
    return final_index

def setupPlot(setup_specs):
    plt.style.use('fivethirtyeight')
    plt.gca().set_position([0.10, 0.15, 0.80, 0.77])
    plt.xlabel(setup_specs.x_label)
    plt.title(setup_specs.title + "\n" + setup_specs.subtitle, fontsize=14, y=1.08)
    plt.ylabel(setup_specs.y_label)
    plt.ticklabel_format(useOffset=False)  # So it doesn't use an offset on the x axis
    footer_artist = plt.annotate(setup_specs.footer, (1, 0), (0, -70), xycoords='axes fraction', textcoords='offset points',
                                 va='top', horizontalalignment='right')
    plt.margins(x=0.1, y=0.1)  # increase buffer so points falling on it are plotted
    return footer_artist


def setupXTicks(extra_ticks):
    # Get the ticks automatically generated by matplotlib
    auto_x_ticks = list(plt.xticks()[0])
    # Trim the borders (excessively large)
    auto_x_ticks_wo_borders = auto_x_ticks[1:-1]
    x_ticks = sorted(auto_x_ticks_wo_borders + extra_ticks)
    plt.xticks(x_ticks, rotation='vertical')  # add extra ticks (1975 for vermeulen for example)


def saveAndClearPlt(plot_path_without_extension, lgd, footer_artist, extra_lgd=None):
    extensions = [".svg", ".png"]
    for ext in extensions:
        plot_path = plot_path_without_extension + ext
        if extra_lgd:
            # If two legends (for when the plot has variables with different scale)
            plt.savefig(plot_path, bbox_extra_artists=(lgd, extra_lgd, footer_artist), bbox_inches='tight')
        else:
            # If only one legend
            plt.savefig(plot_path, bbox_extra_artists=(lgd, footer_artist), bbox_inches='tight')
    plt.clf()
