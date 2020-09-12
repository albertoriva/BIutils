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
    datafile = ""               # Input file
    filename = ""               # Output file (png)
    data = []
    series = None               # Name of each series of values
    title = None
    ylabel = None
    xlabel = None
    hsize = 12
    vsize = 8
    attrNames = ['data', 'series', 'title', 'xlabel', 'ylabel', 'hsize', 'vsize']
    #colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    colors = ['g', 'r', 'c', 'm', 'y', 'k']
    coloridx = 0

    def __init__(self, **attributes):
        for a in self.attrNames:
            if a in attributes:
                setattr(self, a, attributes[a])

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

    def plot(self, filename):
        self.filename = filename

class BarChart(Plot):
    """Draw a bar chart for multiple data series. Each row in `data' corresponds
to a series, and has the same number of elements as the length of `xticklabels'."""
    xticklabels = None
    attrNames = ['data', 'series', 'title', 'xlabel', 'ylabel', 'xticklabels']

    def plot(self, filename):
        self.filename = filename
        matplotlib.style.use('default')
        S = len(self.data)
        N = len(self.data[0])
        ind = np.arange(N)
        width = 1.0/(S+1)       # the width of the bars
        w2 = width / 2.0

        fig, ax = plt.subplots(figsize=(self.hsize, self.vsize))
        p = ind + w2
        rects = []
        for row in self.data:
            rects.append(ax.bar(p, row, width, color=self.nextColor()))
            p += width

        self.set_labels(ax)
        ax.set_xticks(ind + (width * S) / 2.0)
        ax.set_xticklabels(self.xticklabels)

        ax.legend([r[0] for r in rects], self.series)

        fig.savefig(filename)

class PercentageBars(Plot):
    xticklabels = None
    attrNames = ['data', 'series', 'title', 'xlabel', 'ylabel', 'xticklabels']

    def plot(self, filename):
        self.filename = filename
        matplotlib.style.use('default')
        barWidth = 0.8
        nvalues = len(self.xticklabels)
        xcoords = range(nvalues)
        bottoms = [0.0]*nvalues

        bars = []
        fig, ax = plt.subplots(figsize=(self.hsize, self.vsize))
        self.set_labels(ax)
        for lab in self.series:
            values = self.data[lab]
            bars.append(plt.bar(xcoords, values, bottom=bottoms, edgecolor="white", width=barWidth))
            for i in range(nvalues):
                bottoms[i] += values[i]
        plt.xticks(xcoords, self.xticklabels)
        plt.xlabel("Sample")
        plt.legend(bars, self.series)
        fig.savefig(filename)


class Scatterplot(Plot):
    fc = None                   # Fold change threshold
    pval = None                 # P-value threshold (default: don't check p-values)
    correlation = None          # Correlation (computed)
    maxv = 1000
    truncate = True
    limits = None

    def plot(self, filename):
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

        # data is a list of pairs [x, y]
        self.filename = filename
        v1 = np.array([d[0] for d in self.data])
        v2 = np.array([d[1] for d in self.data])
        # v3 = np.array([d[2] for d in self.data])
        self.correlation = np.corrcoef(v1, v2)
        if self.truncate:
            self.maxv = max(np.percentile(v1, 90.0), np.percentile(v2, 90.0))
        # sys.stderr.write("Max: {}\n".format(self.maxv))
        # sys.stderr.write("Data: {}\n".format(len(self.data)))
        # sys.stderr.write("Pval: {} Range: {} - {}\n".format(self.pval, np.min(v3), np.max(v3)))
        # raw_input()
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

        # sys.stderr.write("Sig: {}\nOther: {}\n".format(len(xsig), len(xother)))
        # sys.stderr.write("Over: {}\nUnder: {}\n".format(len(xover), len(xunder)))
        # sys.stderr.write("Filtered: {}\nnnn: {}\n".format(nfilt, nnn))
        # raw_input()
        fig, ax = plt.subplots(figsize=(self.hsize, self.vsize))
        if self.truncate or self.limits:
            ax.set_autoscale_on(False)
        ax.scatter(xother, yother, color='k', s=1)
        ax.scatter(xover, yover, color='#FF8C00', s=1)
        ax.scatter(xunder, yunder, color='#0000FF', s=1)
        ax.scatter(xsig, ysig, color='#FF0000', s=1)
        ax.grid(True)
        if self.truncate:
            ax.axis([0, self.maxv, 0, self.maxv])
        elif self.limits:
            ax.axis(self.limits)
        self.set_labels(ax)
        fig.savefig(filename)

