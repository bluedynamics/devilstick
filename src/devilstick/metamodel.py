from devilstick import interfaces
from node import behaviors
from zope.annotation.interfaces import IAnnotations
from zope.component import provideAdapter
from zope.component import adapter
from zope.interface import implementer
import plumber


def _tree(dsn, indent):
    res = ' ' * indent + repr(dsn) + '\n'
    for key in dsn:
        subdsn = dsn[key]
        if interfaces.IDSModelNode.providedBy(subdsn):
            res += _tree(subdsn, indent + 2)
        else:
            res += ' ' * indent + 2 + '?', repr(dsn) + '\n'
    return res

ANNOKEY = '__annotations__'


@implementer(interfaces.IDSAnnotatable)
class Annotateable(plumber.Behavior):

    annotations_factory = plumber.default(behaviors.NodeAttributes)

    @plumber.finalize
    @property
    def annotations(self):
        try:
            annotations = self.nodespaces[ANNOKEY]
        except KeyError:
            annotations = self.nodespaces[ANNOKEY] = \
                self.annotations_factory(name=ANNOKEY, parent=self)
        return annotations


@implementer(IAnnotations)
@adapter(interfaces.IDSAnnotatable)
def annotation_adapter(dsnode):
    return dsnode.annotations
provideAdapter(annotation_adapter)

DS_BASE_BEHAVIORS = (
    Annotateable,
    behaviors.UUIDAware,
    behaviors.NodeChildValidate,
    behaviors.Nodespaces,
    behaviors.Adopt,
    behaviors.Attributes,
    behaviors.Reference,
    behaviors.Order,
    behaviors.AsAttrAccess,
    behaviors.DefaultInit,
    behaviors.Nodify,
    behaviors.OdictStorage,
)


@implementer(interfaces.IDSModelNode)
class DSNode(object):
    """Kind of Abstract Base Class for Devilstick Nodes.
    """
    __metaclass__ = plumber.plumber
    __plumbing__ = DS_BASE_BEHAVIORS

    def __repr__(self):
        return "<%s '%s' at %s>" % (self.__class__.__name__, self.__name__,
                                    hex(id(self))[:-1])

    def __str__(self):
        return _tree(self, 0)


###############################################################################
# Structural

@implementer(interfaces.IDSContainer)
class DSContainer(DSNode):
    """Devilstick Container Model Node
    """

    implicit = True

    @property
    def attributes(self):
        return self.filtereditems(interfaces.IDSAttribute)

    @property
    def containers(self):
        for node in self.values():
            if interfaces.IDSContainer.providedBy(node):
                yield node
            if interfaces.IDSContains.providedBy(node):
                yield node.reference

    @property
    def isRoot(self):
        return self.__parent__ is None

    @property
    def constraints(self, childname):
        return [n for n in self.filterNodes(interfaces.IDSConstraint) \
                if n.validfor == childname]


@implementer(interfaces.IDSAttribute)
class DSAttribute(DSNode):
    """Devilstick Attribute Model Node
    """

    implicit = True

    def __init__(self, name=None, data_type=None):
        self.data_type = data_type
        DSNode.__init__(self, name=name)

    def __setitem__(self, key, value):
        if interfaces.IDSStructural.providedBy(value) \
           or interfaces.IDSConstraint.providedBy(value) \
           or interfaces.IDSInvariant.providedBy(value):
            raise ValueError("Element not permitted as child of IDSAttribute")
        super(DSAttribute, self).__setitem__(key, value)

    def __repr__(self):
        values = {
            'klass': self.__class__.__name__,
            'name': self.__name__,
            'type': self.data_type if self.data_type is not None else '*',
            'id': id(self),
        }
        return "<{klass} '{name}' of type '{type}' at {id}>".format(**values)


@implementer(interfaces.IDSContains)
class DSContains(DSNode):
    """Devilstick Contains Model Node
    """

    _reference_uuid = None

    @property
    def reference(self):
        return self.node(self._reference_uuid)

    @reference.setter
    def reference(self, reference):
        self._reference_uuid = reference.uuid

    def __setitem__(self, key, value):
        raise ValueError("DSContains can't have children.")


###############################################################################
# Behaviors

class DSBehavior(DSNode):
    """Abstract base class for behaviors.
    """
    type = None
    settings = None
    sufficient = False

    def __repr__(self):
        return "<%s '%s' of type '%s' (%s) at %s>" % \
               (self.__class__.__name__, self.__name__, self.type,
                self.sufficient and 'sufficient' or 'unsufficient',
                hex(id(self))[:-1])


@implementer(interfaces.IDSConstraint)
class DSConstraint(DSBehavior):
    """Devilstick Constraint Model Node
    """

    _validfor = None

    @property
    def validfor(self):
        if self._validfor is None or self._validfor not in self.__parent__:
            raise KeyError("Constraint has no valid target.")
        return self.__parent__[self._validfor]

    @validfor.setter
    def validfor(self, childname):
        if not isinstance(childname, basestring):
            raise TypeError("string expected, but got %s" % type(childname))
        self._validfor = childname

    def __repr__(self):
        return "<%s '%s' of type '%s' (%s) for '%s' at %s>" % \
               (self.__class__.__name__, self.__name__, self.type,
                self.sufficient and 'sufficient' or 'unsufficient',
                self._validfor,
                hex(id(self))[:-1])


@implementer(interfaces.IDSInvariant)
class DSInvariant(DSBehavior):
    """Devilstick Invariant Model Node
    """

    _validfor = None

    @property
    def validfor(self):
        if self._validfor is None:
            raise KeyError("Invariant has no valid targets.")
        for childname in self._validfor:
            if childname not in self.__parent__:
                raise KeyError("Invariant has no valid targets.")
            yield self.__parent__[childname]

    @validfor.setter
    def validfor(self, childnames):
        for childname in childnames:
            if not isinstance(childname, basestring):
                raise TypeError(
                    "string expected, but got {0}".format(type(childname))
                )
        if len(childnames) < 2:
            raise ValueError("invariant needs at least 2 validfor children")
        self._validfor = childnames

    def __repr__(self):
        return "<%s '%s' of type '%s' (%s) for '%s' at %s>" % \
               (self.__class__.__name__, self.__name__, self.type,
                self.sufficient and 'sufficient' or 'unsufficient',
                self._validfor and ', '.join(self._validfor) or self._validfor,
                hex(id(self))[:-1])


@implementer(interfaces.IDSValidation)
class DSValidation(DSBehavior):
    """Devilstick Validation Model Node
    """
