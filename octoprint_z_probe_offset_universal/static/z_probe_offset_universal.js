"use strict";

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

var ZProbeOffsetUniversalViewModel = /*#__PURE__*/function () {
  function ZProbeOffsetUniversalViewModel(parameters) {
    _classCallCheck(this, ZProbeOffsetUniversalViewModel);

    this.control = parameters[0];
    this.commands = {
      set: '',
      save: ''
    };
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
      var _this = this;

      this.request('GET', null, null, function (data) {
        _this.error.probe(data.printer_cap.z_probe == 0 ? true : false);

        _this.commands.set = data.set_command_z;
        _this.commands.save = data.save_command;

        _this.offsetVal.actual(data.z_offset);

        _this.offsetVal.edited(data.z_offset);
      });
    }
  }, {
    key: "onDataUpdaterPluginMessage",
    value: function onDataUpdaterPluginMessage(plugin, data) {
      if (plugin != 'z_probe_offset_universal') return;
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
      var _this2 = this;

      if (!this.submit_enabled()) return;
      OctoPrint.control.sendGcode(this.commands.set + this.offsetVal.edited());
      setTimeout(function () {
        OctoPrint.control.sendGcode(_this2.commands.save);
      }, 1000);
    }
  }, {
    key: "submit_enabled",
    value: function submit_enabled() {
      if (!this.control.isOperational() || this.control.isPrinting()) return false;
      if (isNaN(parseFloat(this.offsetVal.edited()))) return false;
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
        url: "/api".concat(PLUGIN_BASEURL, "z_probe_offset_universal"),
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

  return ZProbeOffsetUniversalViewModel;
}();

OCTOPRINT_VIEWMODELS.push({
  construct: ZProbeOffsetUniversalViewModel,
  dependencies: ['controlViewModel']
});