class FoldChangePlot(Plot):
    fc = None                   # Fold change threshold
    pval = None                 # P-value threshold (default: don't check p-values)
    correlation = None          # Correlation (computed)
    maxv = 5

    def plot(self, filename):
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

        # data is a list of pairs [x, y]
        self.filename = filename

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

        # sys.stderr.write("Sig: {}\nOther: {}\n".format(len(xsig), len(xother)))
        # sys.stderr.write("Over: {}\nUnder: {}\n".format(len(xover), len(xunder)))
        # sys.stderr.write("Filtered: {}\nnnn: {}\n".format(nfilt, nnn))
        # raw_input()
        fig, ax = plt.subplots(figsize=(self.hsize, self.vsize))
        ax.set_autoscale_on(False)
        ax.scatter(xother, yother, color='k', s=1)
        ax.scatter(xover, yover, color='#FF8C00', s=1)
        ax.scatter(xunder, yunder, color='#0000FF', s=1)
        ax.scatter(xsig, ysig, color='#FF0000', s=1)
        ax.axis([0, self.maxv, 0, self.maxv])
        self.set_labels(ax)
        fig.savefig(filename)

class VolcanoPlot(Plot):
    fc = 1                   # Fold change threshold
    pval = 2                 # P-value threshold (in -log10 scale)
    plot_all = False         # If true, plot all genes (not just significant ones)

    def plot(self, filename):
        xover = []
        yover = []
        xunder = []
        yunder = []
        xother = []
        yother = []

        # data is a list of pairs [fc, pval]
        self.filename = filename
        for row in self.data:
            fc = row[0]
            lp = -np.log10(row[1])
            if lp > self.pval:  # P-value over threshold?
                if fc > self.fc:
                    xover.append(fc)
                    yover.append(lp)
                elif fc < -self.fc:
                    xunder.append(fc)
                    yunder.append(lp)
                elif self.plot_all:
                    xother.append(fc)
                    yother.append(lp)
            elif self.plot_all:
                xother.append(fc)
                yother.append(lp)
        fig, ax = plt.subplots(figsize=(self.hsize, self.vsize))
        ax.scatter(xother, yother, color='k', s=1)
        ax.scatter(xover, yover, color='#FF0000', s=1)
        ax.scatter(xunder, yunder, color='#00FF00', s=1)
        ax.axis([-5.0, 5.0, 0, 10.0])
        self.set_labels(ax)
        fig.savefig(filename)

class MAplot(Plot):
    fc = 1                      # Fold change threshold
    pval = None
    correlation = None          # Correlation (computed)
    maxx = 20
    maxy = 0

    def plot(self, filename):
        xs = []
        ys = []
        xsig = []
        ysig = []
        nplotted = 0

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
        ax.scatter(xs, ys, color='k', s=1)
        ax.axis([0, self.maxx, -self.maxy, self.maxy])
        self.set_labels(ax)
        fig.savefig(filename)

class HockeyStickPlot(Plot):
    logscale = False
    normalize = False
     
    def parseArgs(self, args):
        prev = ""
        for a in args:
            if prev == "-o":
                self.filename = a
                prev = ""
            elif a in ["-o"]:
                prev = a
            elif a == "-l":
                self.logscale = True
            elif a == "-n":
                self.normalize = True
            else:
                self.datafile = a
   
    def run(self):
        with open(self.datafile, "r") as f:
            c = csv.reader(f, delimiter='\t')
            for line in c:
                if self.normalize:
                    w = int(line[2]) - int(line[1]) + 1
                    v = float(line[3]) / w
                else:
                    v = float(line[3])
                if self.logscale:
                    v = np.log10(v)
                self.data.append(v)
        self.data.sort()
        fig, ax = plt.subplots(figsize=(self.hsize, self.vsize))
        ax.set_autoscale_on(True)
        ax.scatter(range(len(self.data)), self.data, color='k', s=1)
        fig.savefig(self.filename)

def main_volcano(args):
    P = VolcanoPlot(title='Volcano plot', ylabel="-log10(P-value)", xlabel="log2(FC)")
    data = []
    prev = ""
    for a in args:
        if prev == "-o":
            P.filename = a
            prev = ""
        elif prev == "-t":
            P.title = a
            prev = ""
        elif prev == "-f":
            P.fc = float(a)
            prev = ""
        elif prev == "-p":
            P.pval = -np.log10(float(a))
            prev = ""
        elif a in ["-o", "-t", "-f", "-p"]:
            prev = a
        elif a == "-a":
            P.plot_all = True
        else:
            P.datafile = a

    with open(P.datafile, "r") as f:
        c = csv.reader(f, delimiter='\t')
        c.next()
        for line in c:
            data.append([float(line[3]), float(line[4])])
    P.data = data
    P.plot(P.filename)

def main_hockey(args):
    P = HockeyStickPlot(title='Hockeystick plot')
    P.parseArgs(args)
    P.run()

def main(args):
    epoints = {'volcano': main_volcano,
               'hockey': main_hockey}

    if args:
        cmd = args[0]
        if cmd in epoints:
            func = epoints[cmd]
            return func(args[1:])
    usage()

def usage():
    sys.stdout.write("""Usage: ...
""")

if __name__ == "__main__":
    main(sys.argv[1:])
