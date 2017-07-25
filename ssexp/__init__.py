import sys

from fn import recur
import preserialize


DATA = preserialize.DATA
STR = preserialize.STR


class SsexpError(Exception):
    pass


SCHEME_TYPES = preserialize.BASIC_TYPES + (
    (bool,),
    (type(None), preserialize.Deconstructor, dict(name=u"none")),
    (dict, preserialize.DictDeconstructor, dict(name=u":")))


class LabelLinkManager(preserialize.LinkManager):
    """Source and destination integer label."""

    KEY = u":label"

    def is_ref(self, obj):
        return type(obj) == dict and self.KEY in obj

    def make_ref(self, dest):
        return {self.KEY: self._links[dest][0]}

    def label_destination(self, i, obj):
        return {self.KEY: i, DATA: [obj]}

    def unlabel_destination(self, obj):
        return obj[DATA][0]


class SchemeEncoder(preserialize.Encoder):
    """Map ``is_`` prefix to ``?`` suffix, and ``_`` to ``-``."""

    def encode(self, s):
        if s.startswith(u"is_"):
            s = u"{0}?".format(s[3:])
        return s.replace(u"_", u"-")

    def decode(self, s):
        s = s.replace(u"-", u"_")
        if s.endswith(u"?"):
            s = u"is_{0}".format(s)
        return s


class SsexpPreserializer(preserialize.Preserializer):
    """Preserializer to a Scheme-friendly S-expression precursor."""

    def __init__(self, is_translated=True):
        super().__init__(types=SCHEME_TYPES,
                         link_manager_cls=LabelLinkManager,
                         key_encoder=(
                             SchemeEncoder() if is_translated else None))


@recur.stackless
def remove_mapping(data, head_key=u":type", dict_name=None,
                   list_type=list, mapping_type=dict):
    """Turn each *mapping* in ``data`` into a list.

    If ``head_key`` is in the mapping, the corresponding value becomes
    the head of the list.

    Strings are double quote encoded, as we need to distinguish
    between lists and mappings (which have an unquoted string as the
    head).

    """

    escape_char = head_key[0]
    dict_name = escape_char if dict_name is None else dict_name

    t = type(data)
    if t == preserialize.STR:
        yield preserialize.DoubleQuoteEncoder.encode(data)
    elif t == list_type:
        new = t()
        for item in data:
            new.append((yield remove_mapping.call(
                item, head_key, dict_name, list_type, mapping_type)))
        yield new
    elif t == mapping_type:
        new = list_type()

        if head_key in data:
            new.append(data[head_key])

        for key, item in data.items():  # metadata keys first
            if key.startswith(escape_char) and key != head_key:
                new.extend((u"{0}:".format(key),
                            (yield remove_mapping.call(
                        item, head_key, dict_name, list_type, mapping_type))))

        for key, item in data.items():  # kwargs first as nice for eg XML
            if not (key.startswith(escape_char) or key == preserialize.DATA):
                new.extend((u"{0}:".format(key),
                            (yield remove_mapping.call(
                        item, head_key, dict_name, list_type, mapping_type))))

        if preserialize.DATA in data:  # finally splice list items
            maybe_splice = data[preserialize.DATA]
            if type(maybe_splice) == list_type:
                for item in maybe_splice:
                    new.append((yield remove_mapping.call(
                        item, head_key, dict_name, list_type, mapping_type)))
            else:
                raise SsexpError(
                    u'Found data key ("") but item not a list_type.')
        yield new
    else:
        yield data


@recur.stackless
def to_ssexp(tree):
    t = type(tree)
    if t == int or t == float:
        yield preserialize.STR(tree)
    elif t == preserialize.STR:
        yield tree
    elif t == bool:
        yield u"#t" if tree else u"#f"
    elif tree and tree[0] == u":label:":
        n = len(tree)
        if n == 2:  # dest
            yield u"#{0}#".format(tree[1])
        elif n == 3:  # source
            yield u"#{0}={1}".format(tree[1], (yield to_ssexp.call(tree[2])))
        else:
            raise Exception(u"Bad :label: form.")
    else:
        new = []
        for item in tree:
            new.append((yield to_ssexp.call(item)))
        yield u"({0})".format(u" ".join(new))


def dumps(obj, preserializer=None):
    preserializer = preserializer if preserializer else SsexpPreserializer()
    return to_ssexp(remove_mapping(preserializer.preserialize(obj)))
