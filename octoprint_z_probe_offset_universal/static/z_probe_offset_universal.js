"use strict";

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }
function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

var ZProbeOffsetUniversalViewModel = /*#__PURE__*/function () {

  function ZProbeOffsetUniversalViewModel(parameters) {
    _classCallCheck(this, ZProbeOffsetUniversalViewModel);
    this.control = parameters[0];
    this.offsetVal = {
      actual: ko.observable(undefined),
      edited: ko.observable(undefined)
    };
    this.error = {
      offset: ko.observable(undefined),
      probe: ko.observable(undefined)
    };
    this.template = $('#generic_plugin_z_probe_offset_universal');
    this.control.z_probe_offset_universal = this;
    $("#control-jog-general").append(this.template.html());
  }

  _createClass(ZProbeOffsetUniversalViewModel, [{
      key: "onBeforeBinding",
      value: function onBeforeBinding() {
        OctoPrint.simpleApiCommand('z_probe_offset_universal', 'get', {}).done(function (data) {
          this.error.probe(data.printer_cap.z_probe == 0 ? true : false);
          this.offsetVal.actual(data.z_offset);
          this.offsetVal.edited(data.z_offset);
        })
      }
    }, {
      key: "onDataUpdaterPluginMessage",
      value: function onDataUpdaterPluginMessage(plugin, data) {
        if (plugin != 'z_probe_offset_universal') return;
        if (data.type == 'z_offset')
          this.offsetVal.actual(data.msg);
        else if (data.type == 'printer_cap') {
          var printer_cap = JSON.parse(data.msg);
          this.error.probe(printer_cap.z_probe == 1 ? false : true);
        } else if (data.type == 'offset_error') {
          this.error.offset(data.msg);
        }
      }
    }, {
      key: "increase",
      value: function increase(inc) {
        if (this.error.offset()) this.error.offset(undefined);
        this.offsetVal.edited(Math.round((parseFloat(this.offsetVal.edited()) + (inc ? +.05 : -.05)) * 100) / 100);
      }
    }, {
      key: "set",
      value: function set() {
        if (!this.submit_enabled()) return;
        OctoPrint.simpleApiCommand('z_probe_offset_universal', 'set', {
          offset: this.offsetVal.edited()
        });
      }
    }, {
      key: "submit_enabled",
      value: function submit_enabled() {
        if (!this.control.isOperational() || this.control.isPrinting()) return false;
        if (isNaN(parseFloat(this.offsetVal.edited()))) return false;
        if (this.offsetVal.edited() == this.offsetVal.actual()) return false;
        return true;
      }
    },
  ]);

  return ZProbeOffsetUniversalViewModel;
}();

OCTOPRINT_VIEWMODELS.push({
  construct: ZProbeOffsetUniversalViewModel,
  dependencies: ['controlViewModel']
});
