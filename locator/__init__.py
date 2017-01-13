# -*- coding: utf-8 -*-
# remimplement gpoline.icn and digest.cin python.
# This will implement basic functionality of converting gpo locator codes
# to html matching thomas/lis .
#

import re
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


from itertools import zip_longest
# Globals used in this module.
#             char(0)  char(10) char(13)
#             char(27) char(28) char(127)
REMOVE_CHARS = [b'\x000', b'\x00A', b'\x00D',
                b'\x01B', b'\x01C', b'\xac',
                b'\x07F\d+', #seems to appear at the head of a page/section
                b'\x07S\d+', # subformat codes?
                #b'\xad',
                #b'\xa8'
]
# translate mapping tab to space
MAPPING = {b'\x009': b' ',  # tab to space
           b'\xff09':b'&ndash;' , # b'\xff09': u'\u2013',
           b'\x19':  b' ' , # hex 19 End of Medium?  change to space  i.e. Page\x19S2128 -> Page S2128
           b'\x5f': b'--' , # replace underbar with double hyphen??? TODO: check
           b'\x18': b'<br />' , # \x18 CANCEL-> <br/> ?
           b'\x1a': b'<br />' , # \x1a Substitute -> <br/> ?
           #b'\xff': b'&yuml;' , #  y with .. over it.
}


def grouper(iterable, n, fillvalue=None):
    '''Collect data into fixed-length chunks or blocks,
     Modified recipe from  http://docs.python.org/3/library/itertools.html#recipes
     grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    '''
    args = [ filter( lambda x: x!=b'' , iter(iterable)) ] * n
    #args = [  iter(iterable) ] * n
    return zip_longest(*args, fillvalue=fillvalue)



def remove_chars(line, remove_chars, to_string=b''):
    '''Remove a list of chars from a line
    replacing with empty string by default or passed in variable
    .'''
    if len(line) < 100:
        logger.debug(
        "\tRemoving:%s from %s  with [%s]",
        remove_chars,
        line,
        to_string)
    else:
        logger.debug(
        "\tRemoving:%s from input_line(>100 elements) with [%s]",
        remove_chars,
        to_string)

    for character in (remove_chars):
        line = re.sub(character  , to_string, line)
    return line


def translate_chars(line, mapping):
    '''Given a mapping dictionary, replace all keys found in the line
    with the matching values.
    '''
    for k, v in mapping.items():
        line = remove_chars(line, [k], v)
    return line


def find_page(data):
    '''I90.*\{(D\d+)\}
    '''
    page = None
    #m = re.match(b'.+?\x07I90.+?\{(D\d+)\}.+?', data)
    m = re.match(b'\x07I90.+?\{(D\d+)\}', data)
    if m:
        page = m.group(1)
    logger.debug("find_page->(%s)", page)
    return page, m

def find_locators(line):
    '''given a line return a regex match for locator codes in the line.
    match.start gives position start,  match.end gives position end
    match.group('locator') gives the locator code without the Bell
    '''
    code = None
    m = re.finditer(b'\x07(?P<locator>I67H|I66F|T\d?|[a-su-zA-SU-Z]\d{0,2})', line)
    if m:
        code = m
    return code

def find_escape(line, current_grid=b'G1'):
    ''' Escape sequences usually replace a preceding char, like an accented
    e in resume or in foreign accented chars.
    '''
    logger.debug("esc: line:%s", line)
    code = None
    #m = re.finditer(b'(?P<replace>\w)?\xff(?P<esc>\w{2,3})', line)
    m = re.finditer(b'(?P<replace>.?)\xff(?P<esc>AE\d|AF\d|0\d|\dA)', line)
    if m:
        code = m
    logger.debug("Found :%s", code)
    return code

