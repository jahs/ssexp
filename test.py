import unittest

import ssexp


class JsonTests(unittest.TestCase):
    def setUp(self):
        class Parrot(object):
            def __init__(self, is_dead=True, from_egg=None):
                self.is_dead = is_dead
                self.from_egg = from_egg

        self.preserializer = ssexp.SsexpPreserializer()
        self.preserializer.register(Parrot, version=2)

        class Egg(object):
            def __init__(self, from_parrot=None):
                self.from_parrot = from_parrot

        self.preserializer.register(Egg)

        self.parrot = Parrot()
        self.parrot.from_egg = Egg(from_parrot=self.parrot)

    def test_int(self):
        obj = 123
        result = u"123"
        self.assertEqual(ssexp.dumps(obj), result)


    def test_float(self):
        obj = 3.1415927
        result = u"3.1415927"
        self.assertEqual(ssexp.dumps(obj), result)


    def test_str(self):
        obj = u'The Knights who say "Ni!".'
        result = u'"The Knights who say \\"Ni!\\"."'
        self.assertEqual(ssexp.dumps(obj), result)


    def test_bool(self):
        obj = False
        result = u"#f"
        self.assertEqual(ssexp.dumps(obj), result)


    def test_none(self):
        obj = None
        result = u"(none)"
        self.assertEqual(ssexp.dumps(obj), result)


    def test_list(self):
        obj = [123, 3.1415927, u'The Knights who say "Ni!".', False, None]
        result = '(123 3.1415927 "The Knights who say \\"Ni!\\"." #f (none))'
        self.assertEqual(ssexp.dumps(obj), result)


    def test_dict(self):
        obj = {'brian': 'naughty boy'}
        result = '(: brian: "naughty boy")'
        self.assertEqual(ssexp.dumps(obj), result)


    def test_dict_args(self):
        obj = {'brian': 'naughty boy', 3: 'Antioch'}
        result = '(: ("brian" "naughty boy") (3 "Antioch"))'
        self.assertEqual(ssexp.dumps(obj), result)


    def test_dict_args_cyclic(self):
        obj = {'brian': 'naughty boy', 3: 'Antioch', 'ouroboros': self.parrot}
        result = '(: ("brian" "naughty boy") (3 "Antioch") ("ouroboros" #0=(parrot :version: 2 dead?: #t from-egg: (egg from-parrot: #0#))))'
        self.assertEqual(ssexp.dumps(obj, self.preserializer), result)
