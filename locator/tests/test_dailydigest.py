import unittest
import logging
from locator.dailydigest import DailyDigestInputParser
from locator.parser import LocatorParser, OutputParser
logger = logging.getLogger(__name__)


class DailydigestTest(unittest.TestCase):

    def test_all(self):
        '''Check to see if a mini daily digest file is able to be converted.'''
        import os
        TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'dtestPageWhitespace.rec')

        final = ""
        with open (TESTDATA_FILENAME, "rb") as data:
            parser = LocatorParser(inputdata=data,
                                inputparser=DailyDigestInputParser(),
                                outputparser=OutputParser())
            for outputstream in parser.parse():
                outputstream.seek(0)
                final="%s%s" % (final , outputstream.read())
            print (final)
        self.assertEqual(final,  '''<html><h3><em>Tuesday, September 6, 2016<br /></em></h3><center><h1>Daily Digest<br /></h1></center><h4>HIGHLIGHTS <br /></h4><br /><p><strong>Petitions and Memorials:<br /></strong><pre><strong>Pages S5276&ndash;77<br /></strong></pre><br /><p><strong>Additional Cosponsors:<br /></strong><pre><strong>Pages S5279&ndash;81
<br /></html>''')
