from clickreviews.cr_common import ClickReview
from clickreviews import cr_tests


class ClickReviewTestCase(cr_tests.TestClickReview):

    def setUp(self):
        # Monkey patch various file access classes. stop() is handled with
        # addCleanup in super()
        cr_tests.mock_patch()
        super()
        self.review = ClickReview('app.click', 'review_type')

    def test_add_result_default_manual_review(self):
        self.review._add_result('info', 'some-check', 'OK')
        self.assertEqual(self.review.click_report, {
            'info': {
                'review_type_some-check': {
                    'text': 'OK',
                    'manual_review': False,
                }
            },
            'warn': {},
            'error': {},
        })

    def test_add_result_custom_manual_review(self):
        self.review._add_result('info', 'some-check', 'OK',
                                manual_review=True)
        self.assertEqual(self.review.click_report, {
            'info': {
                'review_type_some-check': {
                    'text': 'OK',
                    'manual_review': True,
                }
            },
            'warn': {},
            'error': {},
        })

    def test_verify_peer_hooks_empty(self):
        '''Check verify_peer_hooks() - empty'''
        peer_hooks = dict()
        my_hook = "foo"
        peer_hooks[my_hook] = dict()
        peer_hooks[my_hook]['allowed'] = []
        peer_hooks[my_hook]['required'] = []
        self.review.peer_hooks = peer_hooks

        d = self.review._verify_peer_hooks()
        self.assertEqual(0, len(d.keys()))

    def test_verify_peer_hooks_missing(self):
        '''Check verify_peer_hooks() - missing required'''
        peer_hooks = dict()
        my_hook = "desktop"
        peer_hooks[my_hook] = dict()
        peer_hooks[my_hook]['allowed'] = ["apparmor", "urls"]
        peer_hooks[my_hook]['required'] = ["nonexistent"]
        self.review.peer_hooks = peer_hooks

        d = self.review._verify_peer_hooks()
        self.assertEqual(1, len(d.keys()))
        self.assertTrue('missing' in d.keys())
        self.assertTrue('nonexistent' in d['missing'][self.default_appname])

    def test_verify_peer_hooks_disallowed(self):
        '''Check verify_peer_hooks() - disallowed'''
        peer_hooks = dict()
        my_hook = "desktop"
        peer_hooks[my_hook] = dict()
        peer_hooks[my_hook]['allowed'] = ["apparmor"]
        peer_hooks[my_hook]['required'] = []
        self.review.peer_hooks = peer_hooks

        d = self.review._verify_peer_hooks()
        self.assertEqual(1, len(d.keys()))
        self.assertTrue('disallowed' in d.keys())
        self.assertTrue('urls' in d['disallowed'][self.default_appname])
