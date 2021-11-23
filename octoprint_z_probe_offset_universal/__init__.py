from __future__ import absolute_import

import json
import threading
import flask
import requests
from requests.exceptions import ConnectionError as ConnErr, ConnectTimeout
import octoprint.plugin  # pylint: disable=import-error
from octoprint.events import Events  # pylint: disable=import-error

# GIT_PROJECT_ID = '63729'
# GIT_NAME = 'Octoprint_Z_probe_offset'
# GIT_USER = 'razer'

# GIT_URL = 'https://framagit.org'
# GIT_RELEASES = GIT_URL + '/api/v4/projects/' + GIT_PROJECT_ID + '/releases'
# GIT_ARCHIVES = GIT_URL + '/' + GIT_USER + '/' + GIT_NAME + '/-/archive'

# class _VersionCheck:
#     @classmethod
#     def get_remote_version(cls):
#         try:
#             req = requests.get(GIT_RELEASES, timeout=5)
#         except (ConnErr, ConnectTimeout):
#             return None
#         response = req.json()
#         if not response or not isinstance(response, list):
#             return None
#         tag_map = map(lambda r: r['tag_name'], response)
#         release_map = filter(lambda v: v.replace('.', '').isdigit(), tag_map)
#         release_map = list(map(float, release_map))
#         release_map.sort(reverse=True)
#         if not release_map:
#             return None
#         return str(release_map[0])

#     @classmethod
#     def get_latest(cls, target, check, full_data=False, online=True):
#         # pylint: disable=unused-argument
#         current_version = check.get('current', '1.0.0')
#         remote_version = current_version
#         if online:
#             remote_version = cls.get_remote_version() or current_version
#         info = dict(local=dict(name=current_version, value=current_version),
#                     remote=dict(name=remote_version, value=remote_version))
#         return info, remote_version == current_version


