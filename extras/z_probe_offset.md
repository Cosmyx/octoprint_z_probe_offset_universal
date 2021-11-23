---
layout: plugin

id: z_probe_offset_univeral
title: Z Probe Offset Universal Control
description: Control the z probe offset on marlin/prusa/klipper based printers.
author: razer
license: AGPLv3
date: 2020-06-14

homepage: https://framagit.org/razer/octoprint_z_probe_offset
source: https://framagit.org/razer/octoprint_z_probe_offset
archive: https://framagit.org/razer/octoprint_z_probe_offset/-/archive/latest/octoprint_z_probe_offset-latest.zip

featuredimage: /assets/img/plugins/z_probe_offset/z_probe_offset_control.png

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

# Z Probe Offset Control

Add input to the control tab for z probe offset value change.
Needs firmware with z probe capability enabled.

![screenshot](/assets/img/plugins/z_probe_offset/z_probe_offset_control.png)