#!/usr/bin/python
import json
import logging
import re
import sys
import tkinter

from P4 import P4
from functools import partial

from grouped_diff import XmlDiffLib

log = logging.getLogger(__name__)

class xml_diff_cleaner(tkinter.Tk):
    def __init__(self, parent, source_data, target_data):
        tkinter.Tk.__init__(self,parent)
        self.geometry("1260x800+100+100")
        self.parent = parent
        self.source_data = source_data
        self.target_data = target_data
        self.initialize()

    def initialize_config(self):
        with open('config.json', 'w') as f:
            self.config = json.dump(config, f)

    def initialize(self):
        self.initialize_config()
        self.initializeP4()
        self.grid()

        self.initializeFiles()
        self.initializeDiffFrame()

        # self.grid_columnconfigure(0,weight=1)
        self.resizable(True,True)
        self.update()
        self.geometry(self.geometry())

    def initializeDiffFrame(self):
        self.columns = len(self.filesButtons)

    def updateDiffFrame(self, diffs):
        line = 0;
        for d in diffs:
            line += 1
            self.labelSourceTitle = tkinter.StringVar()
            label = tkinter.Label(self,
                textvariable=self.labelSourceTitle,
                anchor="w",fg="white"
            )
            label.grid(column=0,row=line,columnspan=self.columns,sticky='W')
            self.labelSourceTitle.set(u"Diff :")

            line += 1
            label = tkinter.Label(self,
                text='\n'.join(diffs[d]['diff']),
                anchor="w",fg="white",bg="green",
                justify="left", font=("Fixedsys", 7)
            )
            label.grid(column=0,row=line,columnspan=self.columns,sticky='W')

    def refreshDiffs(self):
        log.debug("Refreshing file diff")
        diff = XmlDiffLib(self.target_data, self.source_data).getDiff(mode='xml')
        log.inf2o("Diff received %s" % diff)
        self.updateDiffFrame(diff)

    def openXmlFile(self, filename):
        with open(filename) as f:
            return f.read()

    def loadLocalFile(self, openedFile):
        with open(openedFile['localFile'], 'r') as f:
            content = f.read()
        log.debug("Target file loaded: %s ..." % content[0:80])
        self.source_data = u"" + content
        return self.source_data

    def loadLatestFile(self, openedFile):
        content = self.p4.run_print("%s#head" % openedFile['depotFile'])
        if len(content) > 2:
            raise Exception("Wrong file format")
        else:
            title = content[0]
            content = content[1]
            log.debug("Source file loaded: %s ..." % content[0:80])
        self.target_data =  u"" + content
        return self.target_data

    def SelectFile(self, bIndex, openedFile):
        self.loadLocalFile(openedFile)
        self.loadLatestFile(openedFile)
        self.refreshDiffs()
        self.filesButtons[bIndex].focus()

    def IntegrateDiff(self, diff):
        return

    def RemoveDiff(self, diff):
        return

    def initializeFiles(self):
        """
        opened files format :
        [{
            'depotFile': '//project_name/main/data/editor/templates/filename.lib.xml',
            'clientFile': '//client_project_folder/data/editor/templates/filename.lib.xml',
            'rev': '472', 'haveRev': '472', 'action': 'edit', 'change': '3126449', 'type': 'text',
            'user': 'username', 'client': 'client_p4_folder_name'
        }]
        """
        self.filesButtons = []
        for bIndex, openedFile in enumerate(self.getOpenedFiles()):
            localFile = re.sub("//%s" % openedFile['client'], self.p4ClientRoot.replace('\\', '/'), openedFile['clientFile'])
            openedFile['localFile'] = localFile
            log.warning("local file path %s " % localFile)
            log.debug("New file changed : %s != %s" % (openedFile['depotFile'], openedFile['localFile']))
            bCommand = partial(self.SelectFile, bIndex=bIndex, openedFile=openedFile)
            self.filesButtons.append(tkinter.Button(self,text=openedFile['depotFile'], command=bCommand))
            self.filesButtons[bIndex].grid(column=bIndex,row=0,sticky='W')

    def getOpenedFiles(self):
        return self.p4.run_opened()

    def initializeP4(self):
        self.p4 = P4()                        # Create the P4 instance
        self.p4.user = self.self.config["p4"]["username"]
        self.p4.password = self.self.config["p4"]["username"]
        try:
            self.p4.connect()                  # Connect to the Perforce Server
            self.p4ClientRoot = self.p4.run('info')[0]['clientRoot']
            log.warning(self.p4.run('info')[0]['clientRoot'])
        except P4Exception:
            for e in p4.errors:
                print(e)

    def disconnectP4(self):
        self.p4.disconnect()

if __name__ == "__main__":
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app = xml_diff_cleaner(None, u"my source", u"my target")
    app.title('Xml Diff changes selector')
    app.mainloop()
    # app.disconnectP4() ##FIXME Probably need safe cleaning
