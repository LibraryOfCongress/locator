import unittest
import logging
from locator.congressionalrecordindex import CongressionalRecordIndexInputParser
from locator.parser import LocatorParser, OutputParser
from locator import process_lines
logger = logging.getLogger(__name__)


class CongressionalRecordIndexLocatorTest(unittest.TestCase):

    def test_I01(self):
        data = b'''I01AAGENES, ALEXA'''
        current_state_stack, _ = process_lines(
            data, (None, b'G2'),
            locator_table=CongressionalRecordIndexInputParser.LOCATOR_TABLE,
            font_table=CongressionalRecordIndexInputParser.FONT_TABLE)
        current_state = current_state_stack[-1]
        self.assertEqual(
            current_state[0].get('end'),  '')
        self.assertEqual(
            current_state[0].get('grid'), b'G2')
        self.assertEqual(
            current_state[0].get('start'), '')

    def test_I02(self):
        data = b''' I02see
        '''
        current_state_stack, _ = process_lines(
            data, (None, b'G2'),
            locator_table=CongressionalRecordIndexInputParser.LOCATOR_TABLE,
            font_table=CongressionalRecordIndexInputParser.FONT_TABLE)
        current_state = current_state_stack[-1]
        self.assertEqual(
            current_state[0].get('end'),  '</h2>')
        self.assertEqual(
            current_state[0].get('grid'), b'G2')
        self.assertEqual(
            current_state[0].get('start'), '<h2>')

    def test_I03(self):
        data = b''' I03Bills and resolutions cosponsored
        '''
        current_state_stack, _ = process_lines(
            data, (None, b'G2'),
            locator_table=CongressionalRecordIndexInputParser.LOCATOR_TABLE,
            font_table=CongressionalRecordIndexInputParser.FONT_TABLE)
        current_state = current_state_stack[-1]
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
        current_state_stack, _ = process_lines(
            data, (None, b'G2'),
            locator_table=CongressionalRecordIndexInputParser.LOCATOR_TABLE,
            font_table=CongressionalRecordIndexInputParser.FONT_TABLE)
        current_state = current_state_stack[-1]
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
                               inputparser=CongressionalRecordIndexInputParser(year=2014),
                               outputparser=OutputParser())
        for output_tuple in parser.parse():
            name, output = output_tuple
            self.assertEqual(
            "<h2>Remarks in House\n</h2><p>Anderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE]\n</p><p>Doctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE]</p>",
                output.read())

    def test_make_stanza(self):
        """Test to see stanzas are separated and titles are correctly parsed"""
        data =b'''\x07F89378\n
\x07I01Title
\x07I02 foo
\x07I03bar

\x07I01Second title
\x07I02 foo
\x07I03bar'''

        good_stanzas = [
        b'\x07I01Title\n\x07I02 foo\n\x07I03bar',
        b'\x07I01Second title\n\x07I02 foo\n\x07I03bar' ]
        cnt = 0
        inputparser=CongressionalRecordIndexInputParser(year=2014)
        for stanza in inputparser.make_stanzas(data):
            self.assertEqual( stanza, good_stanzas[cnt])
            cnt = cnt +1

    def _parse_cri_I01(self, data, year):
        parser = LocatorParser(inputdata=data,
                               inputparser=CongressionalRecordIndexInputParser(year=year),
                               outputparser=OutputParser())

        for num , output in enumerate( parser.parse()):
            #name, iostream = output
            yield num, output

    def test_convert_locatorI01_to_mods_title(self):
        '''Convert I01 titles to the mods title locator_title=b'I01A.B.A.T.E. OF ILLINOIS, INC.' '''
        locator_title=b'I01A.B.A.T.E. OF ILLINOIS, INC.'
        for num, output in self._parse_cri_I01(locator_title, 2014):
            (file_name, term_text) , stream = output
            self.assertEqual(term_text, b'A.B.A.T.E. OF ILLINOIS, INC.')
            self.assertEqual(file_name, b'CRI-2014-A-B-A-T-E-OF-ILLINOIS-INC.htm')

    def test_convert_locatorI01_to_mods_title_smith(self):
        locator_title = b'I01A.O. SMITH CORP.'
        for num, output in self._parse_cri_I01(locator_title, 2014):
            (file_name, term_text) , stream = output
            self.assertEqual(term_text, b'A.O. SMITH CORP.')
            self.assertEqual(file_name, b'CRI-2014-A-O-SMITH-CORP.htm')


    def test_convert_mods_title_to_filename(self):
        '''<title>A.B.A.T.E. OF PENNSYLVANIA (organization)</title>  to mods_filename=b'CRI-2014-A-B-A-T-E-OF-PENNSYLVANIA-D033B6.htm' '''
        mods_filename=b'CRI-2014-A-B-A-T-E-OF-PENNSYLVANIA-D033B6.htm'
        mods_title=b'A.B.A.T.E. OF PENNSYLVANIA (organization)'
        result2 = CongressionalRecordIndexInputParser.process_title(2014, mods_title)
        self.assertEquals(mods_filename,  result2)

    def test_convert_locatorI01_to_mods_title_periods_and_paren(self):
        ''' locator_title = b'I01A.B.A.T.E. OF PENNSYLVANIA (organization)' '''
        locator_title = b'I01A.B.A.T.E. OF PENNSYLVANIA (organization)'
        for num, output in self._parse_cri_I01(locator_title, 2014):
            (file_name, term_text) , stream = output
            self.assertEqual(term_text, b'A.B.A.T.E. OF PENNSYLVANIA (organization)')
            self.assertEqual(file_name, b'CRI-2014-A-B-A-T-E-OF-PENNSYLVANIA-D033B6.htm')



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
                               inputparser=CongressionalRecordIndexInputParser(year=2014),
                               outputparser=OutputParser())

        for num , output in enumerate( parser.parse()):
            name, iostream = output
            if num == 0:
                self.assertEqual(name, (b'CRI-2014-RYAN-PURCELL-FOUNDATION.htm', b'RYAN PURCELL FOUNDATION'))
                                 #b'CRI-2014-RYAN-PURCELL-FOUNDATION.htm')
                self.assertEqual(
                    "<h2>Remarks in House\n</h2><p>Anderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE]\n</p><p>Doctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE]</p>",
                    iostream.read())
            else:
                #self.assertEqual(name, b'Second-stanza-RYAN-PURCELL-FOUNDATION.htm')
                self.assertEqual(
                    "<h2>Remarks in House\n</h2><p>Anderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE]\n</p><p>Doctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE]</p>",
                    iostream.read())


    def test_find_escapes(self):
        """Test to make sure find_escapes will find multiple escapes in a line"""
        from locator import find_escape
        data = b'''I01ACEVEDO-VILA\xffAE1, ANI\xffE1BAL g009T1(a former Resident Commissioner from Puerto Rico)\xff1A'''
        cnt = 0
        good_escape = [b'AE1', b'E1',b'1A' ]
        good_replace =[b'A', b'I', b')' ]
        for found in find_escape(data, current_grid='G2'):
            esc = found.group('esc')
            replace= found.group('replace')
            self.assertEqual( esc,good_escape[cnt] )
            self.assertEqual( replace, good_replace[cnt])
            cnt = cnt+1


    def test_process_escapes(self):
        '''Process multiple escapes in one line'''
        data = b'''I01ACEVEDO-VILA\xffAE1, ANI\xffE1BAL g009T1(a former Resident Commissioner from Puerto Rico)\xff1A'''
        from locator.congressionalrecordindex  import FakeEscapeSequences
        from locator import process_escapes_in_line
        fs = FakeEscapeSequences()

        data = b'''I01ACEVEDO-VILA\xffAE1, ANI\xffE1BAL g009'''
        cleaned_line = process_escapes_in_line(data, 'G2', escape_sequences=fs)
        self.assertEquals(cleaned_line, b'''I01ACEVEDO-VILA, ANIBAL g009''')

        data = b'''I01ACEVEDO-VILA\xffAE1, ANI\xffE1BAL g009T1(a former Resident Commissioner from Puerto Rico)\xff1A'''
        cleaned_line = process_escapes_in_line(data, 'G2', escape_sequences=fs)
        self.assertEquals(cleaned_line, b'''I01ACEVEDO-VILA, ANIBAL g009T1(a former Resident Commissioner from Puerto Rico)''')



    def test_convert_name (self):
        '''FAILING TEST DUE TO ACCENTED CHAR Check to see if we are converting properly the non ascii names of output files.: I01ACEVEDO-VILA\xffAE1, ANI\xffE1BAL g009T1(a former Resident Commissioner from Puerto Rico)\xff1A'''

        #I01ACEVEDO VILA\xffAE1 ANI\xffAE1BAL
        data = b'''I01ACEVEDO-VILA\xffAE1, ANI\xffE1BAL g009T1(a former Resident Commissioner from Puerto Rico)\xff1A
I03Remarks in House
I05Anderson, Michael and Kelly: Ryan Purcell Foundation Tim O'Neil Good Samaritan Award recipients, E1369 [28SE] I05Doctor, Don and Patty Jackson: Ryan Purcell Foundation Michael J. Diggins Community Service Award recipients, E1368 [28SE] '''

        title_mods="ACEVEDO-VILA, ANIBAL (a former Resident Commissioner from Puerto Rico)"
        data=b'I01ACEVEDO-VILA, ANIBAL (a former Resident Commissioner from Puerto Rico)'
        parser = LocatorParser(inputdata=data,
                               inputparser=CongressionalRecordIndexInputParser(year=2016),
                               outputparser=OutputParser())
        for output_tuple in parser.parse():
            name, output = output_tuple
            self.assertEqual(name,  b'CRI-2016-ACEVEDO-VILA-ANIBAL-8F120D7.htm')
            #./CRI-2016/CRI-2016-ACEVEDO-VILA-ANIBAL-8F12D7/mods.xml
            #TODO should be.... how do they get rid of accents in titles ?   is it in the file... CRI-2016-ACEVEDO-VILA-ANIBAL-8F12D7htm.


