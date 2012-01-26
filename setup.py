import os, sys

from setuptools import setup, find_packages

version = u'1.0'

def read(*rnames):
    return open(
        os.path.join('.', *rnames)
    ).read()

long_description = "\n\n".join(
    [read('README.txt'),
     read('docs', 'INSTALL.txt'),
     read('docs', 'HISTORY.txt'),
    ]
)

classifiers = [
    "Programming Language :: Python",
    "Topic :: Software Development",]

name = 'collective.externalimageeditor'
setup(
    name=name,
    namespace_packages=[         'collective',
         'collective.externalimageeditor',],
    version=version,
    description='Project collective.externalimageeditor externalimageeditor product',
    long_description=long_description,
    classifiers=classifiers,
    keywords='plone image editor',
    author='kiorky',
    author_email='kiorky@cryptelium.net',
    url='http://www.makina-corpus.com/',
    license='GPL',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    install_requires=[
        'setuptools',
        'z3c.autoinclude',
        # with_ploneproduct_dexterity
        'z3c.blobfile',
        'plone.app.dexterity',
        # with_ploneproduct_pz3cform
        'five.grok',
        'plone.app.z3cform',
        'plone.directives.form',
        'plone.z3cform',
        # -*- Extra requirements: -*-
        'collective.testcaselayer',
    ],
    entry_points = {
        'z3c.autoinclude.plugin': [
            'target = plone',
        ],

    },
)
# vim:set ft=python:
