# coding=utf-8
''' Plugin setup file '''

from setuptools import setup
plugin_identifier = 'z_probe_offset'
plugin_package = 'octoprint_z_probe_offset'
plugin_name = 'Z Probe Offset Control'
plugin_version = '0.4'
plugin_description = ('Control the z probe offset on marlin based printers.')
plugin_author = 'razer'
plugin_author_email = 'razerraz@free.fr'
plugin_url = 'https://framagit.org/razer/octoprint_z_probe_offset'
plugin_license = 'AGPLv3'
plugin_requires = []
plugin_additional_data = []
plugin_additional_packages = []
plugin_ignored_packages = []
additional_setup_parameters = {}

try:
    import octoprint_setuptools
except ImportError:
    print('Could not import OctoPrint\'s setuptools, are you sure you are ' +
          'running that under the same python installation that OctoPrint ' +
          'is installed under?')
    import sys
    sys.exit(-1)

setup_parameters = octoprint_setuptools.create_plugin_setup_parameters(
    identifier=plugin_identifier,
    package=plugin_package,
    name=plugin_name,
    version=plugin_version,
    description=plugin_description,
    author=plugin_author,
    mail=plugin_author_email,
    url=plugin_url,
    license=plugin_license,
    requires=plugin_requires,
    additional_packages=plugin_additional_packages,
    ignored_packages=plugin_ignored_packages,
    additional_data=plugin_additional_data
)

if additional_setup_parameters:
    # pylint: disable=E0401
    from octoprint.util import dict_merge
    setup_parameters = dict_merge(setup_parameters, additional_setup_parameters)

setup(**setup_parameters)
