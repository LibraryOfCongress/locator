import unittest
import logging
from locator.parser import InputParser
from locator import (
    process_lines,
    remove_chars,
    REMOVE_CHARS,
    MAPPING,
    translate_chars,
    find_page,
    find_locators,
    process_escapes_in_line
    )
logger = logging.getLogger()


class LocatorTest(unittest.TestCase):

    def test_firstline(self):
        data = b"\x07Z! EXT .000 ...DIGEST          PERSONAL COMPUTER\\J\\059060-A18AP9-000-*****-*****-Payroll No.:  -Name: et -Folios: 1-3 -Date: 04/18/2016 -Subformat:   \x07F0627 \x07I32April 18, 2016\x07I33April 18, 2016"
        good0 = b''
        good1 = b''
        cnt = 0
        parser = InputParser()
        for page, match, line in parser.makelines(data):
            if cnt == 0:
                self.assertEqual(line, good0)
            elif cnt == 1:
                self.assertEqual(line, good1)
            else:
                self.assertEqual(line, b"Should only be 2 lines!")

            cnt = cnt + 1

    def test_makeline(self):
        bell = u'\x007'
        so = '\x00E'
        slurped = b"\x07I08this is a first line\x07G1and more\x07I02and a second\x0Eremove these\x0F continues here\x07T1and font here"
        cnt = 0
        parser = InputParser()
        for page, page_match, line in parser.makelines(slurped):
            if cnt == 0:
                self.assertEqual(b'\x07I08this is a first line', line)
            elif cnt == 1:
                self.assertEqual(b'\x07G1and more', line)
            elif cnt == 2:
                self.assertEqual(b'\x07I02and a second continues here', line)
            elif cnt == 3:
                self.assertEqual(b'\x07T1and font here', line)
            else:
                self.assertEqual("Shouldn't reach here", line)
            cnt = cnt + 1

    def test_remove_bellz(self):
        data = b'foo bar Boo bar\x07ZRemove all of me\x07e43but not me'
        parser = InputParser()
        page, page_match, line = parser.makelines(data).__next__()
        good = b'foo bar Boo barbut not me'
        self.assertEqual(line, good)

    def test_bellz_endofline(self):
        data = b'foo bar Boo bar\x07Z!Remove all of me'
        good = b'foo bar Boo bar'
        parser = InputParser()
        page, page_match, line = parser.makelines(data).__next__()
        self.assertEqual(line, good)

    def test_remove_chars(self):
        # Create a string of all the chars we want to remvoe
        all_bad = b'\x000\x00A\x00D\x01B\x01C\x07F123'
        # Remove all the bad chars from our string
        cleaned = remove_chars(all_bad, REMOVE_CHARS)
        # should be empty string as all chars were bad
        self.assertEqual(cleaned, b'')

    def test_translate_chars(self):
        doc = b''
        good = b''
        for k, v in MAPPING.items():
            doc = doc + k
            good = good + v
        #print (doc)
        self.assertNotEqual(doc, b'')
        cleaned = translate_chars(doc, MAPPING)
        self.assertEqual(cleaned, good)

    def test_find_page_no(self):
        #data = b'1 \x07I90[D18AP6-1]{D382}Senate\x07I05Senate\x07I90[D18AP6-2]{D382}Chamber Ac\x07I50Chamber Action\x07I90[D18AP6-3]{D382}Routine Pr\x07I40'
        #page, m = find_page(data)
        #self.assertEqual(b'D382', page)
        full_line = b'\x07I90[D18AP6-1]{D382}Senate'
        page, m = find_page(full_line)
        self.assertEqual(b'D382', page)

    def test_find_locators(self):
        data = b'1 \x07I90[D18AP6-1]{D382}Senate\x07I05Senate\x07I90[D18AP6-2]{D382}Chamber Ac\x07I50Chamber Action\x07I90[D18AP6-3]{D382}Routine Pr\x07I40'
        for cnt, locator in enumerate(find_locators(data)):
            if cnt == 0:
                self.assertEqual(b'I90', locator.group('locator'))
            elif cnt == 1:
                self.assertEqual(b'I05', locator.group('locator'))
            elif cnt == 2:
                self.assertEqual(b'I90', locator.group('locator'))
            elif cnt == 3:
                self.assertEqual(b'I50', locator.group('locator'))
            elif cnt == 4:
                self.assertEqual(b'I90', locator.group('locator'))
            elif cnt == 5:
                self.assertEqual(b'I40', locator.group('locator'))
            else:
                logger.error("%s == %s", cnt, locator.group('locator'))
                self.assertEqual(
                    b' Shouldnt reach here',
                    locator.group('locator'))

    def test_dailydigest_I01_actions(self):
        from locator.dailydigest import DailyDigestInputParser

        data = b'\x07I01Monday, April 18, 2016\xadD382'
        current_state, _ = process_lines(
            data, (None, b'G2'),
            locator_table=DailyDigestInputParser.LOCATOR_TABLE,
            font_table=DailyDigestInputParser.FONT_TABLE)
        self.assertEqual(
            current_state[0].get('end'),  '</em></h3>')
        self.assertEqual(
            current_state[0].get('grid'), b'G2')
        self.assertEqual(
            current_state[0].get('start'), '<h3><em>')
        # TODO mock out output() function and verify that \xadD382 was not
        # output.

    def test_remove_page(self):
        data = b'\x07I90[D18AP6-2]{D382}Chamber Ac'
        parser = InputParser()
        page, page_match, line = parser.makelines(data).__next__()
        self.assertEqual(page, b'D382')
        self.assertEqual(line, b'')

    def test_remove_page_data(self):
        data = b'\x07I90[D18AP6-70]{D387}On Tuesday'
        parser = InputParser()
        page, page_match, line = parser.makelines(data).__next__()
        self.assertEqual(page, b'D387')
        self.assertEqual(line, b'')

    def test_bellcode_byitself(self):
        '''Normally a bell code has text after wards and our grouper will group it,
        but if it doesn't have data we still need to group it properly  with a None  line
        '''
        input = b'Z! EXT .000 ...DIGEST          PERSONAL COMPUTER\J\059060-A18AP9-000-*****-*****-Payroll No.:  -Name: et -Folios: 1-3 -Date: 04/18/2016 -Subformat:   \x07F0627'
        input = input + \
            b'\x07G009\x07I52Senate Chamber\x07I90[D18AP6-70]{D387}On Tuesday'
        parser = InputParser()
        page, m, full_line = parser.makelines(input).__next__()
        self.assertEqual(full_line, b'\x07G009')

    def test_escape_chars(self):
        '''escape chars start with \w{1}\xff\w{2,3}
        the code \w{2,3} tells us what to do with the preceding char.
        i.e accents over chars.
        '''
        input = b'\x07I04See Interim Re\xffAE1sume\xffAE1 of Congressional Activity.'

        temp1 = b'\x07I04See Interim R&#233;sum&#233; of Congressional Activity.'
        line = process_escapes_in_line(input, 'G1')
        self.assertEqual(line, temp1)

    def test_esc_star(self):
        input = b'*\xff1AThese figures include all measures reported, even if there was no accompanying report. A total of 199 written reports have been filed in the Senate, 385 reports have been filed in the House.'
        temp1 = b'*&#160;These figures include all measures reported, even if there was no accompanying report. A total of 199 written reports have been filed in the Senate, 385 reports have been filed in the House.'
        line = process_escapes_in_line(input, 'G1')
        self.assertEqual(line, temp1)

    def test_dailydigest_I67(self):
        from locator.dailydigest import DailyDigestInputParser
        data = b'\x07I67H'
        current_state, _ = process_lines(
            data, (None, b'G2'),
            locator_table=DailyDigestInputParser.LOCATOR_TABLE,
            font_table=DailyDigestInputParser.FONT_TABLE)
        self.assertEqual(
            current_state[0],
            {'end': '</span>', 'grid': b'', 'start':
             "<span class='bell-I67H dailydigest-extension'>"})

        import io
        out_io = io.StringIO()

        current_state = (None, b'G2')  # start as Grid 2
        parser = InputParser()
        for page, page_match, line in parser.makelines(data, output=out_io):
            current_state, _ = process_lines(
                line, current_state, outputf=out_io,
                locator_table=DailyDigestInputParser.LOCATOR_TABLE,
                font_table=DailyDigestInputParser.FONT_TABLE)
            contents = out_io.getvalue()
            self.assertEqual(
                contents,
                "<span class='bell-I67H dailydigest-extension'>\n")
