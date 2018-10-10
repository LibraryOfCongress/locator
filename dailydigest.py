import re
from locator.parser import InputParser


class DailyDigestInputParser(InputParser):

    ''' A locator code has a start and end conversion (html) and a grid code.
    The Grid code controls which  Font  locator code conversion to use.
    so if the active locator code has a grid G2 we use the font code for grid G2.
    The default grid is G2.
    'start-preprocess' will be run against the input line  prior to any processing.
    ( in process_actions() )
    '''
    LOCATOR_TABLE = {
        b"I01": {'start-preprocess': lambda x: re.sub(b'\xad\w\d+\s*', b'', x),
                 # remove extra data not used.
                 #\x07I01Monday, April 18, 2016\xadD382­\x07I02Daily Digest\x07T1
                 'start': "<h3><em>",            'end': "</em></h3>",          'grid': b"G2", },
        b"I06": {'start': "",                    'end': "",                    'grid': b"", },
        b"I07": {'start': "",                    'end': "",                    'grid': b"", },
        b"I08": {'start': "",                    'end': "",                    'grid': b"", },
        b"I02": {'start': "<center><h1>",        'end': "</h1></center>",      'grid': b"G2", },
        b"I03": {'start': "<h4>",                'end': "</h4>",               'grid': b"G1", },
        b"I04": {'start': "<ul><strong>",        'end': "</strong></ul>",      'grid': b"G1", },
        b"I05": {'start': "<center><h2>",        'end': "</h2></center>",      'grid': b"G1", },
        b"I85": {'start': "<center>",            'end': "</center>",           'grid': b"G1", },
        b"I20": {'start': "<em>",                'end': "</em>",               'grid': b"G1", },
        b"I22": {'start': "<p><center><em>",     'end': "</em></center>",      'grid': b"G1", },
        b"I23": {'start': "<p><center><em>",     'end': "</em></center>",      'grid': b"G2", },
        b"I24": {'start': "<p><center><strong>", 'end': "</strong></center>",   'grid': b"G2", },
        b"I25": {'start': "<p><center><em>",     'end': "</em></center>",      'grid': b"G2", },
        b"I50": {'start': "<center><h3><em>",    'end': "</em></h3></center>", 'grid': b"G2", },
        b"I51": {'start': "<p><strong>",         'end': "</strong><p>",        'grid': b"G1", },
        b"I52": {'start': "<p><center><strong>", 'end': "</strong></center><p>", 'grid': b"G1", },

        b"I67H": {'start': "<span class='bell-I67H dailydigest-extension'>", 'end': "</span>", 'grid': b"", },

        b"I70": {'start': "<p><center><strong>", 'end': "</strong></center>",   'grid': b"G1", },
        b"I71": {'start': "<p><strong>",         'end': "</strong>",           'grid': b"G1", },
        b"I83": {'start': "<p><strong>",         'end': "</strong>",           'grid': b"G1", },
        b"I10": {'start': "<p><strong>",         'end': "</strong>",           'grid': b"G1", },
        b"I11": {'start': "<p>",                 'end': "",                    'grid': b"G1", },
        b"I12": {'start': "<p>",                 'end': "",                    'grid': b"G1", },
        b"I13": {'start': "",                    'end': "<br>",                'grid': b"G1", },
        b"I14": {'start': "",                    'end': "<br>",                'grid': b"G1", },
        b"I15": {'start': "<p>",                 'end': "<br>",                'grid': b"G1", },
        b"I21": {'start': "<p>",                 'end': "",                    'grid': b"G1", },
        b"I29": {'start': "<p><strong>",         'end': "</strong><br>",       'grid': b"G1", },
        b"I30": {'start': "<br /><p><strong>",   'end': "</strong>",           'grid': b"G1", },
        b"I31": {'start': "<strong>",            'end': "</strong>",           'grid': b"G1", },
        b"I40": {'start': "<em>",                'end': "</em>",               'grid': b"G1", },
        b"I41": {'start': "<br /><strong><em>",        'end': "</em></strong>",      'grid': b"G2", },
        b"I81": {'start': "<pre><strong>",       'end': "</strong></pre>",     'grid': b"G2", },
        b"I82": {'start': "<pre><strong>",       'end': "</strong></pre>",     'grid': b"G2", },
        b"L": {'start': "<br /><strong>",       'end': "</strong><br /><br />",     'grid': b"G2", },
        b"P": {'start': "<p>",                    'end': "</p>",                'grid': b"G1"},

        b"G1": {'start': "",                    'end': "",                   'grid': b"G1"},
        b"G2": {'start': "",                    'end': "",                   'grid': b"G2"},
        b"G3": {'start': "",                    'end': "",                   'grid': b"G3"},
        b"G4": {'start': "",                    'end': "",                   'grid': b"G4"},
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
