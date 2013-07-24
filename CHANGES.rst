CHANGES
=======

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
    from all registered providers using the reserved name `all`

  - Harvest only records modified since last harvest (unless overridden)

