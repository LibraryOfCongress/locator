import re, os, sys
import io
import argparse
from locator import (
    grouper,
    process_lines,
    output,
    remove_chars,
    REMOVE_CHARS,
    translate_chars, MAPPING)
import logging

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output", nargs='?')
                       # type=argparse.FileType('w'))
    args = parser.parse_args()
    #print (args.input)
    logger.debug("Parsing with args :%s", args)
    parser = LocatorParser()
    parser.parse_file(args.input, outputfile=args.output)


class InputParser(object):

    '''Read a locator fileIO object and parse it to an intermediate
    representation, which is then transformed by an outputparser
    '''
    LOCATOR_TABLE = {}
    FONT_TABLE = {}

    def parse(self, inputdata, **kwargs):
        '''Input parser's .parse() returns a list , but for the default case
        only one item comes back, so we [ item] and yield the item.
        this way our calling api is always
        for x in Inputpuarser.parse():
            do stuff (x)
        '''
        logger.debug("Entering InputParser.parse(%s", inputdata)
        #outputStream = io.BytesIO()
        outputStream = io.StringIO()
        io_output = self.parse_io(inputfile=inputdata, outputfile=outputStream)
        logger.debug("Leaving InputParser.parse(%s)->(%s)", inputdata, outputStream)
        for x in [ io_output ]:
            yield x

    def parse_file(self, infile, outputfile=None):
        '''given a daily digest locator file and
        an optional outputfilename convert the locator codes
        to a simple html format outputing to out or stdout
        '''
        if outputfile is None:
            outputfile = os.dup(sys.stdout.fileno())
        logger.debug("Outputfile:%s", outputfile)
        with open(infile, "rb") as inputfile:
            self.parse_io(inputfile, outputfile)

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
        if not locator_table:
            locator_table = self.LOCATOR_TABLE
        if not font_table :
            font_table = self.FONT_TABLE
        out = outputfile
        if outputfile is None:
            out = io.StringIO()

        input = inputfile.read()
        current_page = None
        output("<html>", outf=out)
        for page, page_match, line in self.makelines(input, output=out):
            current_state , output_line = process_lines(
                line,
                current_state,
                outputf=out,
                locator_table=locator_table,
                font_table=font_table,
                postfix=postfix)
            logger.debug("Current_state:%s", current_state)
            logger.debug("Page:%s Current_page:%s", page, current_page)

            if page:
                #output = re.sub(b'\x07',b'[BELL-]', line)
                if not current_page:
                    current_page = page
                if page != current_page:
                    # changed Page!
                    output(
                        b"<center>[Page:" +
                        current_page +
                        b"] </center>",
                        outf=out)
                    current_page = page
        if current_page:
            output(b"<center>[Page:" + current_page + b"] </center>", outf=out)
        output("</html>", outf=out)
        return out


    def find_page(self, data):
        '''I90.*\{(D\d+)\}
        '''
        page = None
        #m = re.match(b'.+?\x07I90.+?\{(D\d+)\}.+?', data)
        m = re.match(b'\x07I90.+?\{(D\d+)\}', data)
        if m:
            page = m.group(1)
        logger.debug("find_page->(%s)", page)
        return page, m

    def makelines(self, input, output=None):
        '''Take input locator string and yield line by line with page
        where line is a linefeed and lines are made up of related
        groups of data from GPO.

        Documentation ripped from gpoline.icn.

        '''

        logger.debug("makelines input:%s", input)
        BELL = '\x007'
        SHIFTOUT = '\x00E'

        c_chop_chars = [BELL, SHIFTOUT]
        # .2. bell+Z processing.  Delete all data following, including
        # the bell+Z up to and including the following "bell", or
        # char(7).  Note if there is not bell found, read another
        # block.  **There ought to be a following bell**.  If none
        # is found, announce an error, truncate s_line, and break.
        # Since at this point we are at EOF, we will exit the
        # enclosing while s_line ||:= loop, and write the remaining
        # s_line to output, as part of normal termination.
        input = re.sub(b'\x07Z.+?(\x07([a-zA-Z]\d+\s*)|$)', b'', input)
        #logger.debug("After BellZ:%s", input)

        #all = re.split(b'(\x07)', input)
        # logger.debug(all)

        # remove I32/I33->\x07
        # lookahead for ending Bell0I33/I32 or end of line and remove everything
        # for line , matched  in grouper(re.split(b'(\x07[A-FH-SU-Ya-fh-su-y]\d*)', input), 2):
        # for matched, line in grouped(re.split(b'(\x07[A-SU-Ya-su-y]\d*)', input)):
        # for bell_line in
        # grouped(re.split(b'(\x07[A-SU-Ya-su-y]\d*.+?)(?=\x07|$)', input)):
        all_text = re.split(b'(\x07)', input)
        #logger.debug("\tSplit:%s", all_text)
        for bell, line in grouper(all_text, 2, fillvalue=b''):
            # '\x007GKTPol1foo' -> '\x007GKTPol1', 'foo'
            # 1) The set of bell+ characters defined by c_current_keep_set
            #    signifies sequences which must remain on a given line.

            #logger.debug("bell :[%s]", bell)
            #logger.debug("line :[%s]", line)

            full_line = bell + line
            #logger.debug("\tFull_line:%s", full_line)

            page, m = self.find_page(full_line)
            # remove garbage? page indicators:now that we have the page
            #full_line = re.sub(b'\x07I90.+?\{(D\d+)\}.+?(\x07|$)',  b'', full_line)
            #logger.debug("\tAfter Removing Page stuff:%s", full_line)
            if page:
                full_line = b''
            full_line = clean_line(full_line)
            logger.debug("\tyield:%s %s %s", page, m, full_line)
            yield (page, m, full_line)

