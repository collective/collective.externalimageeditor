#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'

import urllib
from zope import component, interface
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interfaces.image import IATImage
from plone.registry.interfaces import IRegistry
from collective.externalimageeditor import interfaces as i
from collective.externalimageeditor.externalimageeditor import logger

from zope.component import getAdapter, getMultiAdapter

class ISave(interface.Interface):
    """Marker interface for ISave"""

class IEdit(interface.Interface):
    """Marker interface for IEdit"""
    def http_get_edit():
        """Use the http get facility to edit an online image...
        You must be warned it doesn't work with localhost
        """

class Save(BrowserView):
    """Save an image after being edited on a webservice"""
    interface.implements(ISave)
    def __call__(self, *args):
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
                editor.save()
        if invalid:
            logger.info('Invalid edit proxy request!')
        if IATImage.providedBy(self.context):
            context_url += "/view"
        self.request.response.redirect(context_url)
        return '' 

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
        if editor is not None:
            url = editor.service_edit_url
            getMultiAdapter((self.context, self.request), i.IEditSessionHelper).register_edit_session(service)
        else:
            logger.info('Invalid edit proxy request!')
            url = context_url
            if IATImage.providedBy(self.context):
                url += "/view"
        self.request.response.redirect(url)
        return ''

# vim:set et sts=4 ts=4 tw=80:
