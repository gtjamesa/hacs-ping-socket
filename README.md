# Ping (Socket) Binary Sensor for Home Assistant

![beta_badge](https://img.shields.io/badge/maturity-Beta-yellow.png)
![release_badge](https://img.shields.io/github/release/gtjamesa/hacs-ping-socket.svg)
![release_date](https://img.shields.io/github/release-date/gtjamesa/hacs-ping-socket.svg)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## About

[Home Assistant](https://www.home-assistant.io/) binary sensor for monitoring whether a port is running on a particular target host. This integration is rewrite of the [TCP integration](https://www.home-assistant.io/integrations/tcp/) until I have submitted my PR to have it improved. The features the following changes:

* Asynchronous handling to not block HA startup if your target host is down
* Correctly updates binary sensor status to `on`/`off` based on whether the host could be contacted
* Updates `available` status to let you know whether the integration has yet attempted to contact the target host

## Installation

Make sure [Home Assistant Community Store (HACS)](https://github.com/custom-components/hacs) is installed. This integration is part of the default HACS store (though can also be added manually using repository: `gtjamesa/hacs-ping-socket`)

### Configuration

The bare minimum configuration creates general sensors to track the Helium blockchange, notably the HNT/USD Oracle price.

```yaml
binary_sensor:
  - platform: ping_socket
      host: 192.168.200.213
      port: 44158
      value_on: "\x13/multistream/1.0.0\n"
      scan_interval: 300
      name: Bobcat Helium Miner
```

