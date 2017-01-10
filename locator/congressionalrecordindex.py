import io
import re
from locator.parser import (InputParser, output, process_lines, clean_line)
from locator import grouper, remove_chars, REMOVE_CHARS, process_escapes_in_line
import logging
logger = logging.getLogger(__name__)


class CongressionalRecordIndexInputParser(InputParser):

    ''' A locator code has a start and end conversion (html) and a grid code.
    The Grid code controls which  Font  locator code conversion to use.
    so if the active locator code has a grid G2 we use the font code for grid G2.
    The default grid is G2.
    'start-preprocess' will be run against the input line  prior to any processing.
    ( in process_actions() )
    '''
    LOCATOR_TABLE = {
        b"I01": {
            # skip all of I01 line, return None
            'start-preprocess': lambda x: None,
            'bellcode': b"I01",
            'start': "",
            'end': "",
            'grid': b"G2",
        },
        b"I02": {
            'bellcode': b"I02",
            'start': "<h2>",
            'end': "</h2>",
            'grid': b"G2",
            },
        b"I03": {
            'bellcode': b"I03",
            'start': "<h2>",
            'end': "</h2>",
            'grid': b"G2",
            },
        b"I05": {
            'bellcode': b"I05",
            'start': "<p>",
            'end': "</p>",
            'grid': b"G2",
            },
        }

    FONT_TABLE = {
        b'G1': {
            b"T1": {'start': "",                'end': "",                      'grid': b"G1", },
            b"T2": {'start': "<center><strong>", 'end': "</strong></center>",    'grid': b"G1", },
            b"T3": {'start': "<em>",            'end': "</em>",                 'grid': b"G1", },
            b"T4": {'start': "",                'end': "",                      'grid': b"G1", },
            },
        b'G2': {
            b"T1": {'start': "<strong>",        'end': "</strong>",             'grid': b"G2", },
            b"T2": {'start': "<strong><em>",    'end': "</em></strong>",        'grid': b"G2", },
            b"T3": {'start': "<em>",            'end': "</em>",                 'grid': b"G2", },
            b"T4": {'start': "<h5><em>",        'end': "</em></h5>",            'grid': b"G2", },
            },
        b'G3': {
            b"T1": {'start': "",                'end': "",                      'grid': b"G3", },
            b"T2": {'start': "<strong>",        'end': "</strong>",             'grid': b"G3", },
            b"T3": {'start': "<strong>",        'end': "</strong>",             'grid': b"G3", },
            b"T4": {'start': "",                'end': "",                      'grid': b"G3", },
            },
        b'G4': {
            b"T1": {'start': "",                'end': "",                      'grid': b"G4", },
            b"T2": {'start': "<strong>",        'end': "</strong>",             'grid': b"G4", },
            b"T3": {'start': "<em>",            'end': "</em>",                 'grid': b"G4", },
            b"T4": {'start': "<strong>",        'end': "</strong>",             'grid': b"G4"},
            }
    }

    def parse(self, inputdata, **kwargs):
        '''input is a bytes io object '''
        bytes_input = io.BytesIO(inputdata)
        for parsed_stanza in self.parse_io(
                inputfile=bytes_input,
                current_state=(
                    None,
                    b'G2'),
                locator_table=CongressionalRecordIndexInputParser.LOCATOR_TABLE,
                font_table=CongressionalRecordIndexInputParser.FONT_TABLE,
                postfix=None):

            yield parsed_stanza

    def find_page(self, data):
        '''For CongressionalRecordIndex we will want to split the giant file
        up into tiny files based on page, a page is started with
        ^GI01<Title Text>
        '''
        page = None
        m = re.match(b'\x07I01', data)
        return page, m

    def parse_io(
            self,
            inputfile=None,
            current_state=(
                None,
                b'G2'),
            outputfile=None,
            locator_table=None,
            font_table=None,
            postfix=None):
        ''' output by default is a StringIO object, you will probably want to
        output = parse_io(...)
        output.seek(0)
        to rewind to the begining.  Alternatively you can pass in a file handle.
        '''
        orig_current_state = current_state
        outputs = {}
        inputdata = inputfile.read()
        name = ""
        for stanza in self.make_stanzas(inputdata):
            out = io.StringIO()
            # For every sub document in the dat file reset the state to the
            # start
            current_state = orig_current_state
            for page, page_match, line in self.makelines(stanza, output=out):
                logger.debug(
                    "Page:%s, page_match:%s line:%s",
                    page,
                    page_match,
                    line)
                logger.debug("\tcurrent_state:%s", current_state)
                current_state, output_line = process_lines(
                    line,
                    current_state,
                    outputf=out,
                    locator_table=locator_table,
                    font_table=font_table,
                    postfix=postfix)
                logger.debug("Current_state:%s", current_state)
                if current_state[0].get('bellcode') == b'I01':
                    # new stanza title, should only be one per stanza remove
                    # bellcode.
                    cleaned_line =  clean_line (re.sub( b'\x07I01',b'', line))
                    cleaned_line =  process_escapes_in_line(cleaned_line, 'G2')
                    name = self.article_name(cleaned_line)
            if current_state[0] and current_state[0].get('end'):
                logger.debug(
                    "\tcurrent_state.end:%s",
                    current_state[0].get('end'))
                output(current_state[0].get('end'), outf=out)
            # rewind to the begining now that we are finshed with output.
            out.seek(0)
            # if there is no name then we don't bother with the section
            if name:
                outputs[name] = out

            yield (name, out)

    def article_name(self, name):
        '''clean up article title into a common name output,
        A.B. WON PAT GUAM INTERNATIONAL AIRPORT AUTHORITY\n
        '''
        if name:
            name = name.replace(b'\n', b'')
            name_temp = name.replace(b'.', b'')
            name_temp = name_temp.replace(b',', b'-')
            name_temp = name_temp.replace(b' ', b'-') + b'.htm'
            name = name_temp.replace(b'--', b'-')
        return name

    def makelines(self, input, output=None):
        '''Take input locator string and yield line by line
        where line is a linefeed and lines are made up of related
        groups of data from GPO.

        cri starts with \x07F<number>
        some have new lines every bell code, others do not
        '''

        input = input.strip()  # remove leading spaces
        logger.debug("makelines input:%s", input)
        all_text = re.split(b'(\x07)', input)
        logger.debug("\tSplit:%s", all_text)
        for bell, line in grouper(all_text, 2, fillvalue=b''):
            # '\x007GKTPol1foo' -> '\x007GKTPol1', 'foo'
            # 1) The set of bell+ characters defined by c_current_keep_set
            #    signifies sequences which must remain on a given line.

            logger.debug("bell :[%s]", bell)
            logger.debug("line :[%s]", line)
            full_line = bell + line
            full_line = remove_chars(full_line, REMOVE_CHARS)
            page, m = self.find_page(full_line)
            logger.debug("\tFull_line:%s", full_line)
            logger.debug("\tyield:%s %s %s", page, m, full_line)
            yield (page, m, full_line)

    def make_stanzas(self, input):
        ''' A stanza is a group of lines separated by \x07I01
        return the lines including the starting \x07I01
        \x07F89378
        \x07I01Title
        \x07I02 foo
        \x07I03bar

        \x07I01Second title
        \x07I02 foo
        \x07I03bar

        would yield these 3 elements of stanzas = [
        '\x07F89378',
        '\x07I01Title\n\x07I02 foo\n\x07I03bar',
        '\x07I01Second title\n\x07I02 foo\n\x07I03bar' ]
        '''
        full_line = remove_chars(input.strip(), REMOVE_CHARS)
        # split into stanzas and remove empty lines
        stanzas = [
            x
            for x in re.split
            (b'(\x07I01)', full_line) if x.strip() != b'']

        for bell, line in grouper(stanzas, 2, fillvalue=b''):
            yield bell + line
