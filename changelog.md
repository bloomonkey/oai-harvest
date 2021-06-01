# Changelog

## [Unreleased]
### Added
- Incremental harvesting during a given time window
- Option to resume from a given token

### Changed
- Adopt codestyle from [black](https://black.readthedocs.io/en/stable/)
- Refactor out fetching records
- Changes file follows [recognised convention](https://keepachangelog.com/en/1.0.0/)

## [3.0.0] - 2017-10-31
### Removed
- Support for Python 2.6

### Fixed
- Log complete traceback on errors
- Decode binary metadata string returned by pyoai in Python 3
- Output files as UTF-8

## [2.0.0] - 2017-04-19
### Added
- Support for building a development virtualenv and testing builds using [Tox](https://tox.readthedocs.io/en/latest/)
- Continuous Integration testing with [Travis CI](https://travis-ci.org/)

### Fixed
- Working in Python 3 (thanks to [@ulikoehler](https://github.com/ulikoehler))
- Allow providers with https transport scheme (thanks to [@ulikoehler](https://github.com/ulikoehler))

## [1.2.0] - 2016-12-30
### Fixed
- Fix build by using ``ez_setup.py`` instead of ``distribute_setup.py`` for
  bootstrapping setuptools.

## [1.1.5] - 2014-04-28
### Added
- Report an appropriate error when a given URL does not appear to resolve to an OAI-PMH server.

## [1.1.4] - 2014-04-02
### Added
- Option to specify a string that, when it occurs in identifiers, is treated as a separator to store harvested records in sub-directories.

### Fixed
- File name escaping on Windows. On Windows do not protect `:` characters from being escaped.

## [1.1.3] - 2013-10-14
### Added
- Option for creating sub-directories based on slashes in identifiers.

## [1.1.2] - 2013-07-24
### Added
- Automatically create download directory if missing, thanks to [@mhoffman](https://github.com/mhoffman)

## [1.1.1] - 2013-05-10
# Fixed
- Removed rogue debugging `raise` statement
- Update registry with `--until` option when given
- Only update registry if harvest completed (i.e. not truncated with `--limit=N`)

## [1.1] - 2013-05-09
### Added
- Handle deletions
- Selective harvesting by set
- Limit harvesting to an arbitrary number of records (e.g. to avoid throttling / blacklisting by provider server)

### Fixed
- Don't ERROR when encountering deleted records

## [1.0] - 2013-04-15
### Added
- Harvest from a given URL
- Selective harvesting by modification date
- Facilitate regular harvesting from 1 or more providers
  - Register parameters - e.g. URL, Schema (`metadataPrefix`), target directory - for regular harvesting from a named provider
  - Specify provider using registered name when harvesting, or harvest from all registered providers using the reserved name `all`
  - Harvest only records modified since last harvest (unless overridden)
