Scheme S-expressions
====================

This is a serializer that produces an S-expression compatible with a
subset of R7RS Scheme.

Basic usage:

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
