# Copyright 2007-2009, BlueDynamics Alliance - http://bluedynamics.com
# BSD License derivative, see LICENSE.txt or package long description.

from zope.interface import implements
from node.base import OrderedNode
from devilstick.interfaces import (
    IDSModelNode,
    IDSStructural,
    IDSContainer,
    IDSAttribute,
    IDSContains,
    IDSConstraint,
    IDSInvariant,
    IDSValidation,
)

def _tree(dsn, indent):
    res = ' ' * indent + repr(dsn) + '\n'
    for key in dsn:
        subdsn = dsn[key]
        if IDSModelNode.providedBy(subdsn):
            res += _tree(subdsn, indent+2)
        else:
            res += ' ' * indent+2 + '?', repr(dsn) + '\n'
    return res

class DSNode(OrderedNode):
    """Kind of Abstract Base Class for Devilstick Nodes.
    """
    implements(IDSModelNode)
    
    def __repr__(self):
        return "<%s '%s' at %s>" % (self.__class__.__name__, self.__name__, 
                                    hex(id(self))[:-1])
        
    def __str__(self):
        return _tree(self, 0)
        

################################################################################
# Structural    

class DSContainer(DSNode):
    """Devilstick Container Model Node
    """
    implements(IDSContainer)
    
    implicit = True

    @property
    def attributes(self):
        return self.filtereditems(IDSAttribute)

    @property
    def containers(self):
        for node in self.values():
            if IDSContainer.providedBy(node):
                yield node
            if IDSContains.providedBy(node):
                yield node.reference

    @property
    def isRoot(self):
        return self.__parent__ is None
    
    @property
    def constraints(self, childname):
        return [n for n in self.filterNodes(IDSConstraint) \
                if n.validfor==childname]
        
    
class DSAttribute(DSNode):
    """Devilstick Attribute Model Node
    """
    implements(IDSAttribute)
    
    implicit = True

    def __init__(self, name=None, type=None):
        self.type = type
        DSNode.__init__(self, name=name)
    
    def __setitem__(self, key, value):
        if IDSStructural.providedBy(value) \
           or IDSConstraint.providedBy(value) \
           or IDSInvariant.providedBy(value):
            raise ValueError, "Element not permitted as child of IDSAttribute"
        super(DSAttribute, self).__setitem__(key, value)

    def __repr__(self):
        return "<%s '%s' of type %s at %s>" % (self.__class__.__name__, 
                                               self.__name__, self.type, 
                                               hex(id(self))[:-1])    
        
class DSContains(DSNode):
    """Devilstick Contains Model Node
    """
    implements(IDSContains)
    
    _reference_uuid = None
    
    def get_reference(self):
        return self.node(self._reference_uuid)
    
    def set_reference(self, reference):
        self._reference_uuid = reference.uuid
        
    reference = property(get_reference, set_reference)

    def __setitem__(self, key, value):
        raise ValueError, "DSContains can't have children."

################################################################################
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
               
    
class DSConstraint(DSBehavior):
    """Devilstick Constraint Model Node
    """
    implements(IDSConstraint)
    
    _validfor = None
    
    def get_validfor(self):
        if self._validfor is None or self._validfor not in self.__parent__:
            raise KeyError, "Constraint has no valid target."
        return self.__parent__[self._validfor]
    
    def set_validfor(self, childname):
        if not isinstance(childname, basestring):
            raise TypeError, "string expected, but got %s" % type(childname)
        self._validfor = childname
        
    validfor = property(get_validfor, set_validfor)

    def __repr__(self):
        return "<%s '%s' of type '%s' (%s) for '%s' at %s>" % \
               (self.__class__.__name__, self.__name__, self.type, 
                self.sufficient and 'sufficient' or 'unsufficient',
                self._validfor,  
                hex(id(self))[:-1])    

    
class DSInvariant(DSBehavior):
    """Devilstick Invariant Model Node
    """
    implements(IDSInvariant)
    
    _validfor = None
    
    def get_validfor(self):
        if self._validfor is None:
            raise KeyError, "Invariant has no valid targets."
        for childname in self._validfor:
            if childname not in self.__parent__:
                raise KeyError, "Invariant has no valid targets."
            yield self.__parent__[childname]        
    
    def set_validfor(self, childnames):
        for childname in childnames:
            if not isinstance(childname, basestring):
                raise TypeError, "string expected, but got %s" % type(childname)
        if len(childnames) < 2:
            raise ValueError, "invariant needs at least 2 validfor children"
        self._validfor = childnames
        
    validfor = property(get_validfor, set_validfor)

    def __repr__(self):
        return "<%s '%s' of type '%s' (%s) for '%s' at %s>" % \
               (self.__class__.__name__, self.__name__, self.type, 
                self.sufficient and 'sufficient' or 'unsufficient',
                self._validfor and ', '.join(self._validfor) or self._validfor,  
                hex(id(self))[:-1])    
    
    
class DSValidation(DSBehavior):
    """Devilstick Validation Model Node
    """        
    implements(IDSValidation)

    
