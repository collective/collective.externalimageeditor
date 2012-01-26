collective.externalimageeditor Installation
=================================================================================

To install collective.externalimageeditor into the global Python environment (or a workingenv),
using a traditional Zope 2 instance, you can do this:

 * When you're reading this you have probably already run ::

   ``easy_install collective.externalimageeditor``.

   Find out how to install setuptools (and EasyInstall) here: http://peak.telecommunity.com/DevCenter/EasyInstall

 * If you are using Zope 2.9 (not 2.10), get `pythonproducts`_ and install it
   via::

       python setup.py install --home /path/to/instance

   into your Zope instance.

 * Create a file called ``collective.externalimageeditor-configure.zcml`` in the
   ``/path/to/instance/etc/package-includes`` directory.  The file
   should only contain this::

       <include package="collective.externalimageeditor" />

.. _pythonproducts: http://plone.org/products/pythonproducts


Alternatively, if you are using zc.buildout and the plone.recipe.zope2instance
recipe to manage your project, you can do this:

 * Add ``collective.externalimageeditor`` to the list of eggs to install, e.g.::

    [buildout]
    ...
    eggs =
        ...
        collective.externalimageeditor

 * Tell the plone.recipe.zope2instance recipe to install a ZCML slug::

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zcml =
        collective.externalimageeditor

 * Re-run buildout, e.g. with::

    $ ./bin/buildout

You can skip the ZCML slug if you are going to explicitly include the package
from another package's configure.zcml file.
