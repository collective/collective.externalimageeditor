from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from zope import interface, schema
from plone.theme.interfaces import IDefaultPloneLayer
from Products.CMFCore.utils import getToolByName

from collective.externalimageeditor import MessageFactory as _

class IMyPortalUser(IPropertiedUser):
    """ Marker interface implemented by users in my portal. """

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer and a plone skin marker.
    """

class ILayer(interface.Interface):
    """Marker interface that defines a Zope 3 browser layer.
    """
class IExternalimageeditorConfiguration(interface.Interface):
    has_pixlr = schema.Bool(
        title=_(u"Pixlr"),
        description=_(u"Activate support for editing on Pixlr."),
        default=False)

    has_fotoflexer = schema.Bool(
        title=_(u"Fotoflexer"),
        description=_(u"Activate support for editing on Fotoflexer."),
        default=False)

    has_aviary = schema.Bool(
        title=_(u"Aviary"),
        description=_(u"Activate support for editing on Aviary."),
        default=False)

    aviary_key = schema.ASCIILine(
        title=_(u"Aviary key"),
        description=_(u"Activate support for editing on Aviary (http://www.aviary.com/web-key)."),
        required = False,
        default="")

    aviary_secret = schema.ASCIILine(
        title=_(u"Aviary secret"),
        description=_(u"Relevant secret for aviary."),
        required = False,
        default="")

class IExternalImageEditor(interface.Interface):
    link_infos = interface.Attribute("link_infos", "Image tuple icon & title")
    enabled = interface.Attribute("enabled", "Return true if this service is enabled")
    edit_url = interface.Attribute("edit_url", "edit_url proxy")
    service_edit_url = interface.Attribute("edit_url", "edit_url real service")


class IEditSessionHelper(interface.Interface):
    """Register in annotations an information directory for the cotext:

        {
            (serviceName, userid): {'time': datetime.datetime}
        }

    """
    def register_edit_session(service, user=None):
        """Register an image marked as edited on an external service at a specified time."""

    def remove_edit_session(service, user=None):
        """Remove an image marked as edited on an external service."""

    def is_edited_by(service, user):
        """True if the user has edited this image somewhere"""


class BaseAdapter(object):

    def __init__(self, context=None, request=None):
        self.context = context
        self.request = request

    @property
    def portal_url(self):
        return getToolByName(self.context, 'portal_url')


