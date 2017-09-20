#!/usr/bin/python
import copy
import logging

from diff_handlers.unidiff_handler import unidiffHandler
from diff_handlers.xml_diff_handler import xmlDiffHandler

log = logging.getLogger(__name__)


class UnimplementedDiffMode(Exception):
    pass


class XmlDiffLib(object):

    def __init__(self, source, target, mode='unidiff'):
        self.source = source.splitlines(1)
        self.target = target.splitlines(1)
        self.backup = copy.deepcopy(target)
        if mode == 'unidiff':
            self.handler = unidiffHandler(self.source, self.target)
        elif mode == 'xml':
            self.handler = xmlDiffHandler(self.source, self.target)
        else:
            raise UnimplementedDiffMode()
        log.debug("XmlDiffLib __init__ done")

    def getDiffs(self):
        return self.handler.getDiffs()

    def revertDiff(self, diff_id):
        self.handler.revertDiff(diff_id)
        self.target = '\n'.join(self.handler.getTarget())
        log.info("File after revert:\n%s" % self.target)
        return self.getDiffs()

    def getFileContent(self):
        return self.target
