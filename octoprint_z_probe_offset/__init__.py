from __future__ import absolute_import

import json
import threading
import flask
import requests
from requests.exceptions import ConnectionError as ConnErr, ConnectTimeout
import octoprint.plugin  # pylint: disable=import-error
from octoprint.events import Events  # pylint: disable=import-error

GIT_PROJECT_ID = '63729'
GIT_NAME = 'Octoprint_Z_probe_offset'
GIT_USER = 'razer'

GIT_URL = 'https://framagit.org'
GIT_RELEASES = GIT_URL + '/api/v4/projects/' + GIT_PROJECT_ID + '/releases'
GIT_ARCHIVES = GIT_URL + '/' + GIT_USER + '/' + GIT_NAME + '/-/archive'

class _VersionCheck:
    @classmethod
    def get_remote_version(cls):
        try:
            req = requests.get(GIT_RELEASES, timeout=5)
        except (ConnErr, ConnectTimeout):
            return None
        response = req.json()
        if not response or not isinstance(response, list):
            return None
        remote_version = response[0]['tag_name']
        if not remote_version.replace('.', '').isdigit():
            return None
        return remote_version

    @classmethod
    def get_latest(cls, target, check, full_data=False, online=True):
        # pylint: disable=unused-argument
        current_version = check.get('current', '1.0.0')
        remote_version = current_version
        if online:
            remote_version = cls.get_remote_version() or current_version
        info = dict(local=dict(name=current_version, value=current_version),
                    remote=dict(name=remote_version, value=remote_version))
        return info, remote_version == current_version


# pylint: disable=attribute-defined-outside-init
class Z_probe_offset_plugin(octoprint.plugin.AssetPlugin,
                            octoprint.plugin.EventHandlerPlugin,
                            octoprint.plugin.SimpleApiPlugin,
                            octoprint.plugin.TemplatePlugin):

    def initialize(self):
        self._version = '0.1'
        self._plugin_version = self._version
        self.z_offset = None
        self.printer_cap = {'eeprom': None, 'z_probe': None}

    def get_update_information(self):
        return dict(Z_probe_offset=dict(
            displayName='Z Probe Offset Control',
            displayVersion=self._plugin_version,
            current=self._plugin_version,
            type='python_checker',
            python_checker=_VersionCheck,
            pip=GIT_ARCHIVES + '/{target}/%s-{target}.zip' % GIT_NAME))

    def get_template_configs(self):
        return [dict(type='generic', template='%s.jinja2' % self._identifier)]

    def get_assets(self):
        return dict(js=['%s.js' % self._identifier])

    def on_api_get(self, unused_request):
        self._logger.info('ON API GET')
        return flask.jsonify(printer_cap=self.printer_cap,
                             z_offset=self.z_offset)

    def on_event(self, event, unused_payload):
        if event == 'Disconnected':
            self.printer_cap = {'eeprom': None, 'z_probe': None}
            self._send_message('printer_cap', json.dumps(self.printer_cap))
        if event == 'Connected':
            self._printer.commands(['M851'])

    def set_z_offset_from_gcode(self, line):
        offset_map = line.lower().replace('m851', '').split()
        z_part = list(filter(lambda v: v.startswith('z'), offset_map))
        if not z_part:
            self._logger.warning('Bad M851 response: %s', line)
            return
        z_offset = z_part[0][1:]
        if not z_offset.replace('.', '', 1).replace('-', '', 1).isdigit():
            self._logger.warning('Unable to extract Z offset from "%s"', line)
            return
        self.z_offset = float(z_offset)
        self._send_message('z_offset', float(z_offset))
        self._logger.info('Z probe offset is now %s', z_offset)

    def on_printer_gcode_sent(self, comm, phase, cmd, cmd_type, gcode, *args,
                              subcode=None, tags=None, **kwargs):
        # pylint: disable=too-many-arguments, unused-argument
        if gcode and 'm851' in gcode.lower() and cmd.replace(gcode, ''):
            self._logger.debug('Setting z probe offset from user command %s',
                               cmd)
            self.set_z_offset_from_gcode(cmd.replace(gcode, ''))

    def populate_printer_cap(self, line):
        cap = list(filter(lambda c: c in line.lower(), self.printer_cap))
        if not cap:
            return None
        cap = cap[0]
        self.printer_cap[cap] = int(line.split(':')[-1])
        self._logger.info('Printer_cap[%s]:%s', cap, line.split(':')[-1])
        return True

    def on_printer_gcode_received(self, comm, line, *args, **kwargs):
        # pylint: disable=unused-argument
        if len(line) < 3:
            return line
        line_lower = line.lower()
        if 'cap:' in line_lower:
            cap_populated = self.populate_printer_cap(line)
            if cap_populated:
                self._send_message('printer_cap', json.dumps(self.printer_cap))
        elif 'probe z offset:' in line_lower:
            # Marlin 1.x
            self._logger.debug('Using printer\'s z probe offset from %s', line)
            self.z_offset = float(line.split(':')[-1])
        elif 'm851' in line_lower or 'probe offset ' in line_lower:
            # Marlin 2.x
            self._logger.debug('Using printer\'s z probe offset from %s', line)
            self.set_z_offset_from_gcode(line.replace('probe offset', ''))
            return line
        elif '?z out of range' in line_lower:
            self._logger.error('Setting z offset: %s', line)
            self._send_message('offset_error', line.replace('?', ''))
            self._printer.commands(['M851'])
        return line

    def _send_message(self, msg_type, message):
        self._plugin_manager.send_plugin_message(
            self._identifier,
            dict(type=msg_type, msg=message))

__plugin_name__ = 'Z Probe Offset'
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
    # pylint: disable=global-variable-undefined
    global __plugin_implementation__
    __plugin_implementation__ = Z_probe_offset_plugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        'octoprint.plugin.softwareupdate.check_config':
        __plugin_implementation__.get_update_information,
        'octoprint.comm.protocol.gcode.received':
        __plugin_implementation__.on_printer_gcode_received,
        'octoprint.comm.protocol.gcode.sent':
        __plugin_implementation__.on_printer_gcode_sent,
    }
