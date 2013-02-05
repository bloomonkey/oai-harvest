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

Copyright © 2013, the `University of Liverpool`_. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

-  Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
-  Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
-  Neither the name of the University of Liverpool nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


.. Links
.. _Python: http://www.python.org/
.. _WSGI: http://wsgi.org
.. _`Encoded Archival Description`: http://www.loc.gov/ead/
.. _`University of Liverpool`: http://www.liv.ac.uk
.. _GitHub: http://github.com
.. _virtualenv: http://www.virtualenv.org/en/latest/
