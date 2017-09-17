#!/usr/bin/python
import json
import logging
import re
import sys
import tkinter

from functools import partial

from xml_diff_lib import XmlDiffLib

from handlers.test_handler import testHandler
from handlers.p4_handler import p4Handler

log = logging.getLogger(__name__)


def get_handler(handler_name):
    if handler_name == 'test':
        return testHandler
    elif handler_name == 'p4':
        return p4Handler
    else:
        raise Exception("unsupported handler")

class Colors(object):
    bg = "#555555"
    fg = "#eeeeee"
    add = "#00aa00"
    remove = "#aa0000"
    change = "#999999"

class diffWindow(tkinter.Tk):
    def __init__(self, parent, handler, diff_mode='xml'):
        tkinter.Tk.__init__(self, parent)
        self.diff_mode = diff_mode
        self.geometry("1260x800+100+100")
        self.colors = Colors()
        self.configure(background=self.colors.bg)
        self.parent = parent
        self.read_conf()
        self.init_handler(handler)
        self.init_window()

    def read_conf(self):
        with open('config.json', 'r') as f:
            self.conf = json.load(f)

    def init_handler(self, handler):
        self.handler = get_handler(handler)(self.conf.get(handler, {}))

    def init_window(self):
        self.grid()

        self.initFilesButtons()
        self.initializeDiffFrame()

        # self.grid_columnconfigure(0,weight=1)
        self.resizable(True,True)
        self.update()
        self.geometry(self.geometry())

    def initFilesButtons(self):
        """
            Create each buttons for diff-able frames
        """
        self.filesButtons = []
        for bIndex, file_name in enumerate(self.handler.listFiles()):
            bCommand = partial(self.SelectFile, bIndex=bIndex, file_name=file_name)
            self.filesButtons.append(tkinter.Button(self,text=file_name, command=bCommand, fg=self.colors.fg, bg=self.colors.bg))
            self.filesButtons[bIndex].grid(column=bIndex,row=0,sticky='W')

    def initializeDiffFrame(self):
        self.columns = len(self.handler.listFiles())

    def updateUnidiffFrame(self, diffs):
        line = 0;
        for d in diffs:
            line += 1
            self.labelSourceTitle = tkinter.StringVar()
            label = tkinter.Label(self,
                textvariable=self.labelSourceTitle,
                anchor="w", fg=self.colors.fg, bg=self.colors.bg
            )
            label.grid(column=0,row=line,columnspan=self.columns,sticky='W')
            self.labelSourceTitle.set(u"Diff :")

            for line_diff in diffs[d]['diff']:
                line += 1
                bg_color = self.colors.change
                if line_diff[0] == '+':
                    bg_color = self.colors.add
                if line_diff[0] == '-':
                    bg_color = self.colors.remove
                label = tkinter.Label(self,
                    text=line_diff,
                    anchor="w", fg="white", bg=bg_color,
                    justify="left", font=("Fixedsys", 7)
                )
                label.grid(column=0,row=line,columnspan=self.columns,sticky='W')

    def updateDiffFrame(self, diffs):
        line = 0;
        print(diffs)
        for d in diffs:
            for part in diffs[d]['diff']:
                # part is a tupple: (name, removed, added)
                line += 1
                self.labelSourceTitle = tkinter.StringVar()
                label = tkinter.Label(self,
                    textvariable=self.labelSourceTitle,
                    anchor="w", fg="white"
                )
                label.grid(column=0,row=line,columnspan=self.columns,sticky='W')
                self.labelSourceTitle.set(part[0])

                line += 1
                if not part[1]:
                    label = tkinter.Label(self,
                        text=part[2],
                        anchor="w", fg="white", bg="green",
                        justify="left", font=("Fixedsys", 7)
                    )
                elif not part[2]:
                    label = tkinter.Label(self,
                        text=part1,
                        anchor="w", fg="white", bg="red",
                        justify="left", font=("Fixedsys", 7)
                    )
                else:
                    label = tkinter.Label(self,
                        text='\n'.join(part[1:]),
                        anchor="w", fg="white", bg="gray",
                        justify="left", font=("Fixedsys", 7)
                    )

                label.grid(column=0,row=line,columnspan=self.columns,sticky='W')

    def displayDiff(self, current_file):
        log.debug("Getting file diff")
        diff = XmlDiffLib(current_file['file']['content'],
                          current_file['base_file']['content']).getDiff(mode=self.diff_mode)
        log.info("Diff received %s" % diff)
        if self.diff_mode == 'unidiff':
            self.updateUnidiffFrame(diff)
        else:
            self.updateDiffFrame(diff)


    def SelectFile(self, bIndex, file_name):
        current_file = self.handler.getFile(file_name)
        self.displayDiff(current_file)
        self.filesButtons[bIndex].focus()

    def IntegrateDiff(self, diff):
        return

    def RemoveDiff(self, diff):
        return
