import logging
import re

from diff_handlers.diff_handler import diffHandler
from diff_handlers.unidiff_handler import unidiffHandler

log = logging.getLogger(__name__)


class NoCleanDiffException(Exception):
    pass


class xmlDiffHandler(diffHandler):

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
            {'regex':r"\-\?\+\?", 'method': 'diffEdit'},  # edit
            {'regex':r"\-\?\+", 'method': 'diffRemoveValue'},  # values removed
            {'regex':r"\-\+\?", 'method': 'diffAddValue'},  # values added
            {'regex':r"\-+", 'method': 'diffRemove'},  # lines removed
            {'regex':r"\++", 'method': 'diffAdd'},  # lines added
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
        indexes = getPrintIndexes(diff_mask)
        res = []
        for low, high in indexes:
            while low-1 > 0 and item[low-1] != ' ':
                low-=1
            while high < len(item) and item[high+1] != ' ':
                high+=1
            res.append((low, high))

    def getFullMask(self, rm=None, add=None):
        mask = rm
        if not mask:
            mask = add
        else:
            if add:
                mask = list(mask)
                # We combine both prints
                for i, p in enumerate(add):
                    if p:
                        mask[i] = p
                ''.join(mask)
        if not mask:
            raise Exception("A diff mask is required to get the xml diff")
        return mask

    def getEditPosItem(self, old=None, rm=None, new=None, add=None):
        """
        for "1111 2222222 3333 444  55555555 6666"
            "        ^     ---  ++            -- "
        returns :
        [222222, 3333, 444, 6666]
        """
        from time import sleep
        low = 0
        high = 1
        items = old or new
        if not items:
            raise Exception("Must provide items")
        else:
            log.debug("items provided : %s" % items)
        diff_mask = self.getFullMask(rm=rm, add=add)
        log.debug("mask provided : %s" % diff_mask)
        title = items.split(' ', 1)[0]
        diffs = []
        while low < len(diff_mask):
            while low < len(diff_mask) and diff_mask[low] == ' ':
                low += 1
            high = low + 1
            while high < len(diff_mask) and diff_mask[high] != ' ':
                high += 1
            log.debug(diff_mask[low:high])
            if '^' in diff_mask[low:high]:
                diffs.append((title, old[low:high], new[low:high]))
                low = high + 1
            if '-' in diff_mask[low:high]:
                diffs.append((title, old[low:high], ''))
                low = high + 1
            if '+' in diff_mask[low:high]:
                diffs.append((title, '', new[low:high]))
                low = high + 1
            low = high
        log.debug("Diffs found : %s" % diffs)
        return diffs

    def diffEdit(self, item):
        """
        value addition, removal + other value edit
          -
          ?    ---       ^
          +
          ?         ++++ ^
        fingerprint [(Added item, None, Added value),(Removed item, Removed value, None),(Changed item, old value, new value)]
        """
        old = item[0][2:]
        rm = item[1][2:]
        new = item[2][2:]
        add = item[3][2:]

        res = self.getEditPosItem(old, rm, new, add)

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
        old = item[0][2:]
        rm = item[1][2:]
        new = item[2][2:]

        res = self.getEditPosItem(old, rm, new, None)

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
        old = item[0][2:]
        new = item[1][2:]
        add = item[2][2:]

        res = self.getEditPosItem(old, None, new, add)

        remains = item[3:]
        if len(remains) > 0:
            return res + self.unidiffToXml(remains)
        else:
            return res

    def diffRemove(self, item):
        removals = 0
        while removals+1 < len(item) and item[removals+1][0] == '-':
            removals +=1
        res = []
        for removed in range(removals):
            res.append(item[removed][2:])
        if removals < len(item):
            return res + self.unidiffToXml(item[removals:])
        else:
            return res

    def diffAdd(self, item):
        additions = 0
        print("debug %s" % item)
        while additions+1 < len(item) and item[additions+1][0] == '-':
            additions +=1
        res = []
        for added in range(additions):
            res.append(item[added][2:])
        if additions < len(item):
            return res + self.unidiffToXml(item[additions:])
        else:
            return res