class TestCRITitleHashing(unittest.TestCase):
    def test_title_punctuation(self):
        '''Given a title "U.S. CHAMBER OF COMMERCE" and year 2016 return "CRI-2016-U-S-CHAMBER-OF-COMMERCE.htm"
        '''
        result = CongressionalRecordIndexInputParser.process_title(2016, b"U.S. CHAMBER OF COMMERCE")
        self.assertEquals(result,  b"CRI-2016-U-S-CHAMBER-OF-COMMERCE.htm")

    def test_title_short(self):
        '''Given a title "ADAMS, PAUL A"  return "ADAMS-PAUL-A"
        '''
        result = CongressionalRecordIndexInputParser.process_title(2014, b"ADAMS, PAUL A")
        self.assertEquals(result,  b"CRI-2014-ADAMS-PAUL-A.htm")

    def test_title_lowercase_to_upper(self):
        '''Given a title "adams, paul a"  return "ADAMS-PAUL-A"

        '''
        result = CongressionalRecordIndexInputParser.process_title(2014, b"adams, paul a")
        self.assertEquals(result,  b"CRI-2014-ADAMS-PAUL-A.htm")

    def test_title_lowercase_to_upper_real_example(self):
        """FAILING TEST due to conversion of accented char? : CRI-2016-MOVING-AHEAD-FOR-PROGRESS-IN-THE-21S-112D36htm."""
        #locator filename
        result = CongressionalRecordIndexInputParser.process_title(2014, b"MOVING AHEAD FOR PROGRESS IN THE 21st CENTURY ACT (MAP\xff0921)")
        #process filename from congressional_record_index.title
        result2 = CongressionalRecordIndexInputParser.process_title(2014, b'MOVING AHEAD FOR PROGRESS IN THE 21ST CENTURY ACT (MAP-21)')
        self.assertEquals(result,  result2)
        # still doesn't match what is in the mods/ on disk file
        self.assertEquals(result,  b"CRI-2014-MOVING-AHEAD-FOR-PROGRESS-IN-THE-21S-112D36.htm")


    def test_title_long(self):
        '''Given a title "ADVANCED NUCLEAR REACTOR RESEARCH, DEVELOPMENT, AND DEMONSTRATION ACT"
        return "ADVANCED-NUCLEAR-REACTOR-RESEARCH-DEVEL-27BA5A"
        where puctuation is removed and spaces convert to hypens
        and the first 6 chars of an md5 sum of the remaining title are appended
        MD5("OPMENT, AND DEMONSTRATION ACT") = 27BA5A6F....A8
        '''
        result = CongressionalRecordIndexInputParser.process_title( 2014, b"ADVANCED NUCLEAR REACTOR RESEARCH, DEVELOPMENT, AND DEMONSTRATION ACT")
        self.assertEquals(result, b"CRI-2014-ADVANCED-NUCLEAR-REACTOR-RESEARCH-DEVEL-27BA5A.htm")

    def test_title_puctuation(self):
        '''Given a title "ADDABBO, JOSEPH P.(a former Representative from New York)"
        MD5(" (a former Representative from New York)")= D09C5C....A4A
        returns "ADDABBO-JOSEPH-P-D09C5C"
        '''

        # from the gpo specs:
        text = b'ADDABBO, JOSEPH P. (a former Representative from New York)'
        #result = CongressionalRecordIndexInputParser.process_title( 1989, b"ADDABBO, JOSEPH P.(a former Representative from New York)")
        result = CongressionalRecordIndexInputParser.process_title( 1989, text)
        self.assertEquals(result, b"CRI-1989-ADDABBO-JOSEPH-P-D09C5C.htm")

        # but looking at the mods.xml file for 1989:
        text = b'ADDABBO, JOSEPH P. (a former Representative from New York)'
        result = CongressionalRecordIndexInputParser.process_title( 1989, text)
        self.assertEquals(result, b"CRI-1989-ADDABBO-JOSEPH-P-7D0A5.htm")


