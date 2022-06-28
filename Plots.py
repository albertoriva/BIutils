#!/usr/bin/env python

# (c) 2016, A. Riva, DiBiG, ICBR Bioinformatics
# University of Florida

import sys
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.style
import matplotlib.pyplot as plt

### Easy plotting

class Plot():
    __doc__ = "Simple plot, on one or more data series."
    datafile = ""               # Input file
    filename = ""               # Output file (png)
    data = []
    series = None               # Name of each series of values
    title = None
    ylabel = None
    xlabel = None
    xlimits = None
    ylimits = None
    hsize = 12
    vsize = 8
    xcolumn = 0
    ycolumn = 1
    grid = None
    color = 'k'
    skipHeader = False
    attrNames = ['data', 'series', 'title', 'xlabel', 'ylabel', 'hsize', 'vsize']
    #colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    colors = ['g', 'r', 'c', 'm', 'y', 'k']
    coloridx = 0
    nplots = 1                  # number of side-by-side plots (single row for now)

    def __init__(self, **attributes):
        for a in self.attrNames:
            if a in attributes:
                setattr(self, a, attributes[a])
        self.init()

    def init(self):
        self.data = []

    def standardArgs(self, args):
        if not args or "-h" in args or "--help" in args:
            return self.usage()
        restargs = []
        prev = ""
        for a in args:
            if prev == "-o":
                self.filename = a
                prev = ""
            elif prev == "-t":
                self.title = a
                prev = ""
            elif prev == "-g":
                if a in "xyXY":
                    self.grid = a.lower()
                else:
                    self.grid = "both"
                prev = ""
            elif prev == "-c":
                self.color = a
                prev = ""
            elif prev == "-xl":
                self.xlabel = a
                prev = ""
            elif prev == "-yl":
                self.ylabel = a
                prev = ""
            elif prev == "-xs":
                self.hsize = float(a)
                prev = ""
            elif prev == "-ys":
                self.vsize = float(a)
                prev = ""
            elif prev == "-xc":
                self.xcolumn = int(a) - 1
                prev = ""
            elif prev == "-yc":
                self.ycolumn = int(a) - 1
                prev = ""
            elif prev == "-xr":
                parts = a.split(":")
                self.xlimits = [float(parts[0]), float(parts[1])]
                prev = ""
            elif prev == "-yr":
                parts = a.split(":")
                self.ylimits = [float(parts[0]), float(parts[1])]
                prev = ""
            elif a in ["-o", "-t", "-g", "-c", "-xl", "-yl", "-xs", "-ys", "-xc", "-yc", "-xr", "-yr"]:
                prev = a
            elif a == "-H":
                self.skipheader = True
            else:
                restargs.append(a)
        return restargs

    def usage(self):
        self.standardHelp()

    def parseArgs(self, args):
        args = self.standardArgs(args)
        if args:
            self.datafile = args[0]
            return True
        return False

    def standardHelp(self, out=sys.stdout):
        out.write("""Common options:
 -o O    | Write image to file O
 -t T    | Set image title
 -g G    | Set grid; G is one of x, y, b(oth)
 -c C    | Draw plot using color C (one of 'g', 'r', 'c', 'm', 'y', 'k')
 -xl L   | Label for X axis
 -yl L   | Label for Y axis
 -xs S   | Image width in inches (default: {})
 -ys S   | Image height in inches (default: {})
 -xc C   | Column containing X values in data file (default: {})
 -yc C   | Column containing Y values in data file (default: {})
 -xr A:B | Set X axis range to A - B
 -yr A:B | Set Y axis range to A - B

""".format(self.hsize, self.vsize, self.xcolumn+1, self.ycolumn+1))
        return False

    def parseDatafile(self):
        """Generic method to read data from tab-delimited files. Passes
line contents to storeLine(). Lines starting with # are ignored."""
        with open(self.datafile, "r") as f:
            c = csv.reader(f, delimiter='\t')
            for line in c:
                if len(line) > 0 and line[0][0] == '#':
                    continue
                self.storeLine(line)

    def storeLine(self, line):
        """Generic method to store data from a tab-delimited line. By default
reads X value from xcolumn, Y value from ycolumn."""
        self.data.append([float(line[self.xcolumn]), float(line[self.ycolumn])])

    def run(self):
        """Generic method to generate image. Calls parseDatafile() and plot()."""
        self.parseDatafile()
        self.plot()
                
    def nextColor(self):
        c = self.colors[self.coloridx]
        self.coloridx = (self.coloridx + 1) % len(self.colors)
        #c = "C" + str(self.coloridx)
        #self.coloridx = (self.coloridx + 1) % 10
        return c

    def set_labels(self, ax):
        if self.title:
            ax.set_title(self.title)
        if self.xlabel:
            ax.set_xlabel(self.xlabel)
        if self.ylabel:
            ax.set_ylabel(self.ylabel)

    def setRanges(self, ax):
