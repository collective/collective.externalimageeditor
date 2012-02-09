"""
Checking specifics portal settings.
This package must run in a externalimageeditor package (needs app_config.py)
"""

import datetime
import unittest2 as unittest
from persistent.mapping import PersistentMapping
from StringIO import StringIO
from zope.interface import alsoProvides, implements
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from base import (
    IntegrationTestCase,
    TestCase,
)

from Products.CMFCore.utils import getToolByName

# adapt if any need to your testing utils module.
from collective.externalimageeditor.tests.globals import *
from collective.externalimageeditor import services as s
from collective.externalimageeditor import session
from collective.externalimageeditor import testing
from collective.externalimageeditor import interfaces as i

from plone.app.testing.helpers import (
    login,
    TEST_USER_NAME,
    logout,
)


from zope.publisher.interfaces.browser import IBrowserRequest
from pkg_resources import resource_filename

from collective.externalimageeditor.browser.methods import Save, Edit

imgpath = resource_filename('collective.externalimageeditor', '/browser/resources/edit_12.png')

class FakeResponse(object):
    def __init__(self):
        self._redirect = None
    def redirect(self, url):
        self._redirect = url

class FakeRequest(object):
    implements(IBrowserRequest)
    def __init__(self):
        self.response = FakeResponse()
        self.form = {}
        self.URL = 'http://localhost:8080/Plone'
        self.method = 'GET'

class Base(IntegrationTestCase):
    """Check Policy."""

    def setUp(self):
        super(Base, self).setUp()
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'servicefolder')
        self.context = self.portal['servicefolder']
        self.context.invokeFactory('Image', 'save_img')
        self.context.invokeFactory('News Item', 'mynews')
        self.img = self.context['save_img']
        self.news = self.context['mynews']
        self.request = TestRequest()
        alsoProvides(self.request, IAttributeAnnotatable)
        self.activate_pixlr()

    def tearDown(self):
        super(Base, self).tearDown()
        self.loginAsPortalOwner()
        self.deactivate_pixlr()
        self.portal.manage_delObjects(['servicefolder'])
        self.logout()

    @property
    def registry(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            i.IExternalimageeditorConfiguration)
        return settings

    def activate_pixlr(self):
        self.registry.has_pixlr = True

    def deactivate_pixlr(self):
        self.registry.has_pixlr = False

class TestEdit(Base):

    def test_localhost(self):
        req = FakeRequest()
        req.URL = 'http://localhost'
        view = Edit(self.img, req)
        ret = view()
        self.assertEquals(ret, 'localhost is not supported')

    def test_http_get_edit_wrongservice(self):
        req = FakeRequest()
        req.URL='http://foo'
        req.form['service'] = 'unknown'
        view = Edit(self.img, req)
        view()
        self.assertEquals(req.response._redirect, 'http://nohost/plone/servicefolder/save_img/view')

    def test_http_get_edit(self):
        req = FakeRequest()
        req.URL='http://foo'
        req.form['service'] = 'pixlr'
        view = Edit(self.img, req)
        view()
        self.assertTrue(
            req.response._redirect.startswith(
            'http://www.pixlr.com/editor?'
            'image=http%3A%2F%2Fnohost%2Fplone%2Fservicefolder%2Fsave_img'
            '&locktarget=true'
            '&target=http%3A%2F%2Fnohost%2Fplone%2Fservicefolder%2Fsave_img%2F%40%40externalimageeditor_save%3Fservice%3Dpixlr'
            )
        )

class TestSave(Base):
    def test_unknown_service(self):
        req = FakeRequest()
        req.form['service'] = 'unknown'
        req.URL='http://foo' 
        ses = session.EditSessionHelper(self.img, req)
        ses.register_edit_session('unknown') 
        view = Save(self.img, req)
        ret = view()
        self.assertEquals(req.response._redirect, 'http://nohost/plone/servicefolder/save_img/view')
        self.assertEquals(ret, 'Invalid edit proxy request!')


    def test_save_without_editsession(self):
        req = FakeRequest()
        req.URL='http://foo'
        req.form['service'] = 'pixlr'
        req.form['image'] = 'file://%s' % imgpath
        view = Save(self.img, req)
        ret = view()
        self.assertEquals(ret, 'No edit session!')

    def test_save(self):
        req = FakeRequest()
        ses = session.EditSessionHelper(self.img, req)
        ses.register_edit_session('pixlr')
        req.URL='http://foo'
        req.form['service'] = 'pixlr'
        req.form['image'] = 'file://%s' % imgpath
        view = Save(self.img, req)
        ret = view()
        self.assertEquals(ret, 'image updated')
        self.assertEquals(req.response._redirect, 'http://nohost/plone/servicefolder/save_img/view')
        ses = session.EditSessionHelper(self.news, req)
        ses.register_edit_session('pixlr')
        req.URL='http://foo'
        req.form['service'] = 'pixlr'
        req.form['image'] = 'file://%s' % imgpath
        view = Save(self.news, req)
        ret = view()
        self.assertEquals(ret, 'image updated')
        self.assertEquals(req.response._redirect, 'http://nohost/plone/servicefolder/mynews')
 

def test_suite():
    """."""
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromName(
            __name__))
    return suite