def translate_locator(locator, grid=b'G2',
                      locator_table=None,
                      font_table=None):
    ''' A locator code has a start and end  conversion (html) and a grid code.
    The Grid code controls which  Font  locator code conversion to use.
    so if the active locator code has a grid G2 we use the font code for grid G2.
    The default grid is G2.
    '''
    converted_code = locator_table.get(locator)
    if not converted_code:
        #check if a font, using passed in grid:
        font_grid = font_table.get(grid)
        if font_grid:
            converted_code= font_grid.get(locator)
    if converted_code:
        return converted_code
    else:
        return {'start':'', 'end':'', 'grid':grid }


import sys
def output(input_line, prefix=None, postfix=None, outf=sys.stdout):
    ''' Print output to filehandle outf or sys.stdout if no filehandle
    passed in.  Attempt to convert bytes from latin1 to utf-8.
    prefix is printed prior to input_line, postfix is print after input_line.
    '''
    if not postfix:
        postfix = ''
    _output(input_line, prefix, postfix, outf)

def _output(input_line, prefix=None, postfix=None, outf=sys.stdout):
    logger.debug("[%s] %s [%s]", prefix, input_line, postfix)
    if isinstance(input_line, bytes):
        line = input_line.decode('latin1').encode('utf-8')
    else:
        line  = input_line
    if line and line != b'':
        if prefix:
            logger.debug("%s", prefix)
            if isinstance(prefix, bytes) :
                outf.write (prefix.decode("utf-8"))
            else:
                outf.write (line)
        logger.debug("%s", line)
        if isinstance(line, bytes) :
            outf.write (line.decode("utf-8"))
        else:
            outf.write (line)
        if postfix:
            logger.debug("%s", postfix)
            if isinstance(postfix, bytes) :
                outf.write (postfix.decode("utf-8"))
            else:
                outf.write (postfix)

ESCAPE_SEQUENCES = {#esc    # action
                    b'1A' : { 'desc' :'Thin space' , 'html':b'&#160;' },
                    b'09' : { 'desc' :'N dash' ,     'html':b'&#150;' },   #TODO: check
                    # 08  not clear what to do  All Mark
                    b'AF' : { 'desc' :'copywright' , 'html':b'&#169;' },
                    b'0A' : { 'desc' :'Multiplication', 'html':b'&#215;' },
                    # esc   # replace # action
                    b'AE0': { 'S':  {'desc' :'breve' ,      'html':b'&#169;' },
                             's':  {'desc' :'breve' ,      'html':b'&#154;' },
                           },

                    b'AE1':{ b'A':  {'desc' :'acute' ,      'html':b'&#193;' },
                             b'E':  {'desc' :'acute' ,      'html':b'&#201;' },
                             b'I':  {'desc' :'acute' ,      'html':b'&#205;' },
                             b'O':  {'desc' :'acute' ,      'html':b'&#211;' },
                             b'U':  {'desc' :'acute' ,      'html':b'&#218;' },
                             b'Y':  {'desc' :'acute' ,      'html':b'&#221;' },

                             b'c':  {'desc' :'acute' ,      'html':b'c&#180;' }, #TODO check
                             b's':  {'desc' :'acute' ,      'html':b's&#180;' }, #TODO check

                             b'a':  {'desc' :'acute' ,      'html':b'&#223;' },
                             b'e':  {'desc' :'acute' ,      'html':b'&#233;' },
                             b'i':  {'desc' :'acute' ,      'html':b'&#237;' },
                             b'o':  {'desc' :'acute' ,      'html':b'&#243;' },
                             b'u':  {'desc' :'acute' ,      'html':b'&#250;' },
                             b'y':  {'desc' :'acute' ,      'html':b'&#253;' },
                   }
    }
