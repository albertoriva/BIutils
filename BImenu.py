#!/usr/bin/env python

__author__    = "Alberto Riva, ICBR Bioinformatics Core"
__contact__   = "ariva@ufl.edu"
__copyright__ = "(c) 2021, University of Florida Foundation"
__license__   = "MIT"
__date__      = "Jul 24 2021"
__version__   = "1.0"

import sys
import readline

QUIT = "q"
BACK = "b"
LIST = "l"
HELP = "h"

class Menu(object):
    choices = []
    submenus = {}
    showBack = True
    showQuit = True
    default = None
    maxchoice = 0
    helptext = None

    def __init__(self, choices=[], Back=True, Quit=True, Default=None, Help=None):
        self.init(choices, Back, Quit, Default, Help)

    def init(self, choices=[], Back=True, Quit=True, Default=None, Help=None):
        self.choices = choices
        self.showBack = Back
        self.showQuit = Quit
        self.default = Default
        self.helptext = Help
        self.helpmsg = "Enter a number between 1 and {}".format(len(self.choices))
        if self.helptext:
            self.helpmsg += ", {} for help".format(HELP)
        if self.showBack:
            self.helpmsg += ", {} to return to the previous menu".format(BACK)
        if self.showQuit:
            self.helpmsg += ", {} to quit the program".format(QUIT)
        self.helpmsg += "."

    def addSubmenu(self, key, menu):
        self.submenus[key] = menu

    def show(self):
        idx = 1
        for ch in self.choices:
            sys.stdout.write("{:3}. {}\n".format(idx, ch[1]))
            idx += 1
        if self.showBack or self.showQuit or self.helptext:
            sys.stdout.write("\n")
        if self.helptext:
            sys.stdout.write("  {}. Display help\n".format(HELP))
        if self.showBack:
            sys.stdout.write("  {}. Return to previous menu\n".format(BACK))
        if self.showQuit:
            sys.stdout.write("  {}. Exit\n".format(QUIT))

    def choose(self):
        validchoices = []
        idx = 1
        for ch in self.choices:
            validchoices.append(str(idx))
            idx += 1
        self.maxchoice = idx
        if self.showBack:
            validchoices.append(BACK)
        if self.showQuit:
            validchoices.append(QUIT)
        if self.default and self.default not in validchoices:
            sys.stderr.write("Warning: default '{}' is not among valid choices.\n".format(self.default))
            self.default = None

        self.show()
        while True:
            try:
                a = input("-> ")
            except EOFError:
                return QUIT
            if a == '' and self.default:
                a = self.default
            if a == "?":
                sys.stdout.write(self.helpmsg + "\n")
            elif a == LIST:
                self.show()
            elif self.showBack and a == BACK:
                return a
            elif self.showQuit and a == QUIT:
                return a
            elif self.helptext and a == HELP:
                sys.stdout.write(self.helptext + "\n")
            elif a in validchoices:
                idx = int(a) - 1
                selected = self.choices[idx][0]
                return selected
                    
            else:
                sys.stdout.write(self.helpmsg + "\n")

if __name__ == "__main__":
    M = Menu([["A", "Elves"], ["B", "Humans"], ["C", "Dwarves"], ["D", "Hobbits"], ["E", "Wizards"]],
             Help="Choose one of the MIddle-Earth species.")
    print(M.choose())
