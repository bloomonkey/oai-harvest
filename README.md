# OAI-PMH Harvest


![build:status](https://travis-ci.org/bloomonkey/oai-harvest.svg?branch=master "build status on Travis CI")
![pypi:oaiharvest](https://img.shields.io/pypi/v/oaiharvest.svg "oaiharvest on PyPI")
![license:BSD](https://img.shields.io/pypi/l/oaiharvest.svg "BSD License")
![format:black](https://img.shields.io/badge/code%20style-black-000000.svg "Formatted with black - the uncompromising code formatter")


## Contents

- [Description](#description)
- [Latest Version](#latest-version)
- [Documentation](#documentation)
- [Requirements / Dependencies](#requirements-dependencies)
- [Installation](#installation)
- [Bugs, Feature requests etc.](#bugs-feature-requests-etc)
- [Copyright And Licensing](#copyright-and-licensing)
- [Examples](#examples)

## Description

A harvester to collect records from an OAI-PMH enabled provider.

The harvester can be used to carry out one-time harvesting of all
records from a particular OAI-PMH provider by giving its base URL. It
can also be used for selective harvesting, e.g. to harvest only records
updated after, or before specified dates.

To assist in regular harvesting from one or more OAI-PMH providers,
there's a provider registry. It is possible to associate a short
memorable name for a provider with its base URLs, destination directory
for harvested records, and the format (metadataPrefix) in which records
should be harvested. The registry will also record the date and time of
the most recent harvest, and automatically add this to subsequent
requests in order to avoid repeatedly harvesting unmodified records.

This could be used in conjunction with a scheduler (e.g. CRON) to
maintain a reasonably up-to-date copy of the record in one or more
providers. `Examples`_ of how to accomplish these tasks are available
below.


## Latest Version
--------------

The latest stable release version is available in the Python Packages Index:

https://pypi.python.org/pypi/oaiharvest

Source code is under version control and available from:

http://github.com/bloomonkey/oai-harvest

## Documentation

All executable commands are self documenting, i.e. you can get help on
how to use them with the `-h` or `--help` option.

At this time the only additional documentation that exists can be found
in this README file!

## Requirements / Dependencies

- Python >= 2.7 or Python 3.x
- pyoai
- lxml
- sqlite3

## Installation

### Users

`pip install oaiharvest`

### Developers

I recommend that you use virtualenv to isolate your development environment from system Python and any packages that may be installed
there.

1. In GitHub, fork the repository
2. Clone your fork:

   ```
   git clone git@github.com:<username>/oai-harvest.git
   ```

3. Setup development virtualenv using tox:

   ```
   pip install tox
   tox -e dev
   ```
   
4. Activate development virtualenv:

   -nix:
   
   ```
   source env/bin/activate
   ```
   
   Windows:

   ```
   env\Scripts\activate
   ```

## Bugs, Feature requests etc.

Bug reports and feature requests can be submitted to the GitHub issue
tracker:
http://github.com/bloomonkey/oai-harvest/issues

If you'd like to contribute code, patches etc. please email the author,
or submit a pull request on GitHub.


## Copyright And Licensing

Copyright (c) [University of Liverpool](http://www.liv.ac.uk), 2013-2014

This project is licensed under the terms of the [3-Clause BSD License](LICENSE.md).

## Examples

### Harvesting records from an OAI-PMH provider URL

All records

```
oai-harvest http://example.com/oai
```

Records modified since a certain date

```
oai-harvest --from 2013-01-01 http://example.com/oai
```

Records from a named set

```
oai-harvest --set "some:set" http://example.com/oai
```

Limit the number of records to harvest

```
oai-harvest --limit 50 http://example.com/oai
```

Get help on all available options

```
oai-harvest --help
```

### OAI-PMH Provider Registry

Add a provider

```
oai-reg add provider1 http://example.com/oai/1
```

If you don't supply `--metadataPrefix` and `--directory` options,
you will be interactively prompted to supply alternatives, or accept
the defaults.

Remove an existing provider

```
oai-reg rm provider1 [provider2]
```

List existing providers

```
oai-reg list
```

### Harvesting from OAI-PMH providers in the registry

Harvest from one or more providers in the registry using the short names that they were registered with:

```
oai-harvest provider1 [provider2]
```

By default, this will harvest all records modified since the last harvest from each provider. You can over-ride this behavior using the `--from` and `--until` options.

Harvest from all providers in the registry:

```
oai-harvest all
```

### Scheduling Regular Harvesting

In order to maintain a reasonably up-to-date copy of all the the
records held by those providers, one could configure a scheduler to
periodically harvest from all registered providers. e.g. to tell CRON
to harvest all at 2am every day, one might add the following to
crontab:

```
0 2 * * * oai-harvest all
```
