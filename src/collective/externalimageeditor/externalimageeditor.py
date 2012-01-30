import logging

from zope.i18nmessageid import MessageFactory
MessageFactory = collectiveexternalimageeditorMessageFactory = MessageFactory('collective.externalimageeditor') 
logger = logging.getLogger('collective.externalimageeditor')
def initialize(context):
    """Initializer called when used as a Zope 2 product."""
