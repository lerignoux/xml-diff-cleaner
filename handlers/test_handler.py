# Handler to use perforce files
import logging

log = logging.getLogger(__name__)


class testHandler(object):

    name = 'test'

    def __init__(self, conf):
        self.files = {
            'test' : {
                'file': {"filename":"test.xml",
                         "content": "First test file with simple content\nEnd\n"},
                'base_file': {"filename":"base/test.xml",
                              "content": "First test file has been changed with simple content\nEnd\n"}
            },
            'addition' : {
                'file': {"filename":"addition.xml",
                         "content": "First test file with simple content\nEnd\n"},
                'base_file': {"filename":"base/addition.xml",
                              "content": "First test file with simple content\nA new line was added\nEnd\n"}
            },
            'removal' : {
                'file': {"filename":"removal.xml",
                         "content": "First test file with simple content\nA line that will be removed\nEnd\n"},
                'base_file': {"filename":"base/removal.xml",
                              "content": "First test file with simple content\nEnd\n"}
            }
        }

    def listFiles(self):
        """
        Return the list of files and their base versions for diff
        """
        return self.files.keys()

    def getFile(self, filename):
        """
        Returns {
            'file':'***********,
            'base_file':'*************'
        }
        """
        return self.files[filename]

    def saveFile(self, file_name, file_content):
        """
        Save the file after diff cleaning
        """
        log.info("saving file %s: %s" %(file_name, file_content))

    def refresh(self):
        return

    def destroy(self):
        pass
