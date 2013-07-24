OAI-PMH Harvest
===============

24th July 2013 (2013-07-24)

Contents
--------

- `Description`_
- `Author(s)`_
- `Latest Version`_
- `Documentation`_
- `Requirements / Dependencies`_
- `Installation`_
- `Bugs, Feature requests etc.`_
- `Copyright And Licensing`_
- `Examples`_


Description
-----------

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


Author(s)
---------

John Harrison <john.harrison@liv.ac.uk> at the `University of Liverpool`_ 


Latest Version
--------------

The latest release version is available in the Python Packages Index:

https://pypi.python.org/pypi/oaiharvest

.. image:: https://pypip.in/v/oaiharvest/badge.png
    :target: https://crate.io/packages/oaiharvest/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/oaiharvest/badge.png
    :target: https://crate.io/packages/oaiharvest/
    :alt: Number of PyPI downloads



Source code is under version control and available from:

http://github.com/bloomonkey/oai-harvest


Documentation
-------------

All executable commands are self documenting, i.e. you can get help on
how to use them with the ``-h`` or ``--help`` option.

At this time the only additional documentation that exists can be found
in this README file!


Requirements / Dependencies
---------------------------

- Python_ >= 2.6
- pyoai_
- lxml_
- sqlite3_


Installation
------------

Users
~~~~~

``pip install git+http://github.com/bloomonkey/oai-harvest.git#egg=oaiharvest``


Developers
~~~~~~~~~~

I recommend that you use virtualenv_ to isolate your development
environment from system Python_ and any packages that may be installed
there.

1. In GitHub_, fork the repository

2. Clone your fork::

       git clone git@github.com:<username>/oai-harvest.git

3. Install dependencies::

       pip install -r requirements.txt

4. Install in develop / editable mode::

       pip install -e .


Bugs, Feature requests etc.
---------------------------

Bug reports and feature requests can be submitted to the GitHub issue
tracker:
http://github.com/bloomonkey/oai-harvest/issues

If you'd like to contribute code, patches etc. please email the author,
or submit a pull request on GitHub.


Copyright And Licensing
-----------------------

Copyright (c) `University of Liverpool`_, 2013

See `LICENSE.rst <LICENSE.rst>`_ for licensing details.


Examples
--------

Harvesting records from an OAI-PMH provider URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All records
'''''''''''

::

   oai-harvest http://example.com/oai


Records modified since a certain date
'''''''''''''''''''''''''''''''''''''

::

   oai-harvest --from 2013-01-01 http://example.com/oai


Records from a named set
''''''''''''''''''''''''

::

   oai-harvest --set "some:set" http://example.com/oai


Limiting the number of records to harvest
'''''''''''''''''''''''''''''''''''''''''

::

   oai-harvest --limit 50 http://example.com/oai


Getting help on all available options
'''''''''''''''''''''''''''''''''''''

::

   oai-harvest --help


OAI-PMH Provider Registry
~~~~~~~~~~~~~~~~~~~~~~~~~

Adding a provider
'''''''''''''''''

::

   oai-reg add provider1 http://example.com/oai/1


If you don't supply ``--metadataPrefix`` and ``--directory`` options,
you will be interactively prompted to supply alternatives, or accept
the defaults.


Removing an existing provider
'''''''''''''''''''''''''''''

::

   oai-reg rm provider1 [provider2]


Listing existing providers
''''''''''''''''''''''''''

::

   oai-reg list


Harvesting from OAI-PMH providers in the registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can harvest from one or more providers in the registry using the
short names that they were registered with::

   oai-harvest provider1 [provider2]


By default, this will harvest all records modified since the last
harvest from each provider. You can over-ride this behavior using the
``--from`` and ``--until`` options.

You can also harvest from all providers in the registry::

   oai-harvest all


Scheduling Regular Harvesting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to maintain a reasonably up-to-date copy of all the the
records held by those providers, one could configure a scheduler to
periodically harvest from all registered providers. e.g. to tell CRON
to harvest all at 2am every day, one might add the following to
crontab::

   0 2 * * * oai-harvest all


.. Links
.. _Python: http://www.python.org/
.. _pyoai: https://pypi.python.org/pypi/pyoai
.. _PyPI: https://pypi.python.org/pypi
.. _lxml: https://pypi.python.org/pypi/lxml
.. _sqlite3: http://www.sqlite.org/
.. _`University of Liverpool`: http://www.liv.ac.uk
.. _GitHub: http://github.com
.. _virtualenv: http://www.virtualenv.org/en/latest/