def process_escapes(found, orig_line, current_start, current_line, current_grid , escape_sequences=ESCAPE_SEQUENCES):
    ''' if current_grid > 4 then do something else
    do our conversions see documentation..found on cornell law site
    <replace char>\xff<esc>
        escape_sequences.get(esc).get(<replace_char>).get('html')
    or
    \xff<esc>
        escape_sequences.get(esc).get('html')
    '''
    logger.debug("process esc:%s", current_line)
    output = current_line
    if int(current_grid[1:]) <= 4:
        replace = found.group('replace')
        esc = found.group('esc')
        if esc:
            '''2 types of esc sequences:
            One where we match first the
            esc char and then the replace char to get the action part of the
            dictionary.
            Two: just match the esc char and then we get the action part of the
            dictionary.
            '''
            temp = escape_sequences.get(esc, {'desc': 'default', 'html': b'' } )
            # if the temp action has a dictionary matching the replace char,
            # make that dictionary the action
            action = temp.get(replace)
            keep_replacement = False
            if not action:
                # otherwise the action is the dictionary returned by the escape
                # sequence above (or the default, and empty space) and we keep
                # the replace char if existing in the output.
                action = temp
                keep_replacement= True

            logger.debug("process esc: esc:%s, replace:%s action:%s", esc, replace, action)
            replace_with_html = b''
            replace_with_html = action.get('html')
            if keep_replacement:
                output = none2empty(orig_line[current_start:found.start()]) + none2empty(replace) + none2empty(replace_with_html)
            else:
                output = orig_line[current_start:found.start()] + replace_with_html
            if action.get('desc') == 'default':
                logger.warn("No translation from %s, defaulting to empty space..", esc)
            current_start = found.end()

    logger.debug("output:%s", output)
    return output, current_start

def none2empty(input):
    if input:
        return input
    return b''

def process_escapes_in_line(line, current_grid):
    current_start = 0
    current_line = b''
    for afound in find_escape(line, current_grid):
        logger.debug("line:%s", line)
        a_current_line , current_start = process_escapes(afound, line, current_start, current_line,  current_grid )
        current_line = current_line + a_current_line
        logger.debug("after esc :%s", current_line)
    if current_start > 0:
        current_line = current_line + line[current_start:]
        line = current_line
    return line

def process_lines(line, current_state, outputf=sys.stdout,
                      locator_table=None,
                      font_table=None, postfix="<br />"):
    '''For every line process it for locator codes,
    Set the current_state to the action's grid,value  unless it is a
    Font locator (T\d+).  We use the grid code of the current locator action
    to determine which Font action to use.

    action = { 'start': "<h3><em>",'end': "</em></h3>",'grid':"G2",},
    current_state = tuple( action,b'G2')
    There should only be one locator per line at the begining.
    '''
    line_start = 0
    current_grid = current_state[1]
    for found in find_locators(line):
        logger.debug("Found locator:%s", found.group('locator'))

        action = translate_locator(found.group('locator'), grid=current_grid,
                                   locator_table=locator_table, font_table=font_table)
        if action:
            logger.debug("Found Action:%s" , action)
            current_action = current_state[0]
            line, line_start = process_actions(found, line, line_start, current_action, action, outputf=outputf)
            # Not a font locator code:
            if found.group('locator')[0] != 'T':
                # set the current grid equal to the locator codes grid code.
                current_grid = action.get('grid')
            current_state = ( action, current_grid )
    if line:
        line = process_escapes_in_line(line, current_grid)
        output_line = line[line_start:]
        output (output_line, postfix=postfix,outf=outputf)
    else:
        output_line = None
    return current_state, output_line

def process_actions(found, line, line_start, current_state, actions, outputf=None):
    ''' Process a given locator code according to the actions object
    an action is the current locator state  from FONT_TABLE or LOCATOR_TABLE
    '''
    locator = found.group('locator')
    if actions.get('start-preprocess'):
        line = actions.get('start-preprocess')(line)
        if not line:
            line_start = None

    if line:
        pattern_start = found.start()
        pattern_end = found.end()
        output( line[line_start:pattern_start],outf=outputf)
        line_start = pattern_end
        if current_state and current_state.get('end'):
            logger.debug("\tcurrent_state.end:%s" , current_state.get('end'))
            output (current_state.get('end'),outf=outputf)
        logger.debug("\tlocator:%s action start:%s", locator, actions.get('start'))
        output ( actions.get('start'),outf=outputf)
        output (line[line_start:pattern_start],outf=outputf)
    return line, line_start


