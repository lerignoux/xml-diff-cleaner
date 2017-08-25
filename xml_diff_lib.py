#!/usr/bin/python
import copy
import logging
import re
import hashlib

from difflib import Differ

log = logging.getLogger(__name__)


class NoCleanDiffException(Exception):
    pass


class UnimplementedDiffMode(Exception):
    pass


class XmlDiffLib(object):
    """
    """
    def __init__(self, source, target):
        self.source = source.splitlines(1)
        self.target = target.splitlines(1)
        self.unidiffGroups = {}
        self.xmlDiffGroups = {}
        log.debug("XmlDiffLib __init__ done")

    def getDiff(self, mode='unidiff'):
        self.diff = list(Differ().compare(self.source, self.target))
        self.getUnidiffItems()
        if mode == 'unidiff':
            return self.unidiffGroups
        elif mode == 'xml':
            ## We gorup Xmldiffs together
            return self.getXmlDiff(self.unidiffGroups)
        raise UnimplementedDiffMode()

## ************************ Unidif methods ************************** ##

    def addUnidiffItem(self, item, index):
        log.debug("Adding new diff item :")
        log.debug(item)
        hashId = hashlib.md5()
        hashId.update(repr(item).encode('utf-8'))
        itemId = hashId.hexdigest()
        if itemId in self.unidiffGroups:
            self.unidiffGroups[itemId]['indexes'].append(index)
        else:
            self.unidiffGroups[itemId] = {
                'indexes': [index],
                'diff': item
            }

    def getUnidiffItems(self):
        """
        Regroup diff similarities (similar additions, removal ...)
        """
        index = 0
        length = 1
        log.debug("Unidiff lines count: %d" % len(self.diff))
        while index < len(self.diff):
            line = self.diff[index]
            log.debug(self.diff[index])
            if self.diff[index][0:2] != '  ':
                while index+length < len(self.diff) and self.diff[index+length][0:2] != '  ':  # No diff
                    length+=1
                print("New Diff found : ")
                print(self.diff[index:index+length])
                self.addUnidiffItem(self.diff[index:index+length], index)
                index+=length
                length = 1
            else:
                index+=1

## ************************ XML diff methods ************************** ##

    def getXmlDiff(self, unidiff):
        updated = copy.deepcopy(unidiff)
        for h in updated:
            try:
                updated[h]['diff'] = self.unidiffToXml(updated[h]['diff'])
            except NoCleanDiffException:
                pass
        return updated

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

    def getPrintIndexes(self, full_print):
        res = []
        current_low = None
        for i, p in enumerate(full_print):
            if p != ' ':
                if current_low is None:
                    current_low = i
                else:
                    current_high = i
            elif current_low is not None and current_high is not None:
                res.append((current_low, current_high))
                current_low = None
        return res

    def getItemIndexes(self, item, full_print):
        indexes = getPrintIndexes(full_print)
        res = []
        for low, high in indexes:
            while low-1 > 0 and item[low-1] != ' ':
                low-=1
            while high < len(item) and item[high+1] != ' ':
                high+=1
            res.append((low, high))


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
        full_print = rm
        if not full_print:
            full_print = add
        else:
            if add:
                # We combine both prints
                for i, p in enumerate(add):
                    if p:
                        full_print[i] = p
        if not full_print:
            raise Exception("must provide a diff print")
        else:
            log.debug("print provided : %s" % full_print)
        log.debug("Getting diff items on %s" % items)
        title = items.split(' ', 1)[0]
        diffs = []
        while low < len(items):
            log.debug(diffs)
            high = low + 1
            while high < len(full_print) and full_print[high] != ' ':
                high += 1
            log.debug(full_print[low:high])
            if '^' in full_print[low:high]:
                diffs.append((title, old[low:high], new[low:high]))
                low = high + 1
            if '-' in full_print[low:high]:
                diffs.append((title, old[low:high], ''))
                low = high + 1
            if '+' in full_print[low:high]:
                diffs.append((title, '', new[low:high]))
                low = high + 1
            sleep(10)

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
            return res + unidiffToXml(remains)
        else:
            return res

    def diffRemoveValue(self, item):
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

        res = self.getEditPosItem(old, rm, new, None)

        remains = item[3:]
        if len(remains) > 0:
            return res + unidiffToXml(remains)
        else:
            return res

    def diffAddValue(self, item):
        """
        value addition, removal + other value edit
          -
          ?    ---       ^
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
            return res + unidiffToXml(remains)
        else:
            return res

    def diffRemove(self, item):
        removals = 0
        while removals+1 <= len(items) and item[removals+1][0] == '-':
            removals +=1
        res = []
        for removed in range(removals):
            res.append(item[removed][2:])
        if removals == len(items):
            return res + unidiffToXml(items[removals:])
        else:
            return res

    def diffAdd(self, item):
        additions = 0
        while additions+1 <= len(items) and item[additions+1][0] == '-':
            additions +=1
        res = []
        for added in range(additions):
            res.append(item[added][2:])
        if removals == len(items):
            return res + unidiffToXml(items[removals:])
        else:
            return res


testFile1 = """
<AnimalPersonalities>
    <Duck type=Generic>
        <hp value=200/>
        <attack value=50/>
    </Duck>
    <Bear type=undead>
        <hp value=200/>
        <attack value=50/>
    </Bear>
    <Dog type=undead>
        <hp value=100/>
        <attack value=30 tag=1/>
    </Dog>
    <Lion>
        <hp value=200/>
        <attack value=50/>
    </Lion>
    <Mouse>
    </Mouse>
</AnimalPersonalities>
"""

testFile2 = """
<Animal>
    <Duck type=Generic skin=flashy>
        <hp value=200/>
        <attack value=40/>
    </Duck>
    <Bear type=undead>
        <hp value=300/>
        <attack value=30 tag=1/>
    </Bear>
    <Dog type=undead>
        <hp value=100/>
        <attack value=30 tag=1/>
    </Dog>
    <Lion>
        <priority value=50/>
        <hp value=200/>
        <attack value=50/>
        <preys>
          <cat/>
          <mouse/>
        </preys>
    </Lion>
    <Cat>
        <hp value=20/>
    </Cat>
</Animal>
"""

if __name__ == "__main__":
    print("testing XmlDiffLib")
    diff = XmlDiffLib(testFile1, testFile2)
    from pprint import pprint
    diffs = diff.getDiff()
    pprint(diffs)
    for d in diffs:
        pprint(diff.explainDiff(diffs[d]))
