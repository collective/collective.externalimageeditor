"""
Checking specifics portal settings.
This package must run in a externalimageeditor package (needs app_config.py)
"""
import unittest

from Products.CMFCore.utils import getToolByName

from collective.externalimageeditor.app_config import SKIN, PRODUCT_DEPENDENCIES, GLOBALS
from collective.externalimageeditor.tests_tools import getWorkflows
from collective.externalimageeditor.tests.base import TestCase, setup_site
from collective.externalimageeditor.tests.portal_properties import check_portal_properties
from collective.externalimageeditor.tests.portal_mailhost   import check_portal_mailhost
from collective.externalimageeditor.tests.globals import (
    getTestingOptionsFromIni,
    errprint,
    ZOPETESTCASE,
    format_test_title,
    UNTESTED_WARNING,
)


_options = getTestingOptionsFromIni()


# utilities and basic variables/options
# if you have plone.reload out there add an helper to use in doctests while programming
# just use preload(module) in pdb :)
# it would be neccessary for you to precise each module to reload, this method is also not recursive.
# eg: (pdb) from foo import bar;preload(bar)
# see utils.py for details

# adapt if any need to your testing utils module.
from collective.externalimageeditor.tests.globals import *

class TestSetup(TestCase):
    """Check Policy."""

    wkf = getWorkflows()

    def afterSetUp(self):
        """."""
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.types = getToolByName(self.portal, 'portal_types')

    def test_skin_installed(self):
        """."""
        skins = getToolByName(self.portal, 'portal_skins')
        layer = skins.getSkinPath(SKIN)
        self.failUnless('collective_skin_custom_images' in layer)
        self.failUnless('collective_skin_custom_templates' in layer)
        self.failUnless('collective_skin_styles' in layer)
        self.assertEquals(SKIN, skins.getDefaultSkin())

    def test_products_dependencies_installed(self):
        """."""
        products = getToolByName(self.portal, 'portal_quickinstaller')
        for product in PRODUCT_DEPENDENCIES:
            self.failUnless(products.isProductInstalled(product))

def test_suite():
    """."""
    setup_site()
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite

