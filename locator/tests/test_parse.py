import unittest
import logging
from locator.parse import split,getField
logger = logging.getLogger(__name__)


class ParseTest(unittest.TestCase):

    def test_split(self):
        data = b'''F8383

I01A.B.A.T.E. OF ILLINOIS, INC.
I03Remarks in House
I05Safety: tribute to efforts to promote motorcycle safety and education, H4692 [21MY]

I01A.B.A.T.E. OF PENNSYLVANIA (organization)
I03Remarks in House
I05Motorcycle Toy Run: anniversary, E1437 [17SE]

I01A.O. SMITH CORP.
I03Remarks in Senate
I05Anniversary, S5856 [18SE]

I01AARON, HENRY J.
I03Remarks in Senate
I05Social Security Advisory Board: nomination, S5354, S5365 [8SE]
I05___nomination, unanimous-consent agreement, S5330 [1AU]
'''
        good_result = [b'\x07F8383\n\n',
                       b'\x07I01A.B.A.T.E. OF ILLINOIS, INC.\n\x07I03Remarks in House\n\x07I05Safety: tribut'
                       b'e to efforts to promote motorcycle safety and education, H4692 [21MY]\n\n',
                       b'\x07I01A.B.A.T.E. OF PENNSYLVANIA (organization)\n\x07I03Remarks in House\n\x07I05M'
                       b'otorcycle Toy Run: anniversary, E1437 [17SE]\n\n',
                       b'\x07I01A.O. SMITH CORP.\n\x07I03Remarks in Senate\n\x07I05Anniversary, S5856 [18SE]'
                       b'\n\n',
                       b'\x07I01AARON, HENRY J.\n\x07I03Remarks in Senate\n\x07I05Social Security Advisory B'
                       b'oard: nomination, S5354, S5365 [8SE]\n\x07I05___nomination, unanimous-consen'
                       b't agreement, S5330 [1AU]\n']

        for cnt, found in enumerate(split(data, b'I01')):
            self.assertEqual(found, good_result[cnt])

    def test_match(self):
        data = b'''I01A.B.A.T.E. OF ILLINOIS, INC.'''
        m = getField(data, b'I01(.+?)$')
        self.assertEqual(m.group(1), b'A.B.A.T.E. OF ILLINOIS, INC.')

    def test_split_and_match(self):
        data = b'''F8383

I01A.B.A.T.E. OF ILLINOIS, INC.
I03Remarks in House
I05Safety: tribute to efforts to promote motorcycle safety and education, H4692 [21MY]

I01A.B.A.T.E. OF PENNSYLVANIA (organization)
I03Remarks in House
I05Motorcycle Toy Run: anniversary, E1437 [17SE]

I01A.O. SMITH CORP.
I03Remarks in Senate
I05Anniversary, S5856 [18SE]

I01AARON, HENRY J.
I03Remarks in Senate
I05Social Security Advisory Board: nomination, S5354, S5365 [8SE]
I05___nomination, unanimous-consent agreement, S5330 [1AU]
'''
        sections = split(data, b'I01')
        good_result = [None,
                       b'A.B.A.T.E. OF ILLINOIS, INC.\n\x07I03Remarks in House\n\x07I05Safety: tribut'
                       b'e to efforts to promote motorcycle safety and education, H4692 [21MY]\n\n',
                       b'A.B.A.T.E. OF PENNSYLVANIA (organization)\n\x07I03Remarks in House\n\x07I05M'
                       b'otorcycle Toy Run: anniversary, E1437 [17SE]\n\n',
                       b'A.O. SMITH CORP.\n\x07I03Remarks in Senate\n\x07I05Anniversary, S5856 [18SE]'
                       b'\n\n',
                       b'AARON, HENRY J.\n\x07I03Remarks in Senate\n\x07I05Social Security Advisory B'
                       b'oard: nomination, S5354, S5365 [8SE]\n\x07I05___nomination, unanimous-consen'
                       b't agreement, S5330 [1AU]\n']

        for cnt, section in enumerate(sections):
            field = getField(section, b'\x07I01(.+?)$')
            self.assertEqual(field, good_result[cnt])