#        ax.set_autoscale_on(True)
        if self.xlimits:
            sys.stderr.write("Setting X range to {}\n".format(self.xlimits))
            plt.xlim(self.xlimits)
        if self.ylimits:
            sys.stderr.write("Setting Y range to {}\n".format(self.ylimits))
            plt.ylim(self.ylimits)

    def plot(self, filename=None):
        if filename:
            self.filename = filename
        matplotlib.style.use('default')
        fig, ax = plt.subplots(1, self.nplots, figsize=(self.hsize, self.vsize), sharey=True)

        self.setRanges(ax)

        self.plot0(ax)
        
        if self.grid:
            ax.grid(axis=self.grid)
        self.set_labels(ax)
        fig.savefig(self.filename)

    def plot0(self, ax):
        #ax.scatter([v[0] for v in self.data], [v[1] for v in self.data])
        ax.plot([v[0] for v in self.data], [v[1] for v in self.data])

class Histogram(Plot):
    "Histogram on a single data series."
    nbins = 10
    rwidth = None
    attrNames = ["nbins"]

    def parseArgs(self, args):
        args = self.standardArgs(args)
        prev = ""
        for a in args:
            if prev == "-n":
                self.nbins = int(a)
                prev = ""
            elif prev == "-r":
                self.rwidth = float(a)
                prev = ""
            elif a  in ["-n", "-r"]:
                prev = a
            else:
                self.datafile = a
        return self.datafile

    def storeLine(self, line):
        """Generic method to store data from a tab-delimited line. By default
reads X value from xcolumn, Y value from ycolumn."""
        self.data.append(float(line[self.xcolumn]))

    def plot0(self, ax):
        ax.hist(self.data, bins=self.nbins, rwidth=self.rwidth)

class BarChart(Plot):
    "Bar chart on one or more data series."
    xticklabels = None
    attrNames = ['data', 'series', 'title', 'xlabel', 'ylabel', 'xticklabels']

    def usage(self):
        sys.stdout.write("""Draw a bar chart for multiple data series. Each row in `data' corresponds
to a series, and has the same number of elements as the length of `xticklabels'.""")

    def parseArgs(self, args):
        args = self.standardArgs(args)
        prev = ""
        for a in args:
            if prev == "-xt":
                self.xticklabels = a.split(",")
                prev = ""
            elif a in ["-xt"]:
                prev = a
            else:
                self.datafile = a
        if self.datafile:
            return True
                
    def plot0(self, ax):
        S = len(self.data)
        N = len(self.data[0])
        ind = np.arange(N)
        width = 1.0/(S+1)       # the width of the bars
        w2 = width / 2.0

        p = ind + w2
        rects = []
        for row in self.data:
            rects.append(ax.bar(p, row, width, color=self.nextColor()))
            p += width

        ax.set_xticks(ind + (width * S) / 2.0)
        ax.set_xticklabels(self.xticklabels)
        ax.legend([r[0] for r in rects], self.series)

class PercentageBars(BarChart):
    xticklabels = None
    attrNames = ['data', 'series', 'title', 'xlabel', 'ylabel', 'xticklabels']

    def init(self):
        pass

    def plot0(self, ax):
        barWidth = 0.8
        nvalues = len(self.xticklabels)
        xcoords = range(nvalues)
        bottoms = [0.0]*nvalues

        bars = []
        for lab in self.series:
            values = self.data[lab]
            bars.append(plt.bar(xcoords, values, bottom=bottoms, edgecolor="white", width=barWidth))
            for i in range(nvalues):
                bottoms[i] += values[i]
        plt.xticks(xcoords, self.xticklabels)
        plt.xlabel("Sample")
        plt.legend(bars, self.series)