def clean_line(full_line):
    ''' clean and translate a line'''
    full_line = re.sub(
                b'\x07I3[23].+?(?=(\x07I3[23]|$))',
                b'',
                full_line)
    #logger.debug("\tAfter    Bell-I33/I32:%s", full_line)

    # remove SO->SI 14-15
    full_line = re.sub(b'\x0E.+?[\x0F|$]', b'', full_line)
    #logger.debug("\tAfter    SO/I:%s", full_line)

    full_line = remove_chars(
                full_line,
                REMOVE_CHARS)  # remove bad chars

    #logger.debug("\tAfter  Remove:%s", full_line)
    full_line = translate_chars(full_line, MAPPING)   # tab to space
    #logger.debug("\tAfter   Trans:%s", full_line)
    # remove stuff between \xa8 and \xad e.g.g: b'\xa8D382\xad'
    full_line = re.sub(b'\xa8.+?[\xad|$]', b'', full_line)
    #logger.debug("\tAfter xa8 nad xad:%s", full_line)
    return full_line




class OutputParser(object):

    '''parse the intermediate represenation of a locator file into some
    final output this implementation does nothing but return the passed
    in input.
    '''

    def parse(self, input, **kwargs):
        logger.debug("Output parser returning :%s" ,  input)
        return input

class MultipleOutputFilesOutputParser(object):
    '''parse the intermediate represenation of a locator file into some
    final output. This implemenation accepts a dictionary of
    input = { 'name': stream }
    it then will Write each stream into a file named  'name'
    CongressionalRecordIndexInputParser outputs in this manner.
    '''

    def __init__(self, basedir=None, prepend=None, **kwargs):
        self.basedir = basedir
        self.prepend = prepend

    def parse(self, input_tuple, **kwargs):
        '''process a tuple (filename, stream)
        Write each stream into a file named  'filename'
        '''
        basedir = kwargs.get('basedir')
        if not basedir and self.basedir:
            basedir = self.basedir
        if not basedir:
            basedir = ''

        filename_prepend = kwargs.get('prepend', '')
        if not filename_prepend and self.prepend:
            filename_prepend = self.prepend
        if not filename_prepend:
            filename_prepend = ''

        if basedir != '':
            basedir = basedir + "/"

        name, stream = input_tuple
        logger.debug("basedir:%s", basedir)
        logger.debug("prepend:%s", filename_prepend)
        logger.debug("name   :%s", name)
        fullfilename = basedir +  filename_prepend + name.decode('utf-8')
        # create any intermediate directories that are missing
        os.makedirs ( os.path.dirname(fullfilename), exist_ok=True)
        with open (fullfilename, "w") as output:
            output.write(stream.read())
        return input_tuple


class LocatorParser(object):

    '''Implement a base Locator parser that loads a locator file and based on
    1) input parser module (for a type of locator input file) (bill text, CRI,
    etc)
    2) input a parser ouptut module ( bill text html, CRI html, etc.)
    passed in sub modules parses different types of Locator files to specific
    output formats.

    parser = LocatorParser(inputdata=<inputFileIOorName>,
                inputparser=<parserInputClass()>,
                outputparser=<parserOutputClass()>)

    streamIOobj = parser.parse() if all params added above
    or if not:
    streamIOobj = parser.parse(input='/tmp/locator.rec',
                    inputparser=None,
                    outputparser=None)

    # note different output parser's can  do differnet things, i.e.
    # but by default they will all return a streamIO object that can be read.
    # and handled however you need.

    with open ( '/tmp/foo.html', 'wb' ) as  out:
        out.write(streamIOobj.read())

    '''

    def __init__(self, inputdata=None, inputparser=None, outputparser=None):
        self.input = inputdata
        self.inputparser = inputparser
        self.outputparser = outputparser

    def parse(self, inputdata=None, inputparser=None, outputparser=None, **kwargs):
        if inputdata:
            self.input = inputdata
        if inputparser:
            self.inputparser = inputparser
        if outputparser:
            self.outputparser = outputparser
        if not self.outputparser:
            self.outputparser = OutputParser()
        if not self.inputparser:
            raise Exception("Must set inputparser!")
        for inputs_output in self.inputparser.parse(self.input, **kwargs):
            outputs_output =  self.outputparser.parse(inputs_output, **kwargs)
            yield outputs_output

if __name__ == "__main__":
    main()
