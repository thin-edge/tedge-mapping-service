# tedge-mapping-service

Thin-edge.io can be extended with plugins or operations. This is a sample how to add a custom service that performs some business logic.
In this case the service maps from a custom json format to tedge json format.

Publish custom measurement:
```
tedge mqtt pub custom/signal '{"value":90}'
```

This measurement is converted to:

```
{ "temperature": {"value": 180  } }
```

and published on the topic: `te/device/main///m/c8y_Temperature`

## Requirements

- Ubuntu >= 22.04 or Debian >= 11.0
- Python >= 3.8, including [paho-mqtt](https://pypi.org/project/paho-mqtt/)
- systemd
- for operations support: thin-edge.io >= 1.1.0

## Build

A package of the service, can be build with nfpm. To build the packages locally, make sure to install nfpm first.
The package requires a python3 installation on your device.

To create the packages, you need to install nfpm first:

[Install nfpm](https://nfpm.goreleaser.com/install/)


### Debian package

After installing, you can build the Debian package with:

     nfpm pkg --packager deb --target /tmp/

## Deployment

### As deb file

Run `sudo dpkg -i tedge-mapping-service-<version>-<arch>.deb`