# pylint: disable=attribute-defined-outside-init
class Z_probe_offset_universal_plugin(octoprint.plugin.AssetPlugin,
                            octoprint.plugin.EventHandlerPlugin,
                            octoprint.plugin.SimpleApiPlugin,
                            octoprint.plugin.TemplatePlugin):

    def initialize(self):
        self._version = '0.6'
        self._plugin_version = self._version
        self.z_offset = None
        self.printer_cap = {'eeprom': None, 'z_probe': None}
        self.firmware_name = 'marlin'
        self.get_command = 'M851'
        self.set_command = 'M851'
        self.set_command_z = self.set_command + 'Z'
        self.save_command = 'M500'
        self.prusa_zoffset_following = False

    def get_update_information(self):
        return dict(Z_probe_offset_universal=dict(
            displayName='Z Probe Offset Universal Control',
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
        return flask.jsonify(printer_cap=self.printer_cap,
                             z_offset=self.z_offset)

    def on_event(self, event, payload):
        if event == 'Disconnected':
            self.printer_cap = {'eeprom': None, 'z_probe': None}
            self._send_message('printer_cap', json.dumps(self.printer_cap))
        # elif event == 'Connected':
        elif event == Events.FIRMWARE_DATA:
            self._logger.debug('Get firmware data: %s - %s',
                               payload.get('name'), payload.get('data'))
            firmware_name = payload.get('name')
            if firmware_name:
                self.firmware_name = firmware_name.lower()
            if 'klipper' in self.firmware_name:
                self.get_command = 'GET_POSITION'
                self.set_command = 'SET_GCODE_OFFSET'
                self.set_command_z = self.set_command + ' Z='
                self.save_command = 'SAVE_CONFIG'
            self._printer.commands([self.get_command])

    def set_z_offset_from_printer_response(self, offset):
        offset = offset.strip().replace(' ', '').replace('"', '')
        if not offset:
            self._logger.warning('Offset part is empty !')
            return
        if not offset.replace('-', '', 1).replace('.', '', 1).isdigit():
            self._logger.warning('Unable to extract Z offset from "%s"', offset)
            return
        self._logger.info('Z probe offset is now %s', offset)
        if not self.printer_cap['z_probe']:
            self._logger.warning('Set printer\'s z probe cap as enabled, M115 '
                                 + 'firmware response supposed buggy')
            self.printer_cap['z_probe'] = 1
            self._send_message('printer_cap', json.dumps(self.printer_cap))
        self.z_offset = float(offset)
        self._send_message('z_offset', self.z_offset)

    def set_z_offset_from_gcode(self, line):
        offset_map = line.lower().replace(self.set_command.lower(), '').replace(':', '').split()
        z_part = list(filter(lambda v: v.startswith('z'), offset_map))
        if not z_part:
            self._logger.warning('Bad %s response: %s', self.get_command, line)
            return
        self.set_z_offset_from_printer_response(z_part[0][1:])

    def on_printer_gcode_sent(self, comm, phase, cmd, cmd_type, gcode, *args,
                              **kwargs):
        # pylint: disable=too-many-arguments, unused-argument
        if gcode and self.set_command.lower() in gcode.lower() and cmd.replace(gcode, ''):
            self._logger.debug('Setting z offset from user command %s', cmd)
            self.set_z_offset_from_gcode(cmd.replace(gcode, ''))

    def populate_printer_cap(self, line):
        cap = list(filter(lambda c: c in line, self.printer_cap))
        if not cap:
            return None
        cap = cap[0]
        self.printer_cap[cap] = int(line.split(':')[-1])
        self._logger.info('Printer_cap[%s]:%s', cap, line.split(':')[-1])
        return True

    def on_printer_gcode_received(self, comm, line, *args, **kwargs):
        # pylint: disable=unused-argument
        if not line:
            return line
        line_lower = line.lower().strip()
        if self.prusa_zoffset_following:
            self.prusa_zoffset_following = False
            self._logger.debug('Z offset value (prusa): %s', line_lower)
            self.set_z_offset_from_printer_response(line_lower)
            return line
        if len(line_lower) < 3:
            return line
        if 'cap:' in line_lower:
            cap_populated = self.populate_printer_cap(line_lower)
            if cap_populated:
                self._send_message('printer_cap', json.dumps(self.printer_cap))
        elif 'zprobe_zoffset' in line_lower:
            self._logger.debug('CR3D M851 echo: %s', line_lower)
            self.set_z_offset_from_printer_response(line_lower.split('=')[-1])
        elif 'probe z offset:' in line_lower:
            self._logger.debug('Marlin 1.x M851 echo: %s', line_lower)
            self.set_z_offset_from_printer_response(line_lower.split(':')[-1])
        elif line_lower.endswith('z offset') and 'prusa' in self.firmware_name:
            self._logger.debug('Prusa M851 echo: z offset may follow')
            self.prusa_zoffset_following = True
        elif 'z offset' in line_lower:
            self._logger.debug(
                'CR3D variant echo to M851Z[VALUE]: %s', line_lower)
            self.set_z_offset_from_printer_response(line_lower.split(' ')[-1])
        elif 'm851' in line_lower or 'probe offset ' in line_lower:
            self._logger.debug('Marlin 2.x M851 echo: %s', line_lower)
            self.set_z_offset_from_gcode(line_lower.replace('probe offset', ''))
        elif '// gcode: ' in line_lower and 'klipper' in self.firmware_name:
            # Send: GET_POSITION
            # Recv: // mcu: stepper_x:0 stepper_y:0 stepper_z:0
            # Recv: // stepper: stepper_x:0.000000 stepper_y:0.000000 stepper_z:0.000000
            # Recv: // kinematic: X:0.000000 Y:0.000000 Z:0.000000
            # Recv: // toolhead: X:0.000000 Y:0.000000 Z:0.000000 E:200.000000
            # Recv: // gcode: X:0.000000 Y:0.000000 Z:1.177979 E:200.000000
            # Recv: // gcode base: X:0.000000 Y:0.000000 Z:0.000000 E:0.000000
            # Recv: // gcode homing: X:0.000000 Y:0.000000 Z:0.000000
            # Recv: ok
            self._logger.debug('Klipper GET_POSITION echo: %s', line_lower)
            self.set_z_offset_from_gcode(line_lower.split(' ')[-2])
        elif '?z out of range' in line_lower:
            self._logger.error('Setting z offset: %s', line_lower)
            self._send_message('offset_error', line_lower.replace('?', ''))
            self._printer.commands([self.get_command])
        return line

    def _send_message(self, msg_type, message):
        self._plugin_manager.send_plugin_message(
            self._identifier,
            dict(type=msg_type, msg=message))

__plugin_name__ = 'Z Probe Offset Universal'
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
    # pylint: disable=global-variable-undefined
    global __plugin_implementation__
    __plugin_implementation__ = Z_probe_offset_universal_plugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        'octoprint.plugin.softwareupdate.check_config':
        __plugin_implementation__.get_update_information,
        'octoprint.comm.protocol.gcode.received':
        __plugin_implementation__.on_printer_gcode_received,
        'octoprint.comm.protocol.gcode.sent':
        __plugin_implementation__.on_printer_gcode_sent,
    }
