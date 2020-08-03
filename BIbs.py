#!/usr/bin/env python

__doc__ = "Interface to the Illumina Basespace API"
__author__ = "A. Riva, ICBR Bioinformatics Core"

import os
import sys
import json
import subprocess

COMMANDS = ["list", "meta", "info", "initdir", "all", "api", "nreads", "report"]

def toList(s):
    """If s is not a list, return [s]."""
    if type(s).__name__ == "list":
        return s
    else:
        return [s]

class BSClient():
    bspath = "bs"
    config = None
    command = None
    args = []

    def __init__(self, cmd=None, bspath="bs"):
        self.command = cmd
        self.args = []
        self.bspath = bspath

    def parseArgs(self, args):
        if not args:
            self.usage()
            return False

        prev = ""
        for a in args:
            if prev == "-c":
                self.config = a
                prev = ""
            elif a in ["-c"]:
                prev = a
            elif not self.command:
                if a in COMMANDS:
                    self.command = a
                else:
                    sys.stderr.write("Unknown command: {}.\n".format(a))
                    return False
            else:
                self.args.append(a)
        return True

    def usage(self):
        sys.stdout.write("""bspace.py - Wrapper for BaseSpace command-line interface.

Usage: bspace.py command arguments...

Where command is one of: {}

""".format(", ".join(COMMANDS)))

    def callBS(self, arguments, fmt="csv", token=False):
        """Low-level method to call bs with the supplied arguments. If `fmt' is "csv" (the default)
the result is a string, while if it is "json" the result is a parsed JSON dictionary."""

        cmdline = self.bspath + " --api-server https://api.basespace.illumina.com/ " 
        if token:
            cmdline += "--access-token " + token + " "
        cmdline += " ".join(arguments)
        if self.config:
            cmdline += " -c " + self.config
        cmdline += " -f " + fmt
        result = subprocess.check_output(cmdline, shell=True)
        if fmt == "json":
            return json.loads(result)
        else:
            return result

    def getRunInfo(self, name):
        """Get all information on run `name'. Returns a list of pairs (key, value) in the order in which they were retrieved from BaseSpace."""
        p = self.callBS(["run", "get", "--name", name])
        lines = p.split("\n")
        hdr = lines[0].strip().split(",")
        data = lines[1].strip().split(",")
        return zip(hdr, data)

    def writeRunInfo(self, filename, runinfo):
        """Write run data `runinfo' to `filename' in tab-delimited format."""
        with open(filename, "w") as out:
            for pair in runinfo:
                out.write("{}\t{}\n".format(*pair))

    def writeEntry(self, stream, d, label, key):
        stream.write("{}:\t{}\n".format(label, d[key]))

    def writeMeta(self, filename, runinfo):
        d = dict(runinfo)
        with open(filename, "w") as out:
            self.writeEntry(out, d, "Name", "ExperimentName")
            self.writeEntry(out, d, "ID", "Id")
            self.writeEntry(out, d, "URL", "BaseSpaceUIHref.HrefBaseSpaceUI")
            self.writeEntry(out, d, "BasespaceName", "Name")
            self.writeEntry(out, d, "Instrument", "InstrumentName")
            self.writeEntry(out, d, "Flowcell", "FlowcellBarcode")
            self.writeEntry(out, d, "Date", "DateCreated")
            out.write("Description:\t\n")

    def initializeDirectory(self, name):
        os.mkdir(name)
        ri = self.getRunInfo(name)
        self.writeRunInfo(name + "/runInfo.csv", ri)
        self.writeMeta(name + "/META", ri)
        os.mkdir(name + "/fastq")

    def getAllRuns(self, show=False):
        if show:
            p = self.callBS(["run", "list"], fmt="table")
            sys.stdout.write(p)
            return
        result = []
        p = self.callBS(["run", "list"])
        rows = [ line.strip() for line in p.split("\n") ]
        hdr = rows[0].split(",")
        for line in rows[1:]:
            fields = line.strip().split(",")
            result.append(dict(zip(hdr, fields)))
        return result

    def getRunProjects(self, runid):
        projects = []
        apps = self.callBS(["list", "appsessions", "--input-run", runid], fmt="json")
        for app in apps:
            appdata = self.callBS(["await", "appsession", app["Id"]], fmt="json")
            for ad in appdata:
                proj = ad["Project"]
                prname = proj["Name"]
                if prname != "Unindexed Reads" and not prname in projects:
                    projects.append(prname)
        return projects

    def initializeAllDirectories(self):
        runs = self.getAllRuns()
        for run in runs:
            name = run["ExperimentName"]
            sys.stderr.write("{}... ".format(name))
            self.initializeDirectory(name)
            sys.stderr.write("done.\n")

    def callAPI(self):
        print self.callBS(self.args)

    def projectReads(self, proj, token=False, write=False):
        w = toList(self.callBS(["list", "datasets", "--project-name", proj], fmt="json", token=token))
        totalReads = 0
        samples = []
        for entry in w:
            if "Name" in entry:
                name = entry["Name"]
                attr = entry["Attributes"]["common_fastq"]
                nr = int(attr["TotalReadsPF"])
                totalReads += nr
                samples.append([name, nr])
        samples.sort(key=lambda k:k[0])
        if write:
            for s in samples:
                sys.stdout.write("{}\t{}\t{:.2f}%\n".format(s[0], s[1], 100.0 * s[1] / totalReads))

        return (totalReads, samples)

    def runReport(self):
        R = NGSReport(self.args[0], self.args[1], self.args[2], self.args[3])
        R.run(self)

    def main(self):
        if self.command == "list":
            self.getAllRuns(show=True)
        elif self.command == "initdir":
            for name in self.args:
                self.initializeDirectory(name)
        elif self.command == "all":
            self.initializeAllDirectories()
        elif self.command == "api":
            self.callAPI()
        elif self.command == "nreads":
            self.projectReads(self.args[0], write=True)
        elif self.command == "report":
            self.runReport()

