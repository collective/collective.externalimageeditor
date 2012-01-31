#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'

import datetime
from zope import interface
from zope.annotation.interfaces import IAttributeAnnotatable, IAnnotations

from persistent.dict import PersistentDict

from Products.CMFCore.utils import getToolByName

from collective.externalimageeditor import interfaces as i

KEY = 'COLLECTIVEEXTERNALIMAGE_ANNOTATIONS'


class AnonymousException(Exception):
    """User is not loggued in"""


class EditSessionHelper(i.BaseAdapter):
    """See interface"""
    interface.implements(i.IEditSessionHelper)

    def get_user(self):
        """ Return the username of the current user, or None.
        """
        username, mt = None, getToolByName(self.context, 'portal_membership')
        if not mt.isAnonymousUser(): # the user has logged in
            member = mt.getAuthenticatedMember()
            username = member.getMemberId()
        return username

    def want_user(self, user=None):
        if not user:
            user = self.get_user()
            if user is None:
                raise AnonymousException('invalid')
        return user

    @property
    def registry(self):
        context = self.context
        if not IAttributeAnnotatable.providedBy(context):
            interface.alsoProvides(self.context, IAttributeAnnotatable)
        annotations = IAnnotations(self.context)
        if not KEY in annotations:
            annotations[KEY] = PersistentDict()
        return annotations[KEY]

    def register_edit_session(self, service, user=None):
        user = self.want_user(user)
        if not self.is_edited_by(service, user):
            self.registry[(service, user)] = datetime.datetime.now()

    def remove_edit_session(self, service, user=None):
        user = self.want_user(user)
        if self.is_edited_by(service, user):
            del self.registry[(service, user)]

    def is_edited_by(self, service, user=None):
        user = self.want_user(user)
        return (service, user) in self.registry
# vim:set et sts=4 ts=4 tw=80:
