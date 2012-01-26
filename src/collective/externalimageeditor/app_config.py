#-*- coding: utf-8 -*-
"""Specific project configuration."""
GLOBALS = globals()




################################################################################
# Products that have entries in quickinstaller,
# here are their 'id' (not the translated name)
################################################################################

PRODUCT_DEPENDENCIES = (\
)

EXTENSION_PROFILES = ('collective.externalimageeditor:default',)

SKIN = 'collective.skin'
HIDDEN_PRODUCTS = [u'plone.app.openid', u'NuPlone',
#      u'plone.app.blob',
#      u'plone.app.dexterity',
#      u'Products.TinyMCE',
#      u'plone.app.z3cform',
    #with_ploneproduct_dexterity

#    u'plone.app.dexterity',
    #with_ploneproduct_tinymce

#    u'TinyMCE',
#    u'collective.externalimageeditor.migrations.v1_1',
#    u'collective.externalimageeditor.migrations',
]
HIDDEN_PROFILES = [u'plone.app.openid', u'NuPlone',
    u'collective.externalimageeditor.migrations.v11',
    u'collective.externalimageeditor.migrations',
      u'plone.app.blob',
      u'plone.app.dexterity',
      u'Products.TinyMCE',
      u'plone.app.z3cform',

]

from zope.interface import implements
from Products.CMFQuickInstallerTool.interfaces import INonInstallable as INonInstallableProducts
from Products.CMFPlone.interfaces import INonInstallable as INonInstallableProfiles

class HiddenProducts(object):
    implements(INonInstallableProducts)

    def getNonInstallableProducts(self):
        return HIDDEN_PRODUCTS

class HiddenProfiles(object):
    implements(INonInstallableProfiles)

    def getNonInstallableProfiles(self):
        return [ u'plone.app.openid', u'NuPlone', ]