class Scatterplot(Plot):
    fc = None                   # Fold change threshold
    pval = None                 # P-value threshold (default: don't check p-values)
    correlation = None          # Correlation (computed)
    maxv = 1000
    truncate = True
    limits = None
    # Not used, but stored if necessary
    cols1 = None
    cols2 = None

    def init(self):
        pass

    def parseArgs(self, args):
        args = self.standardArgs(args)
        prev = ""
        for a in args:
            if prev == "-fc":
                self.fc = float(a)
                prev = ""
            elif prev == "-p":
                self.pval = float(a)
                prev = ""
            elif prev == "-m":
                self.maxv = float(a)
                prev = ""
            elif a in ["-fc", "-p", "-m"]:
                prev = a
            elif a == "-T":
                self.truncate = False
            else:
                self.datafile = a

        if self.datafile:
            return True

    def plot0(self, ax):
        xover = []
        yover = []
        xunder = []
        yunder = []
        xother = []
        yother = []
        xsig = []
        ysig = []
        nplotted = 0
        nover    = 0
        nunder   = 0
        nfilt    = 0
        nnn      = 0

        v1 = np.array([d[0] for d in self.data])
        v2 = np.array([d[1] for d in self.data])
        # v3 = np.array([d[2] for d in self.data])
        self.correlation = np.corrcoef(v1, v2)
        if self.truncate:
            m1 = np.percentile(v1, 90.0)
            m2 = np.percentile(v2, 90.0)
            self.maxv = max(m1, m2)
        for row in self.data:
            #print (row, row[2], self.pval, row[2] <= self.pval)
            if row[0] > self.maxv or row[1] > self.maxv:
                nfilt += 1
                continue
            if self.pval and (row[2] <= self.pval):
                ysig.append(row[0])
                xsig.append(row[1])
            elif row[0] == 0:
                yunder.append(row[0])
                xunder.append(row[1])
                nunder += 1
            elif row[1] == 0:
                yover.append(row[0])
                xover.append(row[1])
                nover += 1
            elif self.fc:
                fc = np.log2(1.0 * row[0] / row[1])
                if fc > self.fc:
                    yover.append(row[0])
                    xover.append(row[1])
                    nover += 1
                elif fc < -self.fc:
                    yunder.append(row[0])
                    xunder.append(row[1])
                    nunder += 1
                else:
                    yother.append(row[0])
                    xother.append(row[1])
            else:
                yother.append(row[0])
                xother.append(row[1])
            nplotted += 1

        if self.truncate or self.limits:
            ax.set_autoscale_on(False)
        ax.scatter(xother, yother, color='k', s=1)
        ax.scatter(xover, yover, color='#FF8C00', s=1)
        ax.scatter(xunder, yunder, color='#0000FF', s=1)
        ax.scatter(xsig, ysig, color='#FF0000', s=1)
        if self.truncate:
            ax.axis([0, self.maxv, 0, self.maxv])
        elif self.limits:
            ax.axis(self.limits)

class FoldChangePlot(Plot):
    fc = None                   # Fold change threshold
    pval = None                 # P-value threshold (default: don't check p-values)
    correlation = None          # Correlation (computed)
    maxv = 5

    def plot0(self, ax):
        xover = []
        yover = []
        xunder = []
        yunder = []
        xother = []
        yother = []
        xsig = []
        ysig = []
        nplotted = 0
        nover    = 0
        nunder   = 0
        nfilt    = 0
        nnn      = 0

        for row in self.data:
            #print (row, row[2], self.pval, row[2] <= self.pval)
            if abs(row[0]) > self.maxv or abs(row[1]) > self.maxv:
                nfilt += 1
                continue
            if self.pval and (row[2] <= self.pval):
                ysig.append(row[0])
                xsig.append(row[1])
            elif row[0] == 0:
                yunder.append(row[0])
                xunder.append(row[1])
                nunder += 1
            elif row[1] == 0:
                yover.append(row[0])
                xover.append(row[1])
                nover += 1
            elif self.fc:
                fc = np.log2(1.0 * row[0] / row[1])
                if fc > self.fc:
                    yover.append(row[0])
                    xover.append(row[1])
                    nover += 1
                elif fc < -self.fc:
                    yunder.append(row[0])
                    xunder.append(row[1])
                    nunder += 1
                else:
                    yother.append(row[0])
                    xother.append(row[1])
            else:
                yother.append(row[0])
                xother.append(row[1])
            nplotted += 1

        ax.scatter(xother, yother, color='k', s=1)
        ax.scatter(xover, yover, color='#FF8C00', s=1)
        ax.scatter(xunder, yunder, color='#0000FF', s=1)
        ax.scatter(xsig, ysig, color='#FF0000', s=1)
        ax.set_autoscale_on(False)
        ax.axis([0, self.maxv, 0, self.maxv])

class VolcanoPlot(Plot):
    fc = 1                   # Fold change threshold
    pval = 2                 # P-value threshold (in -log10 scale)
    plot_all = False         # If true, plot all genes (not just significant ones)
    xlabel = "log2(FC)"
    ylabel = "-log10(P-value)"
    nup = 0
    ndown = 0

    def init(self):
        pass

    def parseArgs(self, args):
        args = self.standardArgs(args)
        prev = ""
        for a in args:
            if prev == "-f":
                self.fc = float(a)
                prev = ""
            elif prev == "-p":
                self.pval = -np.log10(float(a))
                prev = ""
            elif a in ["-f", "-p"]:
                prev = a
            elif a == "-a":
                self.plot_all = True
            else:
                self.datafile = a
        self.xcolumn = 3
        self.ycolumn = 4
        return True
    
    def plot0(self, ax):
        xover = []
        yover = []
        xunder = []
        yunder = []
        xother = []
        yother = []

        # data is a list of pairs [fc, pval]
        for row in self.data:
            fc = row[0]
            lp = -np.log10(row[1])
            if lp > self.pval:  # P-value over threshold?
                if fc > self.fc:
                    xover.append(fc)
                    yover.append(lp)
                    self.nup += 1
                elif fc < -self.fc:
                    xunder.append(fc)
                    yunder.append(lp)
                    self.ndown += 1
                elif self.plot_all:
                    xother.append(fc)
                    yother.append(lp)
            elif self.plot_all:
                xother.append(fc)
                yother.append(lp)
        ax.scatter(xother, yother, color='k', s=1)
        ax.scatter(xover, yover, color='#FF0000', s=2, marker='o')
        ax.scatter(xunder, yunder, color='#00FF00', s=2, marker='o')
        ax.axhline(self.pval, 0.0, 1.0, color='#0000FF', linestyle=':')
        ax.axvline(-self.fc, 0.0, 1.0, color='#0000FF', linestyle=':')
        ax.axvline(self.fc, 0.0, 1.0, color='#0000FF', linestyle=':')
        # ax.axis([-5.0, 5.0, 0, 10.0])

class MAplot(Plot):
    fc = 1                      # Fold change threshold
    pval = None
    correlation = None          # Correlation (computed)
    maxx = 20
    maxy = 0

    def plot(self, filename=None):
        xs = []
        ys = []
        xsig = []
        ysig = []
        nplotted = 0

        if filename:
            self.filename = filename
        for row in self.data:
            if row[0] == 0 or row[1] == 0:
                continue
            m = np.log2(1.0 * row[0] / row[1])
            a = 0.5 * (np.log2(float(row[0])) + np.log2(float(row[1])))
            if a > self.maxx:
                continue
            if abs(m) > self.maxy:
                self.maxy = abs(m)
            if self.pval:
                if row[2] <= self.pval:
                    xsig.append(a)
                    ysig.append(b)
                else:
                    xs.append(a)
                    ys.append(m)
            else:
                xs.append(a)
                ys.append(m)
            nplotted += 1

        fig, ax = plt.subplots(figsize=(self.hsize, self.vsize))
        ax.set_autoscale_on(False)
        ax.scatter(xs, ys, color=self.color, s=1)
        ax.axis([0, self.maxx, -self.maxy, self.maxy])
        self.set_labels(ax)
        fig.savefig(filename)

class HockeyStickPlot(Plot):
    logscale = False
    normalize = False
     
    def parseArgs(self, args):
        args = self.standardArgs(args)
        prev = ""
        for a in args:
            if a == "-l":
                self.logscale = True
            elif a == "-n":
                self.normalize = True
            else:
                self.datafile = a
        return True

    def storeLine(self, line):
        if self.normalize:
            w = int(line[2]) - int(line[1]) + 1
            v = float(line[3]) / w
        else:
            v = float(line[3])
        if self.logscale:
            v = np.log10(v)
        self.data.append(v)
        
    def plot0(self, ax):
        self.data.sort()
        ax.scatter(range(len(self.data)), self.data, color=self.color, s=1)

