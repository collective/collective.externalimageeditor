#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'

import time
from StringIO import StringIO
from datetime import datetime
import urllib

from zope import interface
from zope.component import getUtility
from zope.event import notify

from Products.ATContentTypes.interfaces.image import IATImage
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.event import ObjectEditedEvent
from Products.statusmessages.interfaces import IStatusMessage

from plone.registry.interfaces import IRegistry

from collective.externalimageeditor import interfaces as i
from collective.externalimageeditor.externalimageeditor import MessageFactory as _, logger

class DownloadError(Exception):
    """Download failed"""

class ExternalImageEditor(i.BaseAdapter):
    interface.implements(i.IExternalImageEditor)
    #ico = 'edit_12.png'
    ico = 'icofx_12.png'

    def save(self):
        """Save the image"""
        raise Exception('not implemented')

    def fetch(self, url):
        """download image and return dict object:
            {'filename': ... , 'data':..., 'mimetype':...}
        """
        if not url: return
        def download():
            return urllib.urlopen(url)
        # be smart, download 3 tries on error
        tries = 3
        while tries:
            tries -= 1
            try:
                image = download()
                if image.getcode() and (image.getcode() != 200):
                    time.sleep(1)
                else: break
            except Exception, e:
                logger.error('download error: %s' % e)
            if not tries:
                raise DownloadError('download failed')
        res = {}
        res['filename'] = "externaledtiorimage_exported_image" + datetime.now().isoformat()+ ".jpg"
        res['data'] = image.read()
        res['mimetype'] = image.info().gettype()
        return res

    @property
    def enabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            i.IExternalimageeditorConfiguration)
        return getattr(settings, 'has_%s'%self.name, False)

    @property
    def edit_url(self):
        return  "%s/@@%s?service=%s" % (
            self.context.absolute_url(),
            'externalimageeditor_edit',
            self.name)

    @property
    def get_ico(self):
        return '%s/%s/%s' % (
            self.portal_url(),
            '++resource++collective.externalimageeditor',
            self.ico)

    @property
    def link_infos(self):
        return {
            'icon': self.get_ico,
            'title': _("Edit with %s.") % self.name,
            "url": self.edit_url,
        }

    def at_store(self, image_info, field_name='image'):
        """Do the job to fetch image and update the context with it"""
        sio = StringIO()
        sio.write(image_info['data'])
        field = self.context.getField(field_name) or self.context.getPrimaryField()
        field.set(
            self.context,
            image_info['data'],
            mimetype=image_info['mimetype'],
            filename=image_info['filename'],
            refresh_exif=False
        )
        notify(ObjectEditedEvent(self.context))
        IStatusMessage(self.request).addStatusMessage(_('Your image has been updated.'), 'info')
 

class IPixlrEditor(i.IExternalImageEditor):
    """Marker interface for pixlr adapter."""

class PixlrEditor(ExternalImageEditor):
    interface.implements(IPixlrEditor)
    name = 'pixlr'
    ico = 'pixlr_12.png'

    @property
    def service_edit_url(self):
        context, thisurl, url = self.context, '', ''
        if IATImage.providedBy(self.context):
            thisurl = self.context.absolute_url()
            surl = 'http://www.pixlr.com/editor'
            params = {
                'image': thisurl,
                "locktarget": "true",
                "target": "%s/@@externalimageeditor_save?service=%s" % (thisurl, self.name),
            }
            url = '%s?%s' % (surl, urllib.urlencode(params))
        return url

    def save(self):
        """Save the image"""
        context, request, form = self.context, self.request, self.request.form
        if not 'image' in form:
            raise Exception('invalid request')
        data = self.fetch(form['image'])
        if not data:
            raise Exception("image download fails")
        if IATImage.providedBy(self.context):
            self.at_store(data)


# vim:set et sts=4 ts=4 tw=80:
