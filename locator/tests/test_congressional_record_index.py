import unittest
import logging
from locator.congressionalrecordindex import CongressionalRecordIndexInputParser
from locator.parser import LocatorParser, OutputParser, clean_line
from locator import process_lines
logger = logging.getLogger(__name__)


class CongressionalRecordIndexLocatorTest(unittest.TestCase):

    def test_I01(self):
        data = b'''I01AAGENES, ALEXA'''
        current_state, _ = process_lines(
            data, (None, b'G2'),
            locator_table=CongressionalRecordIndexInputParser.LOCATOR_TABLE,
            font_table=CongressionalRecordIndexInputParser.FONT_TABLE)
        self.assertEqual(
            current_state[0].get('end'),  '')
        self.assertEqual(
            current_state[0].get('grid'), b'G2')
        self.assertEqual(
            current_state[0].get('start'), '')

    def test_I02(self):
        data = b''' I02see
        '''
        current_state, _ = process_lines(
            data, (None, b'G2'),
            locator_table=CongressionalRecordIndexInputParser.LOCATOR_TABLE,
            font_table=CongressionalRecordIndexInputParser.FONT_TABLE)
        self.assertEqual(
            current_state[0].get('end'),  '</h2>')
        self.assertEqual(
            current_state[0].get('grid'), b'G2')
        self.assertEqual(
            current_state[0].get('start'), '<h2>')

    def test_I03(self):
        data = b''' I03Bills and resolutions cosponsored
        '''
        current_state, _ = process_lines(
            data, (None, b'G2'),
            locator_table=CongressionalRecordIndexInputParser.LOCATOR_TABLE,
            font_table=CongressionalRecordIndexInputParser.FONT_TABLE)
        self.assertEqual(
            current_state[0].get('end'),  '</h2>')
        self.assertEqual(
            current_state[0].get('grid'), b'G2')
        self.assertEqual(
            current_state[0].get('start'), '<h2>')

    def test_I05(self):
        from locator.congressionalrecordindex import CongressionalRecordIndexInputParser
        data = b'''I05Committee to escort Japanese Prime Minister, Shinzo Abe, into the House Chamber, H2503 [29AP]
        '''
        current_state, _ = process_lines(
            data, (None, b'G2'),
            locator_table=CongressionalRecordIndexInputParser.LOCATOR_TABLE,
            font_table=CongressionalRecordIndexInputParser.FONT_TABLE)
        self.assertEqual(
            current_state[0].get('end'),  '</p>')
        self.assertEqual(
            current_state[0].get('grid'), b'G2')
        self.assertEqual(
            current_state[0].get('start'), '<p>')

    def test_first_stanza(self):
        '''a stanza is what I'm calling the first section in the giant locator
        file, it will be the first section split into a separate file.
        '''
        data = b'''F8383

I01RYAN PURCELL FOUNDATION
I03Remarks in House
I05Anderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE]
I05Doctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE]
'''
        parser = LocatorParser(inputdata=data,
                               inputparser=CongressionalRecordIndexInputParser(),
                               outputparser=OutputParser())
        for output_tuple in parser.parse():
            name, output = output_tuple
            self.assertEqual(
            "<h2>\nRemarks in House\n\n</h2>\n<p>\nAnderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE]\n\n</p>\n<p>\nDoctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE]\n</p>\n",
                output.read())

    def test_split_stanza(self):
        '''a stanza is a section of the locator file that will be split into
        a generated html file.
        Stanzas start with \x07I01.
        '''
        data = b'''F8383

I01RYAN PURCELL FOUNDATION
I03Remarks in House
I05Anderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE]
I05Doctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE]

I01Second stanza RYAN PURCELL FOUNDATION
I03Remarks in House
I05Anderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE]
I05Doctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE]
'''
        parser = LocatorParser(inputdata=data,
                               inputparser=CongressionalRecordIndexInputParser(),
                               outputparser=OutputParser())

        for num , output in enumerate( parser.parse()):
            name, iostream = output
            if num == 0:
                #self.assertEqual(name, b'RYAN-PURCELL-FOUNDATION.htm')
                self.assertEqual(
                    "<h2>\nRemarks in House\n\n</h2>\n<p>\nAnderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE]\n\n</p>\n<p>\nDoctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE]\n</p>\n",
                    iostream.read())
            else:
                #self.assertEqual(name, b'Second-stanza-RYAN-PURCELL-FOUNDATION.htm')
                self.assertEqual(
                    "<h2>\nRemarks in House\n\n</h2>\n<p>\nAnderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE]\n\n</p>\n<p>\nDoctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE]\n</p>\n",
                    iostream.read())



    def test_convert_name (self):
        '''Check to see if we are converting properly the non ascii names of output files. '''

        data = b'''I01ACEVEDO-VILA\xffAE1-ANI\xffAE1BAL
I03Remarks in House
I05Anderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE]
I05Doctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE]
'''

        parser = LocatorParser(inputdata=data,
                               inputparser=CongressionalRecordIndexInputParser(),
                               outputparser=OutputParser())
        for output_tuple in parser.parse():
            name, output = output_tuple
            self.assertEqual(name,  b'ACEVEDO-VIL&#193;-AN&#205;BAL.htm')
