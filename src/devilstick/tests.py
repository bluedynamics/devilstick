import doctest
import interlude
import pprint
import unittest

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    'metamodel.rst',
]


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            filename,
            optionflags=optionflags,
            globs=dict(interact=interlude.interact, pprint=pprint.pprint),
        ) for filename in TESTFILES
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
