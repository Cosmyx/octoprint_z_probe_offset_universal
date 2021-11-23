---
layout: plugin

id: z_probe_offset_univeral
title: Z Probe Offset Universal Control
description: Control the z probe offset on marlin/prusa/klipper based printers.
author: Cosmyx
license: AGPLv3
date: 2021-11-23

homepage: https://github.com/Cosmyx/octoprint_z_probe_offset_universal
source: https://github.com/Cosmyx/octoprint_z_probe_offset_universal
archive: https://github.com/Cosmyx/octoprint_z_probe_offset_universal/archive/refs/heads/master.zip

featuredimage: /assets/img/plugins/z_probe_offset/z_probe_offset_control_universal.png

tags:
- probe
- marlin
- klipper
- prusa

compatibility:
  octoprint:
  - 1.3.9
  os:
  - linux
  - freebsd
  python: ">=2.7,<4"
---

# Z Probe Offset Universal Control

Add input to the control tab for z probe offset value change.
Needs firmware with z probe capability enabled.

> fork of [z_probe_offset_control](https://framagit.org/razer/octoprint_z_probe_offset/-/tree/master) implementing klipper compatibility

![screenshot](/assets/img/plugins/z_probe_offset/z_probe_offset_control.png)