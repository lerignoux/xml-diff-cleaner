import logging
import unittest

from diff_handlers.xml_diff_handler import xmlDiffHandler

log = logging.getLogger(__name__)


class xmlDiffHandlerTest(unittest.TestCase):

    def setUp(self):
        self.diff_handler = xmlDiffHandler('', '')

    def test_diffEdit(self):
        self.assertEqual(
            self.diff_handler.diffEdit(
                ["- test toto=1 tata=2",
                 "?            -------",
                 "+ test flag=0 toto=1",
                 "?      +++++++             "]
            ),
            ["# test", "-  tata=2", "+ flag=0 "]
        )

    def test_diffRemoveValue(self):
        self.assertEqual(
            self.diff_handler.diffRemoveValue(
                ["- test flag=0 toto=1 tata=2",
                 "?      -------      -------",
                 "+ test toto=1"]
            ),
            ["# test", "- flag=0 ", "-  tata=2"]
        )

    def test_diffAddValue(self):
        self.assertEqual(
            self.diff_handler.diffAddValue(
                ["- test toto=1",
                 "+ test flag=0 toto=1 tata=2",
                 "?      +++++++      +++++++"]
            ),
            ["# test", "+ flag=0 ", "+  tata=2"]
        )

    def test_diffRemove(self):
        self.assertEqual(
            self.diff_handler.diffRemove(["- 123456789", "- abcd"]),
            ['- 123456789', '- abcd']
        )

    def test_diffAdd(self):
        self.assertEqual(
            self.diff_handler.diffAdd(["+ 123456789", "+ abcd"]),
            ['+ 123456789', '+ abcd']
        )


if __name__ == '__main__':
    unittest.main()
