import io
import copy
import hashlib
import re
from locator.parser import (InputParser, output, clean_line, translate_chars, MAPPING)
from locator import ESCAPE_SEQUENCES as input_ESCAPE_SEQUENCES
from locator import grouper, remove_chars, REMOVE_CHARS, process_escapes_in_line, process_lines, find_locators
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
            b"g001": {'start': "",              'end': "",            'grid': b"G2", },
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
    ESCAPE_SEQUENCES = input_ESCAPE_SEQUENCES
    # FOR CRI output filenames we don't process escape sequences, we blank them out
    def __init__(self,**kwargs ):
        self.year = kwargs.get('year')
        super( CongressionalRecordIndexInputParser, self)


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
                postfix=None, year=self.year):

            yield parsed_stanza

    def find_page(self, data):
        '''For CongressionalRecordIndex we will want to split the giant file
        up into tiny files based on page, a page is started with
        ^GI01<Title Text>
        '''
        page = None
        m = re.match(b'\x07I01(\w+)', data)
        if m:
            page = m.group(1)
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
            postfix=None, year=None):
        ''' output by default is a StringIO object, you will probably want to
        output = parse_io(...)
        output.seek(0)
        to rewind to the begining.  Alternatively you can pass in a file handle.
        '''

        if self.year and not year:
            year = self.year
        orig_current_state = current_state
        outputs = {}
        inputdata = inputfile.read()
        name = ""
        for stanza in self.make_stanzas(inputdata):
            logger.debug("CRI stanza:%s", stanza)
            out = io.StringIO()
            # For every sub document in the dat file reset the state to the
            # start
            current_state = orig_current_state
            current_state_stack = []
            cnt = 0
            for page, page_match, line in self.makelines(stanza, output=out):
                ret_current_state_stack, output_line = process_lines(
                    line,
                    current_state,
                    outputf=out,
                    locator_table=locator_table,
                    font_table=font_table,
                    postfix=postfix)
                current_state = ret_current_state_stack[-1]
                logger.debug("Current state:%s", current_state)
                logger.debug("Previous state :%s", ret_current_state_stack[0])
                logger.debug("[%d] line:[%s] states[%s]", cnt, line, ret_current_state_stack)
                current_state_stack.append( ( ret_current_state_stack, line))
                cnt=cnt+1

            # check all non first items in stack if they exist and have a bellcode
            for state, line  in current_state_stack :
                # first item in every state is the previous state, so skip it
                if state[1]:
                    for action, grid in state[1:]:
                        if action and action.get('bellcode') == b'I01':
                            name ,cleaned_line= self.process_stanza_title(line,year)
                            line_name = cleaned_line

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

            yield ((name, line_name) , out )

    def process_stanza_title(self, line, year):
        """given a line with I01 get the name for the output file"""
        # new stanza title, should only be one per stanza remove
        # bellcode.
        cleaned_line =  clean_line (re.sub( b'\x07I01',b'', line))
        cleaned_line = cleaned_line.strip()
        # remove fonts "T"
        output_cleaned_line = b""
        last_end = 0
        for locator in find_locators(cleaned_line):
            if locator.group('locator').startswith(b'T') or locator.group('locator').startswith(b'g'):
                output_cleaned_line = output_cleaned_line + cleaned_line[last_end:locator.start()]
                last_end = locator.end()
        if last_end:
            output_cleaned_line = output_cleaned_line + cleaned_line[last_end:]
        if output_cleaned_line:
            cleaned_line = output_cleaned_line

        '''For names (i.e output filenames we don't process accents
        so we pass in the FakeEscapeSequences() class  that always
        returns b'' for any matching escape sequnces
        '''
        fs = FakeEscapeSequences()
        cleaned_line =  process_escapes_in_line(cleaned_line, 'G2',
                            escape_sequences=fs)
        name = CongressionalRecordIndexInputParser.process_title(year, cleaned_line)
        return name, cleaned_line



    @staticmethod
    def process_title(year, title):
        '''Attempt to create the gpo title from the full gpo title (accessid)
        Here are instructions from GPO for improving the file matching. See also attachment.
        on CDG-7130

        The “accessId” becomes the file name.
        Special characters should already converted...

        GCS/accessId
        The access identifier is based on the title of the granule, i.e.
        {GM/title}

        It is constructed using the following template:
        CRI-
        {YYYY}-{title-prefix}-{MD5-title-suffix}
        Where

        1. {YYYY}
        is the year of
        {PM/dateIssued}

        2.
        {title-prefix} is the shortest string from the following options:
        a) All characters up to (and not including) the first left parenthesis
        b) The first forty characters of the title.

        3. {title-suffix} is all characters of the title not included in {title-prefix}

        4.
        {MD5-title-suffix} is a HEX representation of the first 24 bits (first 6 characters) of an MD5 digital signature of the characters in {title-suffix}.

        5. "-{MD5-title-suffix}

        " is omitted when the granule title is equal or less than forty characters.
        6. Replace all single white spaces with a dash character "-".

        7. Remove characters such as commas, periods, etc.

        Unfortunately it doesn't really work as they aren't using the exact same
        source title from the locator code that we generate.
        '''
        mymap = copy.deepcopy(MAPPING)
        mymap[b'\xff09'] = b'-'
        mymap[b'&ndash'] = b'-'
        title = title.upper()

        title = translate_chars(title, mymap)   # tab to space
        title_prefix = title[:40]
        title_suffix = None
        if len(title) > 40:
            title_suffix = title[40:]

        paren = title_prefix.find(b"(")
        if paren and paren >= 0:
            title_prefix = title_prefix[0:paren]
            title_suffix = title[paren:]

        #convert prefix to uppercase
        title_prefix = title_prefix.decode('utf-8').upper()
        title_prefix = title_prefix.encode('utf-8')
        # convert period to hypen
        title_prefix = re.sub(b'[\.]', b'-', title_prefix )
        #remove all punctuation
        title_prefix = re.sub(b'[^0-9a-zA-Z\-\s]+', b'', title_prefix )
        # remove trailing spaces:
        title_prefix = re.sub(b'\s+$', b'', title_prefix)
        #convert space to hyphen
        title_prefix = re.sub(b'[\s]+', b'-', title_prefix )
        md5_title_suffix = None
        if title_suffix:
            md5 = hashlib.md5()
            if isinstance(title_suffix, bytes):
                md5.update(title_suffix)
            else:
                md5.update(title_suffix.encode('utf-8'))

            # get the first 6 of the lowercase hex representation as bytes
            md5_title_suffix = md5.hexdigest()[:6].upper()
            md5_title_suffix = md5_title_suffix.encode('utf-8')
            output = b"CRI-%d-%b-%b.htm" % (year,  title_prefix, md5_title_suffix)
        else:
            output = b"CRI-%d-%b.htm" % (year,  title_prefix)

        # remove duplicate hyphens with one hypen
        output = re.sub(b'\-+', b'-', output )

        return output

    def article_name(self, name):
        '''clean up article title into a common name output,
        A.B. WON PAT GUAM INTERNATIONAL AIRPORT AUTHORITY\n
        '''
        return name
        #TODO remove function.  replaced  by process_title
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
        logger.debug("Input:%s", input)
        all_text = re.split(b'(\x07I|\x07F\d+)', input)
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

        would yield these 2 elements of stanzas = [
        '\x07I01Title\n\x07I02 foo\n\x07I03bar',
        '\x07I01Second title\n\x07I02 foo\n\x07I03bar' ]
        '''
        # remove starting \x07F\d+
        input = re.sub(b'\x07F\d+', b'', input)
        full_line = remove_chars(input.strip(), REMOVE_CHARS)
        # split into stanzas and remove empty lines
        stanzas = [
            x.strip()
            for x in re.split
            (b'(\x07I01)', full_line) if x.strip() != b'']

        for bell, line in grouper(stanzas, 2, fillvalue=b''):
            yield bell + line

import collections


class FakeEscapeSequences(collections.abc.MutableMapping):
    """Change the normal escape sequences for accents to always
    return an empty action for titles to not process accented chars.
    """

    def __init__(self, *args, **kwargs):
        self.store = {}
        empty_action =    { 'desc':'no accented chars allowed in titles', 'html':b'' }
        for k, action in CongressionalRecordIndexInputParser.ESCAPE_SEQUENCES.items():
            self.store[k] = empty_action
            #if action.get('desc'):
            #    self.store[k] = empty_action
            #else:
            #    new_dict = {}
            #    for k1, v1 in action.items():
            #        new_dict[k1] = empty_action
            #    self.store[k] = new_dict
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        logger.debug("fake:%s", pp.pformat(self.store))

        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        action = self.store[key]
        return action
        #return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        dictrepr = dict.__repr__(self.store)
        return '%s(%s)' % (type(self).__name__, dictrepr)


class FakeEscapeSequencesxxx(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def __getitem__(self, key):
        ''' If name is in ESCAPE_SEQUENCE  return empty action
        '''
        action = CongressionalRecordIndexInputParser.ESCAPE_SEQUENCES.get(key)
        if action:
            logger.debug("Searching for %s", key)
            return { 'desc':'no accented chars allowed in titles', 'html':b'' }
        return action

