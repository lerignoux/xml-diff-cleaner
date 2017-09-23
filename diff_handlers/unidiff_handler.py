import logging
from diff_handlers.diff_handler import diffHandler

log = logging.getLogger(__name__)


class unidiffHandler(diffHandler):

    def refreshDiffs(self):
        """
        Regroup diff groups
        """
        base_diff = self.getDiffBase()
        self.diffs = {}
        index = 0  # diff_index
        s_index = 0  # source_index
        s_length = 0
        t_index = 0  # target_index
        t_length = 0
        length = 0
        log.debug("Unidiff lines count: %d" % len(base_diff))
        while index < len(base_diff):
            log.debug(base_diff[index])
            if base_diff[index][0:2] != '  ':
                while index+length < len(base_diff) and base_diff[index+length][0:2] != '  ':
                    if base_diff[index+length][0:2] == '+ ':
                        log.debug('t_length++')
                        t_length += 1
                    elif base_diff[index+length][0:2] == '- ':
                        log.debug('s_length++')
                        s_length += 1
                    length += 1
                print("New Diff found : ")
                print(base_diff[index:index+length])
                self.addDiffItem(
                    base_diff[index:index+length],
                    [{
                        'diff_index': index,
                        'source_index': s_index, 'source_length': s_length,
                        'target_index': t_index, 'target_length': t_length
                    }])
                index += length
                s_index += s_length
                t_index += t_length
                length = 0
                s_length = 0
                t_length = 0
            else:
                #  Unchanged line
                index += 1
                s_index += 1
                t_index += 1
