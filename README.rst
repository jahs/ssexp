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
deep structures.
