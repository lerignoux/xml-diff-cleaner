# Handler to use perforce files
import logging

log = logging.getLogger(__name__)

try:
    from P4 import P4
except ImportError:
    log.error("You must install perforce API in order to use the p4 handler")


class p4Handler(object):

    name = 'p4'

    def __init__(self, conf):
        self.conf = conf
        try:
            self.p4 = P4()
        except NameError:
            raise Exception("P4 not found")
        self.p4.user = self.self.conf["username"]
        self.p4.password = self.self.conf["username"]
        try:
            self.p4.connect()                  # Connect to the Perforce Server
            self.p4ClientRoot = self.p4.run('info')[0]['clientRoot']
            log.warning(self.p4.run('info')[0]['clientRoot'])
        except P4Exception:
            for e in p4.errors:
                print(e)

        self.files = {}  # List of files with diff
        self.initFiles()
        log = logging.getLogger(__name__)


    def initFiles(self):
        """
        opened files format :
        [{
            'depotFile': '//project_name/main/data/editor/templates/filename.lib.xml',
            'clientFile': '//client_project_folder/data/editor/templates/filename.lib.xml',
            'rev': '472', 'haveRev': '472', 'action': 'edit', 'change': '3126449', 'type': 'text',
            'user': 'username', 'client': 'client_p4_folder_name'
        }]
        """
        self.files = {}
        for p4File in self.p4.run_opened():
            filename = p4File['clientFile'].split('/')[-1]
            log.info("New file changed: %s " % filename)
            localFile = re.sub("//%s" % openedFile['client'], self.p4ClientRoot.replace('\\', '/'), openedFile['clientFile'])
            self.files[filename] = {
                'file': {'filename': localFile,
                         'content': self.readLocalFile(localFile)},
                'base_file': { 'filename': p4File['depotFile'],
                               'content': self.readLatestFile(p4File['depotFile'])}
            }

    def listFiles(self):
        """
        Return the list of files and their base versions for diff
        """
        return self.files.keys()

    def readLocalFile(self, filename):
        with open(filename, 'r') as f:
            content = f.read()
        log.debug("p4 local file read: %s ..." % content[0:80])
        content = u"" + content
        return content

    def readLatestFile(self, file):
        content = self.p4.run_print("%s#head" % filename)
        if len(content) > 2:
            raise Exception("Wrong file format")
        else:
            title = content[0]
            content = content[1]
            log.debug("p4 latest file read: %s ..." % content[0:80])
        conetn =  u"" + content
        return content

    def getFile(self, filename):
        """
        Returns {
            'file': {'filename': '', 'content': ""},
            'base_file':{'filename': '', 'content': ""}
        }
        """
        return self.files[filename]

    def saveFile(self, file_name, content):
        """
        Save the file after diff cleaning
        """
        with open(self.files[file_name]['file'], 'w') as f:
            content = f.write(content)

    def refresh(self):
        self.initFiles()

    def destroy(self):
        self.p4.disconnect()
