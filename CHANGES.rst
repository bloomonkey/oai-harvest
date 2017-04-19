CHANGES
=======

2.0.0 Wednesday 19th April 2017
-------------------------------

NEW FEATURES
~~~~~~~~~~~~

- Support for building a development virtualenv and testing builds using Tox_

- Integration with `Travis CI`_


ENHANCEMENTS
~~~~~~~~~~~~

- Now works in Python 3 (thanks to `@ulikoehler <https://github.com/ulikoehler>`_)

- Allow providers with https transport scheme (thanks to
  `@ulikoehler <https://github.com/ulikoehler>`_)


1.2.0 Friday 30th December 2016
-------------------------------

BUG FIXES
~~~~~~~~~

- Fix build by using ``ez_setup.py`` instead of ``distribute_setup.py`` for
  bootstrapping setuptools.


1.1.5 Monday 28th April 2014
----------------------------

ENHANCEMENTS
~~~~~~~~~~~~

- Report an appropriate error when a given URL does not appear to resolve to
  an OAI-PMH server.


1.1.4 Wednesday 2nd April 2014
------------------------------

ENHANCEMENTS
~~~~~~~~~~~~

- Add an option to specify a string that, when it occurs in identifiers, is
  treated as a separator to store harvested records in sub-directories.


BUG FIXES
~~~~~~~~~

- Fix bug in file name escaping on Windows. On Windows do not protect :
  characters from being escaped.


1.1.3 Monday 14th October 2013
------------------------------

ENHANCEMENTS
~~~~~~~~~~~~

- Add option for creating sub-directories based on slashes in identifiers.


1.1.2 Wednesday 24th July 2013
------------------------------

ENHANCEMENTS
~~~~~~~~~~~~

- Automatically create download directory if missing
  Thanks to `@mhoffman <https://github.com/mhoffman>`_.


1.1.1 Friday 10th May 2013
--------------------------

BUG FIXES
~~~~~~~~~

- Removed rogue debugging `raise` statement

- Update registry with `--until` option when given

- Only update registry if harvest completed
  (i.e. not truncated with `--limit=N`)


1.1 Thursday 9th May 2013
-------------------------

NEW FEATURES
~~~~~~~~~~~~

- Handle deletions

- Selective harvesting by set

- Limit harvesting to an arbitrary number of records (e.g. to avoid
  throttling / blacklisting by provider server)


BUG FIXES
~~~~~~~~~

- Don't ERROR when encountering deleted records


1.0 - Monday 15th April 2013
----------------------------

NEW FEATURES
~~~~~~~~~~~~

- Harvest from a given URL

- Selective harvesting by modification date

- Facilitate regular harvesting from 1 or more providers

  - Register parameters - e.g. URL, Schema (metadataPrefix), target
    directory - for regular harvesting from a named provider

  - Specify provider using registered name when harvesting, or harvest
    from all registered providers using the reserved name ``all``

  - Harvest only records modified since last harvest (unless overridden)


.. Links
.. _Travis CI: https://travis-ci.org/
.. _Tox: https://tox.readthedocs.io/en/latest/
