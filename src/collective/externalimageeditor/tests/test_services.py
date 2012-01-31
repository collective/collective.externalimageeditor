"""
Checking specifics portal settings.
This package must run in a externalimageeditor package (needs app_config.py)
"""

import datetime
import unittest2 as unittest
from persistent.mapping import PersistentMapping
from StringIO import StringIO
from zope.interface import alsoProvides
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
from collective.externalimageeditor import testing
from collective.externalimageeditor import interfaces as i

from plone.app.testing.helpers import (
    login,
    TEST_USER_NAME,
    logout,
)               

from pkg_resources import resource_filename

imgpath = resource_filename('collective.externalimageeditor', '/browser/resources/edit_12.png')

class TestService(IntegrationTestCase):
    """Check Policy."""

    def setUp(self):
        super(TestService, self).setUp()
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'servicefolder')
        self.context = self.portal['servicefolder']
        self.context.invokeFactory('Image', 'img')
        self.img = self.context['img']
        self.request = TestRequest()


        alsoProvides(self.request, IAttributeAnnotatable)
        self.service = s.ExternalImageEditor(self.context, self.request)
        self.pixlr  = s.PixlrEditor(self.context, self.request)
        self.iservice = s.ExternalImageEditor(self.img, self.request)
        self.ipixlr  = s.PixlrEditor(self.img, self.request) 
        self.logout()

    def tearDown(self):
        super(TestService, self).tearDown()
        self.loginAsPortalOwner()
        self.portal.manage_delObjects(['servicefolder'])
        self.logout()

    def test_save(self):
        self.assertRaises(Exception, self.service.save)

    def test_at_store(self):
        data  = {
            'data': open(imgpath).read(),
            'mimetype': 'image/png',
            'filename': 'foo.png',
        }
        self.iservice.at_store(data)
        self.assertEquals(self.img.data, data['data'])
        self.assertTrue(
            'Your image has been updated' in re.sub(
                'statusmessages="([^=]+==).*', '\\1', 
                dict(
                    self.request.response.getHeaders()
                )['Set-Cookie']
            ).decode('base64')
        )

    def test_fetch(self):
        data = self.iservice.fetch('file://%s' % imgpath)
        self.assertEquals(data['mimetype'], 'image/png')
        self.assertTrue('PNG'in data['data'])
        self.assertTrue(re.match('externaledtiorimage_exported_image.*jpg', data['filename']))
        self.assertRaises(s.DownloadError, self.iservice.fetch, 'http://INVALID')


    def test_pixlr_infos(self):
        self.assertEquals(
            self.ipixlr.get_ico, 
            'http://nohost/plone/'
            '++resource++collective.externalimageeditor'
            '/pixlr_12.png')
        self.assertTrue(
            self.pixlr.link_infos['title'], u'Edit with pixlr.')
        self.assertTrue(
            self.pixlr.edit_url, 
            'http://nohost/plone/servicefolder/'
            '@@externalimageeditor_edit?service=pixlr')
        self.assertEquals(
            self.ipixlr.service_edit_url, 
            'http://www.pixlr.com/editor?'
            'image=http%3A%2F%2Fnohost%2Fplone%2Fservicefolder%2Fimg'
            '&locktarget=true'
            '&target=http%3A%2F%2Fnohost%2Fplone'
            '%2Fservicefolder%2Fimg%2F%40%40externalimageeditor_save'
            '%3Fservice%3Dpixlr')

    @property
    def registry(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            i.IExternalimageeditorConfiguration) 
        return settings

    def test_enabled(self):
        self.deactivate_pixlr()
        self.assertFalse(self.pixlr.enabled)
        self.activate_pixlr()
        self.assertTrue(self.pixlr.enabled)

    def activate_pixlr(self):
        self.registry.has_pixlr = True
                        
    def deactivate_pixlr(self):
        self.registry.has_pixlr = False


def test_suite():
    """."""
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromName(
            __name__))
    return suite 
