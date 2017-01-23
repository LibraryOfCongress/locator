import unittest
import logging
from locator.dailydigest import DailyDigestInputParser
from locator.parser import LocatorParser, OutputParser
from locator import process_escapes_in_line
logger = logging.getLogger(__name__)


class AccentsTest(unittest.TestCase):

    def _load_and_convert(self, filename):
        '''Check to see if a mini daily digest file is able to be converted.'''
        import os
        TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), filename)

        final = ""
        with open (TESTDATA_FILENAME, "rb") as data:
            parser = LocatorParser(inputdata=data,
                                inputparser=DailyDigestInputParser(),
                                outputparser=OutputParser())
            for outputstream in parser.parse():
                outputstream.seek(0)
                final="%s%s" % (final , outputstream.read())
            print (final)
        return final

    def test_process_aacute(self):
        ''' a acute '''
        line = b'Luja\xffAE1n, Ben'
        current_grid = b'G2'
        aline= process_escapes_in_line(line, current_grid)
        self.assertEqual( b"Luj&aacute;n, Ben", aline)

    def test_process_eecute(self):
        ''' e acute '''
        line = b'e\xffAE1'
        current_grid = b'G2'
        aline= process_escapes_in_line(line, current_grid)
        self.assertEqual( b"&eacute;", aline)

    def test_accent_1(self):
        '''Test to convert accents'''
        final = self._load_and_convert('accents.rec')
        self.assertEqual(final,  '''<html><h3><em>Thursday, September 15, 2016 <br /></em></h3>Luj&aacute;n, Ben<br />\n<br /></html>''')
