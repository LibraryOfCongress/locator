import unittest
import logging
from locator.dailydigest import DailyDigestInputParser
from locator.parser import LocatorParser, OutputParser
logger = logging.getLogger(__name__)


class DailydigestTest(unittest.TestCase):

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

    def test_whitespace(self):
        '''Test to make sure whitespace is not being added in incorrectly'''
        final = self._load_and_convert('dtestPageWhitespace.rec')
        #self.assertEqual(final,  '''<html><h3><em>Tuesday, September 6, 2016<br /></em></h3><center><h1>Daily Digest<br /></h1></center><h4>HIGHLIGHTS <br /></h4><br /><p><strong>Petitions and Memorials:<br /></strong><pre><strong>Pages S5276&ndash;77<br /></strong></pre><br /><p><strong>Additional Cosponsors:<br /></strong><pre><strong>Pages S5279&ndash;81\n<br /></html>''')
        self.assertEqual(final,  '''<html><h3><em>Tuesday, September 6, 2016</em></h3><center><h1>Daily Digest</h1></center><h4>HIGHLIGHTS </h4><br /><p><strong>Petitions and Memorials:</strong><br /><strong>Pages S5276&ndash;77</strong><br /><br /><br /><p><strong>Additional Cosponsors:</strong><br /><strong>Pages S5279&ndash;81\n</html>''')


    def test_badchar27(self):
        '''Test to ensure that random 27s are not appearing due to \x07S0627
        https://www.law.cornell.edu/lexcraft/uscode/docs/locod_xhtml.html
        and
        https://www.gpo.gov/pdfs/vendors/subformat_generation.pdf
        make me think that \x07S0027 is a subformat of type 27 that probably has
        to do with formatting into columns...our conversion is ignorming this
        and will just strip out \x07S{\d+}
        '''

        final = self._load_and_convert('tdailydigestchar27.rec')
        self.assertEqual(final,  '''<html><h3><em>Wednesday, September 14, 2016</em></h3><center><h1>Daily Digest</h1></center><strong> </strong><center><h2>Senate</h2></center><center><h3><em>Chamber Action</em></h3></center><strong> Senate continued consideration of S. 2848, to provide for the conservation and development of water and related resources, to authorize the Secretary of the Army to construct various projects for improvements to rivers and harbors of the United States, taking action on the following amendment proposed thereto: </strong><br /><strong>Pages S5694&ndash;S5718 </strong><br /><br /><p>:<p>McConnell (for Inhofe) Amendment No. 4979, in the nature of a substitute.  E1273<br />\n<center>[Page:D920] </center></html>''')