class BoxPlot(Plot):
    logscale = False
    percentile = None

    def init(self):
        self.data = [ [], [] ]

    def parseArgs(self, args):
        args = self.standardArgs(args)
        self.nplots = 2
        prev = ""
        for a in args:
            if prev == "-p":
                self.percentile = int(a)
                prev = ""
            elif a in ["-p"]:
                prev = a
            elif a == "-l":
                self.logscale = True
            else:
                self.datafile = a
        self.data2 = []
        return True

    def storeLine(self, line):
        good = True
        a = float(line[1])
        b = float(line[2])
        if self.logscale:
            if a == 0:
                good = False
            else:
                a = np.log10(a)
            if b == 0:
                good = False
            else:
                b = np.log10(b)
        if good:
            self.data[0].append(a)
            self.data[1].append(b)

    def clip(self, limit):
        d1 = []
        d2 = []
        for i in range(len(self.data)):
            a = self.data[0][i]
            b = self.data[1][i]
            if a <= limit and b <= limit:
                d1.append(a)
                d2.append(b)
        return d1, d2

    def plot0(self, ax):
        if self.percentile:
            limit = min(np.percentile(self.data, self.percentile), np.percentile(self.data2, self.percentile))
            self.data, self.data2 = self.clip(limit)

        (bp1, bp2) = ax
        bp1.boxplot(self.data)
        bp1.set_title("MUT")
        bp2.boxplot(self.data2)
        bp2.set_title("WT")

class ViolinPlot(Plot):
    nfiles = 0

    def init(self):
        self.data = []

    def parseArgs(self, args):
        restargs = self.standardArgs(args)
        self.datafile = restargs
        self.nfiles = len(self.datafile)
        #print self.datafile
        return True
    
    def parseDatafile(self):
        self.data = [ [] for _ in range(self.nfiles) ]
        for idx in range(self.nfiles):
            with open(self.datafile[idx], "r") as f:
                c = csv.reader(f, delimiter='\t')
                for line in c:
                    if len(line) > 0 and line[0][0] == '#':
                        continue
                    self.data[idx].append(float(line[1]))

    def plot0(self, ax):
        ax.violinplot(self.data, vert=True, showmeans=True, showmedians=True)
        ax.grid()

CLASSES = {'plot': Plot,
           'bars': BarChart,
           'percbars': PercentageBars,
           'scatter': Scatterplot,
           'fcplot': FoldChangePlot,
           'volcano': VolcanoPlot,
           'maplot': MAplot,
           'hockey': HockeyStickPlot,
           'boxplot': BoxPlot,
           'violin': ViolinPlot,
           'hist': Histogram}

def listPlotTypes():
    labels = sorted(CLASSES.keys())
    ml = max([len(l) for l in labels])
    fmt = "{:" + str(ml) + "} | {}\n"
    bar = "-"*ml + "-|---------------------------\n"
    sys.stdout.write("Available plot types:\n\n")
    sys.stdout.write(fmt.format("Name", "Description"))
    sys.stdout.write(bar)
    for k in labels:
        desc = CLASSES[k]().__doc__
        sys.stdout.write(fmt.format(k, desc))
    sys.stdout.write("\n")

def main(args):
    if args:
        if "-L" in args:
            return listPlotTypes()
        cmd = args[0]
        if cmd in CLASSES:
            P = CLASSES[cmd]()
            if P.parseArgs(args[1:]):
                P.run()
            else:
                P.usage()
        else:
            sys.stdout.write("ERROR: the first argument, `{}' should be a plot name.\n\n".format(cmd))
            sys.stdout.write("Valid plot names: {}\n".format(", ".join(CLASSES.keys())))
    else:
        usage()

def usage():
    sys.stdout.write("""Plots - simple command-line plotter.

Usage: Plots.py plot-type [general options] [plot-specific options]

Call `Plots.py -L' to display available plot types.

Call `Plots.py plot-type -h' to see plot-specific options.

""")
    Plot().standardHelp()

if __name__ == "__main__":
    main(sys.argv[1:])
