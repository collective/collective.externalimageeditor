from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc
import transaction
from OFS.Folder import Folder

from Products.PloneTestCase import PloneTestCase as ptc
from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer

TESTED_PRODUCTS = (\
#with_ploneproduct_tinymce
    'TinyMCE',
)


class Layer(BasePTCLayer):
    """Layer to setup the externalimageeditor site"""
    class Session(dict):
        def set(self, key, value):
            self[key] = value  

    def afterSetUp(self):
        """Set up the additional products required for the collective) site externalimageeditor.
        until the setup of the Plone site testing layer.
        """ 
        for product in TESTED_PRODUCTS:
            ztc.installProduct(product) 

        # ------------------------------------------------------------------------------------
        # Import all our python modules required by our packages
        # ------------------------------------------------------------------------------------
    #with_ploneproduct_dexterity
        import plone.app.dexterity
        self.loadZCML('configure.zcml', package=plone.app.dexterity)   
    #with_ploneproduct_pz3cform
        import plone.directives.form
        self.loadZCML('configure.zcml', package=plone.directives.form)   
    #with_ploneproduct_fivegrok
        import five.grok
        self.loadZCML('configure.zcml', package=five.grok)   
    #with_ploneproduct_tinymce
        import Products.TinyMCE
        self.loadZCML('configure.zcml', package=Products.TinyMCE)   
    #with_ploneproduct_cz3cformgrok
        import plone.app.z3cform
        self.loadZCML('configure.zcml', package=plone.app.z3cform)   
        import plone.z3cform
        self.loadZCML('configure.zcml', package=plone.z3cform)   
    #with_ploneproduct_ploneappblob
        import plone.app.blob
        self.loadZCML('configure.zcml', package=plone.app.blob)   

        # ------------------------------------------------------------------------------------
        # - Load the python packages that are registered as Zope2 Products via Five
        #   which can't happen until we have loaded the package ZCML.
        # ------------------------------------------------------------------------------------

        #with_ploneproduct_ploneappblob
        ztc.installPackage('plone.app.blob')

        ztc.installPackage('collective.externalimageeditor')


        # ------------------------------------------------------------------------------------
        # Load our own externalimageeditor
        # ------------------------------------------------------------------------------------
        import collective.externalimageeditor
        self.loadZCML(
            'configure.zcml', 
            package=collective.externalimageeditor
        )
        self.addProfile(
            'collective.externalimageeditor:default'
        )
        
        # ------------------------------------------------------------------------------------
        # support for sessions without invalidreferences if using zeo temp storage
        # ------------------------------------------------------------------------------------
        self.app.REQUEST['SESSION'] = self.Session()
        if not hasattr(self.app, 'temp_folder'):
            tf = Folder('temp_folder')
            self.app._setObject('temp_folder', tf)
            transaction.commit()
        ztc.utils.setupCoreSessions(self.app) 


layer = Layer(bases=[ptc_layer])
# vim:set ft=python:
