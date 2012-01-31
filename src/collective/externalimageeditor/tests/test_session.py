"""
Checking specifics portal settings.
This package must run in a externalimageeditor package (needs app_config.py)
"""

import datetime
import unittest2 as unittest
from persistent.mapping import PersistentMapping

from base import (
    IntegrationTestCase,
    TestCase,
)

from Products.CMFCore.utils import getToolByName

# adapt if any need to your testing utils module.
from collective.externalimageeditor.tests.globals import *
from collective.externalimageeditor import session as s
from collective.externalimageeditor import testing

from plone.app.testing.helpers import (
    login,
    TEST_USER_NAME,
    logout,
)

class TestSession(IntegrationTestCase):
    """Check Policy."""

    def setUp(self):
        super(TestSession, self).setUp()
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'sessionfolder')
        self.context = self.portal['sessionfolder']
        self.request = TestRequest()
        self.session = s.EditSessionHelper(self.context, self.request)
        self.logout()

    def tearDown(self):
        super(TestSession, self).tearDown()
        self.loginAsPortalOwner()
        self.portal.manage_delObjects(['sessionfolder'])
        self.logout()

    def test_get_user(self):
        self.loginAsPortalOwner()
        self.assertEquals(self.session.get_user(), 'admin')
        self.logout()
        self.assertEquals(self.session.get_user(), None)

    def test_want_user(self):
        self.loginAsPortalOwner()
        self.assertEquals(self.session.want_user(), 'admin')
        self.logout()
        self.assertRaises(s.AnonymousException, self.session.want_user)

    def test_registry(self):
        self.assertTrue(isinstance(self.session.registry, PersistentMapping))

    def test_edit_session(self):
        self.loginAsPortalOwner()
        self.session.register_edit_session('foo')
        self.assertTrue(
            ('foo', 'admin') in self.session.registry
        )
        self.assertTrue(
            isinstance(
                self.session.registry[('foo', 'admin')],
                datetime.datetime)
        )
        self.logout()

    def test_remove_session(self):
        self.loginAsPortalOwner()
        self.session.register_edit_session('foo')
        self.assertTrue(
            ('foo', 'admin') in self.session.registry
        )
        self.session.remove_edit_session('foo')
        self.assertFalse(
            ('foo', 'admin') in self.session.registry
        )
        self.logout()

    def test_edited_by(self):
        self.loginAsPortalOwner()
        self.session.register_edit_session('foo')
        self.assertTrue(self.session.is_edited_by('foo'))
        self.assertTrue(self.session.is_edited_by('foo', 'admin'))
        self.assertTrue(
            ('foo', 'admin') in self.session.registry
        )
        self.session.remove_edit_session('foo')
        self.assertFalse(
            ('foo', 'admin') in self.session.registry
        )
        self.assertFalse(self.session.is_edited_by('foo'))
        self.assertFalse(self.session.is_edited_by('foo', 'admin'))
        self.logout()

def test_suite():
    """."""
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromName(
            __name__))
    return suite

