OAI Harvest
===========

5th February 2013 (2013-02-05)

Contents
--------

- `Description`_
- `Author(s)`_
- `Latest Version`_
- `Documentation`_
- `Requirements / Dependencies`_
- `Installation`_
- `Bugs, Feature requests etc.`_
- `Copyright & Licensing`_
                                   

Description
-----------

Harvest records from an OAI-PMH provider.


Author(s)
---------

John Harrison <john.harrison@liv.ac.uk> at the `University of Liverpool`_ 


Latest Version
--------------

This is a pre-release repository of the code. There are no discrete version
numbers as yet. Source code is under version control and available from:
http://github.com/bloomonkey/oai-harvest


Documentation
-------------

All executable commands are self documenting, i.e. you can get help on how to
use them with the ``-h`` or ``--help`` option.

At this time the only additional documentation that exists can be found in this
README file!


Requirements / Dependencies
---------------------------

- Python 2.6+
- pyoai
- lxml


Installation
------------

Users
~~~~~

``pip install git+http://github.com/bloomonkey/oai-harvest.git#egg=oaiharvest``


Developers
~~~~~~~~~~

I recommend that you use virtualenv_ to isolate your development environment
from system Python_ and any packages that may be installed there.

1. In GitHub_, fork the repository

2. Clone your fork:

   ``git clone git@github.com:<username>/oai-harvest.git``

3. Install dependencies:

   ``pip install -r requirements.txt``

4. Install in develop / editable mode:

   ``pip install -e .``


Bugs, Feature requests etc.
---------------------------

Bug reports and feature requests can be submitted to the GitHub issue tracker:
http://github.com/bloomonkey/oai-harvest/issues

If you'd like to contribute code, patches etc. please email the author, or
submit a pull request on GitHub.


Copyright & Licensing
---------------------

Copyright (c) `University of Liverpool`_, 2013

See LICENSE.rst for licensing details.


.. Links
.. _Python: http://www.python.org/
.. _WSGI: http://wsgi.org
.. _`Encoded Archival Description`: http://www.loc.gov/ead/
.. _`University of Liverpool`: http://www.liv.ac.uk
.. _GitHub: http://github.com
.. _virtualenv: http://www.virtualenv.org/en/latest/
