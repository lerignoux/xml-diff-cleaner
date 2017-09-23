import hashlib
import logging

from difflib import Differ

log = logging.getLogger(__name__)


class diffHandler(object):

    def __init__(self, source, target):
        self.diffs = {}
        self.source = source
        self.target = target

    def getDiffBase(self):
        return list(Differ().compare(self.source, self.target))

    def refreshDiffs(self):
        raise Exception("UnimplementedException")

    def getDiffs(self):
        self.refreshDiffs()
        return self.diffs

    def revertDiff(self, diff_id):
        """
        Revert a diff given it's diff id
        """
        diff = self.diffs[diff_id]
        log.debug("reverting diff: %s" % diff)
        for i in diff['indexes']:
            log.debug("reverting to: %s" % (self.source[i['target_index']:(i['target_index']+i['target_length'])]))
            before = self.target[:i['source_index']]
            changed = self.source[i['target_index']:(i['target_index']+i['target_length'])]
            after = self.target[i['source_index']+i['source_length']:]
            self.target = before + changed + after
        log.debug("Target after revert: %s" % self.target)

    def getTarget(self):
        return self.target

    def getDiffHash(self, diff):
        hashId = hashlib.md5()
        hashId.update(repr(diff).encode('utf-8'))
        return hashId.hexdigest()

    def addDiffItem(self, diff, indexes):
        """
        Insert the diff if non existing, add the indexes otherwises.
        indexes is a list of indexes dictionaries
        """
        log.debug("Adding new diff item :")
        log.debug(diff)
        diff_id = self.getDiffHash(diff)
        if diff_id in self.diffs:
            self.diffs[diff_id]['indexes'] += indexes
        else:
            self.diffs[diff_id] = {
                'indexes': indexes,
                'diff': diff
            }
