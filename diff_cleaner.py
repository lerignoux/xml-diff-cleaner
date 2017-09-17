import argparse
import logging
import sys

from diff_window import diffWindow

parser = argparse.ArgumentParser(description='Clean some simple recuring diff in files.')
parser.add_argument('--file-handler', '-f', dest='handler',
                    default='p4', choices=['test', 'p4'],
                    help='What file handler use')
parser.add_argument('--diff', '-d', dest='diff_mode',
                    default='unidiff', choices=['unidiff', 'xml'],
                    help='what diff type do you want to display.')

if __name__ == "__main__":

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    args = parser.parse_args()
    app = diffWindow(parent=None, handler=args.handler, diff_mode=args.diff_mode)
    app.title('%s Diff changes selector' % app.handler.name)
    app.mainloop()
    # app.disconnectP4() ##FIXME Probably need safe cleaning
