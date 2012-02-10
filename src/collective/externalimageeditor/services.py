#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'

import time
from Acquisition import aq_inner
from StringIO import StringIO
from datetime import datetime

import urllib
import hmac
try:
    from hashlib import sha1 as sha
except ImportError:
    import sha


from zope import interface
from zope.component import getUtility
from zope.component import getAdapter, getMultiAdapter, queryMultiAdapter
from zope.event import notify

from Acquisition import aq_inner, aq_parent


from AccessControl import getSecurityManager
from Products.ATContentTypes.interfaces.image import IATImage
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.event import ObjectEditedEvent
from Products.ATContentTypes.interfaces.interfaces import IATContentType
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.linkintegrity.interfaces import IOFSImage

from plone.registry.interfaces import IRegistry
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import check

from collective.externalimageeditor import interfaces as i
from collective.externalimageeditor import MessageFactory as _, logger

class DownloadError(Exception):
    """Download failed"""


def _getUserName():
    user=getSecurityManager().getUser()
    if user is None:
        return "Anonymous User"
    return user.getUserName()

class ExternalImageEditor(i.BaseAdapter):
    interface.implements(i.IExternalImageEditor)
    ico = 'icofx_12.png'

    @property
    def authenticator(self):
        manager = getUtility(IKeyManager)
        secret = manager.secret()
        user = _getUserName()
        auth = hmac.new(secret, user, sha).hexdigest()
        return auth

    @property
    def settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            i.IExternalimageeditorConfiguration)
        return settings

    @property
    def lang(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        current_language = portal_state.language()
        return current_language

    @property
    def service_enabled(self):
        return getattr(self.settings, 'has_%s'%self.name, False)

    @property
    def key(self):
        return getattr(self.settings, '%s_key'%self.name, False)

    @property
    def secret(self):
        return getattr(self.settings, '%s_secret'%self.name, False)

    def save(self):
        """Save the image"""
        context, request, form = self.context, self.request, self.request.form
        check(self.request) # raise an error if not authenficated
        if not 'image' in form:
            raise Exception('invalid request')
        data = self.fetch(form['image'])
        if not data:
            raise Exception("image download fails")
        if IATImage.providedBy(self.context):
            self.at_store(self.context, data)
        parent = aq_parent(self.context)
        if IATContentType.providedBy(parent):
            self.at_store(parent, data, self.context.id())

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
        return self.service_enabled

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

    def at_store(self, context, image_infos, field_name='image'):
        """Do the job to fetch image and update the context with it"""
        sio = StringIO()
        sio.write(image_infos['data'])
        field = context.getField(field_name) or context.getPrimaryField()
        field.set(
            context,
            image_infos['data'],
            mimetype=image_infos['mimetype'],
            filename=image_infos['filename'],
            refresh_exif=False
        )
        notify(ObjectEditedEvent(context))
        IStatusMessage(self.request).addStatusMessage(_('Your image has been updated.'), 'info')

class IPixlrEditor(i.IExternalImageEditor):
    """Marker interface for pixlr adapter."""


class IAviaryEditor(i.IExternalImageEditor):
    """Marker interface for aviary adapter."""

class IFotoFlexerEditor(i.IExternalImageEditor):
    """Marker interface for fotoflexer adapter."""

class PixlrEditor(ExternalImageEditor):
    interface.implements(IPixlrEditor)
    name = 'pixlr'
    ico = 'pixlr_12.png'

    @property
    def service_edit_url(self):
        context, thisurl, url = self.context, '', ''
        if (IATImage.providedBy(self.context)
            or IOFSImage.providedBy(self.context)):
            thisurl = self.context.absolute_url()
            surl = 'http://www.pixlr.com/editor'
            params = {
                'image': thisurl,
                "locktarget": "true",
                "target": "%s/@@externalimageeditor_save?service=%s&_authenticator=%s" % (thisurl, self.name, self.authenticator),
            }
            url = '%s?%s' % (surl, urllib.urlencode(params))
        return url

class AviaryEditor(ExternalImageEditor):
    interface.implements(IAviaryEditor)
    name = 'aviary'
    ico = 'aviary_12.png'
    @property
    def edit_url(self):
        return  "%s/@@%s" % (
            self.context.absolute_url(),
            'externalimageeditor_aviary')

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

    @property
    def enabled(self):
        return (self.service_enabled
                and self.key
                and self.secret)

class FotoFlexerEditor(ExternalImageEditor):
    interface.implements(IFotoFlexerEditor)
    name = 'fotoflexer'
    ico = 'fotoflexer_12.gif'
    langs = {
        'da': 'da-DK',
        'de': 'de-DE',
        'en': 'en-US',
        'es': 'es-LA',
        'fi': 'fi-FI',
        'fr': 'fr-FR',
        'it': 'it-IT',
        'ja': 'ja-JP',
        'ko': 'ko-KR',
        'nb': 'nb-NO',
        'nl': 'nl-NL',
        'pl': 'pl-PL',
        'pt': 'pt-PT',
        'ru': 'ru-RU',
        'sv': 'sv-SE',
        'tu': 'tu-TR',
        'vi': 'vi-VN',
        'zh': 'zh-TW',
    }

    @property
    def service_edit_url(self):
        context, thisurl, url = self.context, '', ''
        langk = (True==(self.lang in self.langs)) and self.lang or 'en'
        lang = self.langs[langk]
        if (IATImage.providedBy(self.context)
            or IOFSImage.providedBy(self.context)):
            thisurl = self.context.absolute_url()
            surl = 'http://fotoflexer.com/API/API_Loader_v1_01.php'
            params = {
                'ff_image_url': thisurl,
                'ff_cancel_url': "%s/view" % thisurl,
                'ff_lang' : lang,
                'ff_callback_url': "%s/@@externalimageeditor_save?service=%s&_authenticator=%s" % (thisurl, self.name, self.authenticator),
            }
            url = '%s?%s' % (surl, urllib.urlencode(params))
        return url

# vim:set et sts=4 ts=4 tw=80:
