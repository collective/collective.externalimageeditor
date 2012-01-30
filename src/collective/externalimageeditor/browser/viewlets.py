from plone.app.layout.viewlets import common as base
from zope.component import getAdapters

from collective.externalimageeditor import interfaces as i


class ExternalEditorViewlet(base.ViewletBase):
    """ Add External links for editing an image"""
    def data(self):
        data = []
        context = self.context
        request = self.request
        adapters = getAdapters((context, request), provided=i.IExternalImageEditor)
        for name, a in adapters:
            if a.enabled:
                data.append(a.link_infos)
        return data

