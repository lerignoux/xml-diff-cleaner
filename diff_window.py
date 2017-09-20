#!/usr/bin/python
import json
import logging
import re
import sys
import tkinter

from functools import partial

from xml_diff_lib import XmlDiffLib

from file_handlers.test_handler import testHandler
from file_handlers.p4_handler import p4Handler

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
    change = "#ff8c00"

    def __init__(self, conf):
        for color in conf:
            setattr(self, color, conf[color])

class diffWindow(tkinter.Tk):
    def __init__(self, parent, handler, diff_mode='xml'):
        tkinter.Tk.__init__(self, parent)
        self.read_conf()
        self.diff_mode = diff_mode
        self.geometry("1260x800+100+100")
        self.colors = Colors(self.conf.get('colors', {}))
        self.configure(background=self.colors.bg)
        self.parent = parent
        self.init_handler(handler)
        self.init_window()

    def read_conf(self):
        with open('config.json', 'r') as f:
            self.conf = json.load(f)

    def init_handler(self, handler):
        self.handler = get_handler(handler)(self.conf.get(handler, {}))

    def init_window(self):
        self.grid()
        self.grid_garbage = []

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

        save_button = tkinter.Button(self,text="save file", command=self.saveFile, fg=self.colors.fg, bg=self.colors.bg)
        save_button.grid(column=bIndex+1,row=0,sticky='E')

    def initializeDiffFrame(self):
        self.columns = len(self.handler.listFiles()) + 1

    def add_to_grid(self, obj, column=0, row=0, sticky='W', columnspan=1):
        self.grid_garbage.append(obj)
        getattr(obj, 'grid')(column=column, row=row, sticky=sticky, columnspan=columnspan)

    def clean_grid(self):
        for obj in self.grid_garbage:
            obj.grid_forget()
        del self.grid_garbage
        self.grid_garbage = []

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
                self.add_to_grid(label, row=line, columnspan=self.columns)

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
                    anchor="w", fg=self.colors.fg, bg=self.colors.bg
                )
                self.add_to_grid(label, row=line, columnspan=self.columns)
                self.labelSourceTitle.set(part[0])

                line += 1
                if not part[1]:
                    label = tkinter.Label(self,
                        text=part[2],
                        anchor="w", fg="white", bg=self.colors.add,
                        justify="left", font=("Fixedsys", 7)
                    )
                elif not part[2]:
                    label = tkinter.Label(self,
                        text=part1,
                        anchor="w", fg="white", bg=self.colors.remove,
                        justify="left", font=("Fixedsys", 7)
                    )
                else:
                    label = tkinter.Label(self,
                        text='\n'.join(part[1:]),
                        anchor="w", fg="white", bg=self.colors.change,
                        justify="left", font=("Fixedsys", 7)
                    )

                self.add_to_grid(label, row=line, columnspan=self.columns)
                self.addCleanDiffButton(row=line, diff_id = d)

    def addCleanDiffButton(self, row, diff_id):
        """
            Create a button to revert a diff
        """
        self.revertButtons = []
        bCommand = partial(self.revertDiff, diff_id=diff_id)
        button = tkinter.Button(self, text="revert", command=bCommand, fg=self.colors.fg, bg=self.colors.bg)
        self.add_to_grid(button, column=self.columns-1, row=row, sticky='E')

    def displayDiff(self):
        self.clean_grid()
        log.debug("Getting file diff")
        diffs = self.currentDiffApi.getDiffs()
        log.info("Diff received %s" % diffs)
        if self.diff_mode == 'unidiff':
            self.updateUnidiffFrame(diffs)
        else:
            self.updateDiffFrame(diffs)

    def revertDiff(self, diff_id):
        self.currentDiffApi.revertDiff(diff_id)
        self.displayDiff()

    def SelectFile(self, bIndex, file_name):
        current_file = self.handler.getFile(file_name)
        self.currentDiffApi = XmlDiffLib(current_file['base_file']['content'],
                                         current_file['file']['content'],
                                         mode=self.diff_mode)
        self.displayDiff()
        self.filesButtons[bIndex].focus()
        self.current_file_name = file_name

    def saveFile(self):
        self.handler.saveFile(self.current_file_name, self.currentDiffApi.getFileContent())

    def IntegrateDiff(self, diff):
        return

    def RemoveDiff(self, diff):
        return
