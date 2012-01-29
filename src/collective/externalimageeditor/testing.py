from Testing import ZopeTestCase as ztc
import transaction
from OFS.Folder import Folder

import unittest2 as unittest

from zope.configuration import xmlconfig

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing.selenium_layers import SELENIUM_FUNCTIONAL_TESTING as SELENIUM_TESTING
from plone.testing import zodb, zca, z2

TESTED_PRODUCTS = (\
)


def print_contents(browser, dest='~/.browser.html'):
    """Print the browser contents somewhere for you to see its context
    in doctest pdb, type print_contents(browser) and that's it, open firefox
    with file://~/browser.html."""
    import os
    open(os.path.expanduser(dest), 'w').write(browser.contents)  

class Browser(z2.Browser):
    def print_contents(browser, dest='~/.browser.html'):
        return print_contents(browser, dest)

class CollectiveExternalimageeditorLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )
    """Layer to setup the externalimageeditor site"""
    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def setUpZope(self, app, configurationContext):
        """Set up the additional products required for the collective) site externalimageeditor.
        until the setup of the Plone site testing layer.
        """
        self.app = app
        self.browser = Browser(app)
        # old zope2 style products
        for product in TESTED_PRODUCTS:
            z2.installProduct(product)

        # ----------------------------------------------------------------------
        # Import all our python modules required by our packages
        # ---------------------------------------------------------------------
        #with_ploneproduct_dexterity
        import plone.app.dexterity
        self.loadZCML('configure.zcml', package=plone.app.dexterity)

        # -----------------------------------------------------------------------
        # Load our own externalimageeditor
        # -----------------------------------------------------------------------
        import collective.externalimageeditor
        self.loadZCML('configure.zcml', package=collective.externalimageeditor)

        # ------------------------------------------------------------------------
        # - Load the python packages that are registered as Zope2 Products
        #   which can't happen until we have loaded the package ZCML.
        # ------------------------------------------------------------------------

        z2.installProduct(app, 'collective.externalimageeditor')

        # -------------------------------------------------------------------------
        # support for sessions without invalidreferences if using zeo temp storage
        # -------------------------------------------------------------------------
        app.REQUEST['SESSION'] = self.Session()
        if not hasattr(app, 'temp_folder'):
            tf = Folder('temp_folder')
            app._setObject('temp_folder', tf)
            transaction.commit()
        ztc.utils.setupCoreSessions(app)

    def setUpPloneSite(self, portal):
        applyProfile(
            portal,
            'collective.externalimageeditor:default'
        )


COLLECTIVE_EXTERNALIMAGEEDITOR_FIXTURE             = CollectiveExternalimageeditorLayer()
COLLECTIVE_EXTERNALIMAGEEDITOR_INTEGRATION_TESTING = IntegrationTesting(bases = (COLLECTIVE_EXTERNALIMAGEEDITOR_FIXTURE,),name = "CollectiveExternalimageeditor:Integration")
COLLECTIVE_EXTERNALIMAGEEDITOR_FUNCTIONAL_TESTING  = FunctionalTesting(bases = (COLLECTIVE_EXTERNALIMAGEEDITOR_FIXTURE,), name = "CollectiveExternalimageeditor:Functional")
COLLECTIVE_EXTERNALIMAGEEDITOR_SELENIUM_TESTING    = FunctionalTesting(bases = (SELENIUM_TESTING, COLLECTIVE_EXTERNALIMAGEEDITOR_FUNCTIONAL_TESTING,), name = "CollectiveExternalimageeditor:Selenium")

# vim:set ft=python:
