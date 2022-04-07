=========
CHANGELOG
=========

1.1.5
======

* Deregister previous patch version while registering new patch version for a package

1.1.4
======

* Don't overwrite asset requirements while re-building containers

1.1.3
======

* Use faster compression setting for GZIP command
* Local docker image support during container build

1.1.2
======

* Updating requirements to Python>=3.6
* Adding install.sh back to support install instructions from v1.0.0

1.1.0
======

* Published panoramacli package to PyPI
* Update README with new installation instructions
* Don't add new interface and node in package.json when an asset is built if an interface already exists with a matching asset name