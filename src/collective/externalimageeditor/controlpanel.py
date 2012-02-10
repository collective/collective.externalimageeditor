from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from collective.externalimageeditor import MessageFactory as _
from collective.externalimageeditor.interfaces import IExternalimageeditorConfiguration
from plone.z3cform import layout

class PanelForm(RegistryEditForm):
    schema = IExternalimageeditorConfiguration

ControlPanelView = layout.wrap_form(PanelForm, ControlPanelFormWrapper)
ControlPanelView.label = _(u"Externalimagerditor settings")

