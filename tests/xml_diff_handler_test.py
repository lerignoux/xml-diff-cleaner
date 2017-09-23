import logging
import unittest

from diff_handlers.xml_diff_handler import xmlDiffHandler

log = logging.getLogger(__name__)


class xmlDiffHandlerTest(unittest.TestCase):

    def setUp(self):
        self.diff_handler = xmlDiffHandler('', '')

    def test_getFullMask(self):
        cases = [
            {'rm': "     ^     ", 'add': "  ++       ", 'res': "  ++ ^     "},
            {'rm': "----------", 'add': "            ", 'res': "----------  "},
            {'rm': " -- ^    ", 'add': "    ^ ++ ", 'res': " -- ^ ++ "},
            {'rm': "----", 'add': "     ++++", 'res': "---- ++++"},
            ]
        for i, case in enumerate(cases):
            self.assertEqual(self.diff_handler.getFullMask(case['rm'], case['add']), case['res'])

    def test_diffEdit(self):
        pass

    def test_diffRemoveValue(self):
        pass

    def test_diffAddValue(self):
        pass

    def test_diffRemove(self):
        self.assertEqual(self.diff_handler.diffRemove(["- 123456789", "- abcd"]), ['123456789', 'abcd'])

    def test_diffAdd(self):
        self.assertEqual(self.diff_handler.diffAdd(["+ 123456789", "+ abcd"]), ['123456789', 'abcd'])


if __name__ == '__main__':
    unittest.main()
