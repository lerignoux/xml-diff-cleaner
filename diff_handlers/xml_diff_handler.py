import logging
import re

from diff_handlers.diff_handler import diffHandler
from diff_handlers.unidiff_handler import unidiffHandler

log = logging.getLogger(__name__)


class NoCleanDiffException(Exception):
    pass


class xmlDiffHandler(diffHandler):

    mask_keys = ['^', '+', '-']

    def getDiffBase(self):
        return unidiffHandler(self.source, self.target).getDiffs()

    def refreshDiffs(self):
        base_diff = self.getDiffBase()
        self.diffs = {}
        log.debug("Converting %d diff blocks from unidiff to xml diff." % len(base_diff))
        for uid in base_diff:
            try:
                xml_diff = self.unidiffToXml(base_diff[uid]['diff'])
                self.addDiffItem(xml_diff, base_diff[uid]['indexes'])
            except NoCleanDiffException:
                self.addDiffItem(base_diff[uid]['diff'], base_diff[uid]['indexes'])
                pass

    def unidiffToXml(self, diff):
        handles = [
            {'regex': r"\-\?\+\?", 'method': 'diffEdit'},  # edit
            {'regex': r"\-\?\+", 'method': 'diffRemoveValue'},  # values removed
            {'regex': r"\-\+\?", 'method': 'diffAddValue'},  # values added
            {'regex': r"\-+", 'method': 'diffRemove'},  # lines removed
            {'regex': r"\++", 'method': 'diffAdd'},  # lines added
        ]
        while len(diff) > 0:
            log.debug("Current diff length : %d" % len(diff))
            diffPrint = ''.join([line[0] for line in diff])
            log.debug("current diff print %s" % diffPrint)
            for handleType in handles:
                if re.search(handleType['regex'], diffPrint):
                    return getattr(self, handleType['method'])(diff)

    def getPrintIndexes(self, diff_mask):
        res = []
        current_low = None
        for i, p in enumerate(diff_mask):
            if p != ' ':
                if current_low is None:
                    current_low = i
                else:
                    current_high = i
            elif current_low is not None and current_high is not None:
                res.append((current_low, current_high))
                current_low = None
        return res

    def getItemIndexes(self, item, diff_mask):
        indexes = self.getPrintIndexes(diff_mask)
        res = []
        for low, high in indexes:
            while low-1 > 0 and item[low-1] != ' ':
                low -= 1
            while high < len(item) and item[high+1] != ' ':
                high += 1
            res.append((low, high))

    def getTitle(self, line):
        """
         '+ <test value=0>' return <test
        """
        return "# {title}".format(title=line[2:].split(' ', 1)[0])

    def getChanges(self, line, mask, title=True):
        low = 2
        high = 1
        changes = [self.getTitle(line)] if title else []
        while low < len(mask):
            while low < len(mask) and mask[low] == ' ':
                low += 1
            high = low + 1
            while high < len(mask) and mask[high] != ' ':
                high += 1
            log.debug(mask[low:high])
            if '^' in mask[low:high]:
                while line[low] != ' ':  # we want to know what value was changed
                    low -= 1
                changes.append('e '+line[low:high])
                low = high + 1
            if '-' in mask[low:high]:
                changes.append('- '+line[low:high])
                low = high + 1
            if '+' in mask[low:high]:
                changes.append('+ '+line[low:high])
                low = high + 1
            low = high
        return changes

    def diffEdit(self, item):
        """
        value addition, removal + other value edit
          -
          ?    ---       ^
          +
          ?         ++++ ^
        fingerprint [(Added item, None, Added value),(Removed item, Removed value, None),(Changed item, old value, new value)]
        """
        old = item[0]
        rm = item[1]
        new = item[2]
        add = item[3]

        res = self.getChanges(old, rm) + self.getChanges(new, add, title=False)

        remains = item[4:]
        if len(remains) > 0:
            return res + self.unidiffToXml(remains)
        else:
            return res

    def diffRemoveValue(self, item):
        """
        value removal
          -
          ?    ---       ^
          +
        fingerprint [(Added item, None, Added value),(Removed item, Removed value, None),(Changed item, old value, new value)]
        """
        old = item[0]
        rm = item[1]
        # new = item[2]

        res = self.getChanges(old, rm)

        remains = item[3:]
        if len(remains) > 0:
            return res + self.unidiffToXml(remains)
        else:
            return res

    def diffAddValue(self, item):
        """
        value addition
          -
          +
          ?         ++++ ^
        fingerprint [(Added item, None, Added value),(Removed item, Removed value, None),(Changed item, old value, new value)]
        """
        log.debug("diffAddValue found")
        # old = item[0]
        new = item[1]
        add = item[2]

        res = self.getChanges(new, add)

        remains = item[3:]
        if len(remains) > 0:
            return res + self.unidiffToXml(remains)
        else:
            return res

    def diffRemove(self, item):
        removals = 1
        while removals+1 < len(item) and item[removals+1][0] == '-':
            removals += 1
        res = []
        for removed in range(removals):
            res.append(item[removed])
        if removals < len(item):
            return res + self.unidiffToXml(item[removals:])
        else:
            return res

    def diffAdd(self, item):
        additions = 1
        print("debug %s" % item)
        while additions+1 < len(item) and item[additions+1][0] == '-':
            additions += 1
        res = []
        for added in range(additions):
            res.append(item[added])
        if additions < len(item):
            return res + self.unidiffToXml(item[additions:])
        else:
            return res
