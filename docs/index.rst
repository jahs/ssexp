.. SSexp documentation master file, created by
   sphinx-quickstart on Tue Jul 25 23:04:44 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SSexp's documentation!
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

This is a serializer that produces an S-expression compatible with a
subset of R7RS Scheme.


Usage
-----

The function :func:`ssexp.dumps` serializes an object to a string. A
pre-serializer can be supplied if the object contains more complex
objects.


Examples
--------

.. code-block:: python

  import ssexp
  ssexp.dumps({'brian': 'naughty boy'})

produces:

.. code-block:: scheme

  (: brian: "naughty boy")

We use the ``preserialize`` library to pre-serialize more complex
structures, and so can handle shared objects, cyclic references and
deep structures:

.. code-block:: python

  class Parrot(object):
      def __init__(self, is_dead=True, from_egg=None):
          self.is_dead = is_dead
          self.from_egg = from_egg

  preserializer = ssexp.SsexpPreserializer()
  preserializer.register(Parrot, version=2)

  class Egg(object):
      def __init__(self, from_parrot=None):
          self.from_parrot = from_parrot

  preserializer.register(Egg)

  parrot = Parrot()
  parrot.from_egg = Egg(from_parrot=parrot)

  ssexp.dumps({'brian': 'naughty boy',
               3: 'Antioch',
               'ouroboros': parrot}, preserializer)

produces:

.. code-block:: scheme

  (: ("brian" "naughty boy")
     (3 "Antioch")
     ("ouroboros" #0=(parrot :version: 2
                      dead?: #t
		      from-egg: (egg from-parrot: #0#))))


License
-------

Copyright James A. H. Skillen, 2017.

Distributed under the terms of the MIT license.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
