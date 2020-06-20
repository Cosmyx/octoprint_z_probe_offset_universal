"use strict";

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

var ZProbeOffsetViewModel =
/*#__PURE__*/
function () {
  function ZProbeOffsetViewModel(parameters) {
    _classCallCheck(this, ZProbeOffsetViewModel);

    this.control = parameters[0];
    this.offsetVal = {
      actual: ko.observable(undefined),
      edited: ko.observable(undefined)
    };
    this.error = {
      offset: ko.observable(undefined),
      probe: ko.observable(undefined)
    };
    this.template = $('#generic_plugin_z_probe_offset');
    this.control.z_probe_offset = this;
    $("#control-jog-general").append(this.template.html());
  }

  _createClass(ZProbeOffsetViewModel, [{
    key: "onBeforeBinding",
    value: function onBeforeBinding() {
      var _this = this;

      this.request('GET', null, null, function (data) {
        _this.error.probe(data.printer_cap.z_probe == 0 ? true : false);

        _this.offsetVal.actual(data.z_offset);

        _this.offsetVal.edited(data.z_offset);
      });
    }
  }, {
    key: "onDataUpdaterPluginMessage",
    value: function onDataUpdaterPluginMessage(plugin, data) {
      if (plugin != 'z_probe_offset') return;
      if (data.type == 'z_offset') this.offsetVal.actual(data.msg);else if (data.type == 'printer_cap') {
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
      OctoPrint.control.sendGcode("M851Z".concat(this.offsetVal.edited()));
      OctoPrint.control.sendGcode('M500');
    }
  }, {
    key: "submit_enabled",
    value: function submit_enabled() {
      if (!this.control.isOperational() || this.control.isPrinting()) return false;
      if (!parseFloat(this.offsetVal.edited())) return false;
      if (this.offsetVal.edited() == this.offsetVal.actual()) return false;
      return true;
    }
  }, {
    key: "request",
    value: function request(type, command, args, successCb) {
      var data = function data() {
        if (command && args) return JSON.stringify({
          command: command,
          args: args
        });
        if (command) return JSON.stringify({
          command: command
        });
      };

      $.ajax({
        url: "/api".concat(PLUGIN_BASEURL, "z_probe_offset"),
        type: type,
        dataType: 'json',
        data: data(),
        contentType: 'application/json; charset=UTF-8',
        success: function success(data) {
          if (successCb) successCb(data);
        }
      });
    }
  }]);

  return ZProbeOffsetViewModel;
}();

OCTOPRINT_VIEWMODELS.push({
  construct: ZProbeOffsetViewModel,
  dependencies: ['controlViewModel']
});
