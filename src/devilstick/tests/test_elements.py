# Copyright 2007-2009, BlueDynamics Alliance - http://bluedynamics.com
# BSD License derivative, see LICENSE.txt or package long description.

import unittest
import doctest
import pprint
import interlude

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    '../elements.txt',
]

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            file, 
            optionflags=optionflags,
            globs=dict(interact=interlude.interact, pprint=pprint.pprint),
        ) for file in TESTFILES
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite') 