class ZProbeOffsetUniversalViewModel {
  constructor (parameters) {
    this.control = parameters[0]
    this.commands = {set: '', save: ''}
    this.offsetVal = {actual: ko.observable(undefined), edited: ko.observable(undefined)}
    this.error = {offset: ko.observable(undefined), probe: ko.observable(undefined)}
    this.template = $('#generic_plugin_z_probe_offset_universal')
    this.control.z_probe_offset_universal = this
    $("#control-jog-general").append(this.template.html())
  }

  onBeforeBinding() {
    this.request('GET', null, null, (data) => {
      this.error.probe(data.printer_cap.z_probe == 0 ? true : false)
      this.commands.set = data.set_command_z
      this.commands.save = data.save_command
      this.offsetVal.actual(data.z_offset)
      this.offsetVal.edited(data.z_offset)
    })
  }


  onDataUpdaterPluginMessage(plugin, data) {
    if (plugin != 'z_probe_offset_universal') return
    if (data.type == 'z_offset')
      this.offsetVal.actual(data.msg)
    else if (data.type == 'printer_cap') {
      let printer_cap = JSON.parse(data.msg)
      this.error.probe(printer_cap.z_probe == 1 ? false : true)
    }
    else if (data.type == 'offset_error') {
      this.error.offset(data.msg)
    }
  }

  increase(inc) {
    if (this.error.offset()) this.error.offset(undefined)
    this.offsetVal.edited(
      Math.round((parseFloat(this.offsetVal.edited()) + (inc ? +.05 : -.05))*100)/100)
  }

  set() {
    if (!this.submit_enabled()) return
    OctoPrint.control.sendGcode(this.commands.set + this.offsetVal.edited())
    setTimeout(() => {OctoPrint.control.sendGcode(this.commands.save)}, 1000)
  }

  submit_enabled() {
    if (!this.control.isOperational() || this.control.isPrinting()) return false
    if (isNaN(parseFloat(this.offsetVal.edited()))) return false
    if (this.offsetVal.edited() == this.offsetVal.actual()) return false
    return true
  }

  request (type, command, args, successCb) {
    let data = () => {
      if (command && args) return JSON.stringify({command: command, args: args})
      if (command) return JSON.stringify({command: command})
    }
    $.ajax({
      url: `/api${PLUGIN_BASEURL}z_probe_offset_universal`,
      type: type,
      dataType: 'json',
      data: data(),
      contentType: 'application/json; charset=UTF-8',
      success: (data) => { if (successCb) successCb(data) }
    })
  }
}


OCTOPRINT_VIEWMODELS.push({
  construct: ZProbeOffsetViewModel,
  dependencies: ['controlViewModel'],
});
