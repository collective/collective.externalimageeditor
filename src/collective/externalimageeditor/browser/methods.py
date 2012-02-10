#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'


import urllib

from zope import component, interface
from zope.component import getAdapter, getMultiAdapter, queryMultiAdapter, getUtility


from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.linkintegrity.interfaces import IOFSImage
from Products.ATContentTypes.interfaces.image import IATImage

from plone.registry.interfaces import IRegistry

from collective.externalimageeditor import interfaces as i
from collective.externalimageeditor import logger

from Products.ATContentTypes.interfaces.interfaces import IATContentType

from Acquisition import aq_parent


class ISave(interface.Interface):
    """Marker interface for ISave"""


class IEdit(interface.Interface):
    """Marker interface for IEdit"""
    def http_get_edit():
        """Use the http get facility to edit an online image...
        You must be warned it doesn't work with localhost
        """

class IAviary(IEdit):
    """Marker interface for Aviary"""


class Save(BrowserView):
    """Save an image after being edited on a webservice"""
    interface.implements(ISave)
    def __call__(self, *args):
        editor, ret = None,  ''
        form = self.request.form
        service = form.get('service', 'pixlr')
        context_url = self.context.absolute_url()
        # edit with pixlr by default
        try:
            editor = getMultiAdapter((self.context, self.request), i.IExternalImageEditor, name = service)
        except Exception, e:
            logger.info(
                'Invalid service or context: %s %s %s' % (
                    e, self.context, service
                )
            )
        invalid = True
        if editor is not None:
            session = getMultiAdapter((self.context, self.request), i.IEditSessionHelper)
            if session.is_edited_by(service):
                invalid = False
                try:
                    editor.save()
                except Exception, e:
                    ret = 'An error occured during image record: %s' % e
                ret = 'image updated'
            else:
                ret = 'No edit session!'
        if invalid:
            if not ret:
                ret = 'Invalid edit proxy request!'
            logger.info(ret)
        if IATImage.providedBy(self.context):
            context_url += "/view"
        parent = aq_parent(self.context)

        if (IATContentType.providedBy(parent)
            and IOFSImage.providedBy(self.context)):
            context_url = parent.absolute_url()
        if service not in ['aviary']:
            self.request.response.redirect(context_url)
        return ret

class Edit(BrowserView):
    """Redirect to a specific edit service"""
    interface.implements(IEdit)


    def __call__(self, *args):
        islocalhost = (self.request.URL.startswith('http://localhost')
                       or self.request.URL.startswith('127.0.0.1'))
        if self.request.method == 'GET' and not islocalhost:
            return self.http_get_edit()
        elif islocalhost:
            logger.info('doesn t support localhost editing at the moment')
            return 'localhost is not supported'

    def http_get_edit(self):
        """."""
        ret = 'OK'
        context_url = self.context.absolute_url()
        form = self.request.form
        service = form.get('service', 'pixlr')
        # edit with pixlr by default
        editor = queryMultiAdapter((self.context, self.request), i.IExternalImageEditor, name = service)
        if editor is not None:
            url = editor.service_edit_url
            getMultiAdapter((self.context, self.request), i.IEditSessionHelper).register_edit_session(service)
        else:
            ret = 'Invalid edit proxy request!'
            logger.info(ret)
            url = context_url
            if IATImage.providedBy(self.context):
                url += "/view"
        self.request.response.redirect(url)
        return ret

AVIARY_ED = """
var featherEditor = new Aviary.Feather({
    apiKey: '%(apikey)s',
    apiVersion: 2,
    language: '%(language)s',
    tools: 'all',
    hiresUrl: '%(image_url)s',
    appendTo: '',
    url: '%(image_preview)s',
    onLoad: function() {
        launchEditor('aviaryimage');
        jQuery('#aviaryimage').click(function(e) {
            launchEditor('aviaryimage');
        })
    },
    onSave: function(imageID, newURL) {
        $.post('%(callback)s',
        {image:newURL, service:"aviary",_authenticator:'%(authenticator)s'},
            function(data) {
            var img = document.getElementById(imageID);
            img.src = '%(image_preview)s'+'/?reload=1';
        });
    }
});
function launchEditor(id) {
    featherEditor.launch({image:id});
    return false;
}
"""

class Aviary(Edit):
    """Redirect to a specific edit service"""
    interface.implements(IAviary)
    template = ViewPageTemplateFile('aviary.pt')

    def http_get_edit(self):
        """Aviary use a javascript in our website to edit the image"""
        ret = ''
        form = self.request.form
        service = 'aviary'
        context_url = self.context.absolute_url()
        editor = queryMultiAdapter((self.context, self.request), i.IExternalImageEditor, name = service)
        languages = ['en', 'de', 'fr',
                     'ja', 'it', 'nl',
                     'es', 'ru']
        if editor.enabled:
            lang = (True==(editor.lang in languages)) and editor.lang or 'en'
            here = self.context.absolute_url()
            params = {
                'language': lang,
                'apikey': editor.key,
                'authenticator': editor.authenticator,
                'apisecret': editor.secret,
                'callback': '%s/%s' % (here, urllib.quote('@@externalimageeditor_save')),
                'image_url': self.image_url,
                'image_preview': self.image_preview_url,
            }
            params['editor'] = AVIARY_ED % params
            getMultiAdapter((self.context, self.request), i.IEditSessionHelper).register_edit_session(service)
            return self.template(**params)
        else:
            ret = 'Invalid edit proxy request!'
            logger.info(ret)
            url = context_url
            if IATImage.providedBy(self.context):
                url += "/view"
            self.request.response.redirect(url)
        return ret

    @property
    def image_url(self):
        here = self.context.absolute_url()
        return here

    @property
    def image_preview_url(self):
        return self.image_url  + '_preview'


# vim:set et sts=4 ts=4 tw=80:
