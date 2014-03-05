from node.interfaces import INode
from zope.annotation.interfaces import IAnnotatable
from zope.interface import Attribute

"""Metamodel interface descriptions for Devilstick.

The metamodel of Devilstick describes how the model behaves.

In Devilstick we have two simple structural elements and elements describing
behavior. These are ```container``` and ```attribute``` (the smallest/atomar
data-entity), a container can contain again containers or attributes.
Order matters. A referencing structural element is ```contains`` which allows
self-containment.

Behavioral elements are defining i.e. constraints applied to structural
elements.

"""


class IDSAnnotatable(IAnnotatable):
    """annotatable DS Nodes
    """


class IDSModelNode(INode):
    """Abstract interface for every element in the model.
    """

#####################
# strcutural elements


class IDSStructural(IDSModelNode):
    """Abstract interface for every structural element in the model.
    """

    implicit = Attribute("""If implicit is set the element has to be created at
                            the same time its container is created. It is
                            expected to be a boolean with default to True.
                            constraints and invariants can be used to define
                            the behavior more fine grained.""")


class IDSContainer(IDSStructural):
    """Container.
    """
    fields = Attribute("Lists all contained fields of the container.")
    containers = Attribute("Lists all contained containers of this container.")
    isRoot = Attribute("check if this container is the root element")

    def constraints(childname):
        """return all constraints valid for the given childname."""


class IDSAttribute(IDSStructural):
    """atomar data-entity
    """
    data_type = Attribute("data type of the attribute (string)")

    def __setitem___(self):
        """Forbids containment of IDSContainer and IDSAttribute implementations.
        """


class IDSContains(IDSStructural):
    """Containment of Elements which arent children of parent element.
    """
    referenced = Attribute("IDSContainer or IDSAttribute element which is not "
                        "directly contained in parent. Major use-case for this "
                        "is self-containment or re-use.")


#####################
# behavioral elements

class IDSBehavior(IDSModelNode):
    """Behavioral Model Elements
    """
    type = Attribute("""Type of behaviour, a name as string. Supposed to be
                        looked up against a registry.""")
    settings = Attribute("Some settings, a dict, supports type")
    sufficient = Attribute("""Behaviors should be processed in a chain. If a
                              behavior is sufficient and the result of the
                              behavior is True the chain processing will be
                              stopped and success returned. Otherwise the chain
                              will be processed further. In any case, on a False
                              result the chain processing will be stopped and
                              failure is returned.
                           """)


class IDSConstraint(IDSBehavior):
    """Rule for a certain structural element contained in parent
    element.
    """
    valid_for = Attribute("Element this constraint is valid for.")


class IDSInvariant(IDSBehavior):
    """Rule for two or more structural elements contained in parent.

    Invariants are rules dependent on existence (or values) of two or more
    structural elements in the container.
    """
    valid_for = Attribute("List of elements this invariant is valid for.")


class IDSValidation(IDSBehavior):
    """Rule valid for parent, with parent is an IDSAttribute.
    """
