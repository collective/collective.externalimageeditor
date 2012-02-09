from plone.app.layout.viewlets import common as base
from zope.component import getAdapters

from collective.externalimageeditor import interfaces as i
from Products.ATContentTypes.interfaces.image import IATImage
from Products.ATContentTypes.interfaces.interfaces import IATContentType

class ExternalEditorViewlet(base.ViewletBase):
    """ Add External links for editing an image"""

    def get_infos_for(self, context):
        data = {'embedded_images' : False,
                'contexts_info' : []}
        contexts_info = data['contexts_info']
        if IATImage.providedBy(self.context):
            contexts_info.append({'c':self.context, 'type': 'image'})
        if IATContentType.providedBy(self.context):
            for f in self.context.schema.keys():
                field = self.context.schema[f]
                if 'image' == field.type:
                    data['embedded_images'] = True
                    contexts_info.append(
                        {'c':field.get(self.context), 'type': 'atimage'}
                    )
        for context_info in contexts_info:
            request = self.request
            adapters = getAdapters((context_info['c'], request), provided=i.IExternalImageEditor)
            context_info['infos'] = []
            for name, a in adapters:
                if a.enabled:
                    context_info['infos'].append(a.link_infos)
        return data

    def data(self):
        data = self.get_infos_for(self.context)
        return data

