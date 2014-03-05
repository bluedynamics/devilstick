=============================
devilstick.metamodel elements
=============================

The Devilstick metamodel defines how data is structured and how it does behave.

Structural elements
===================

Structural elements are used to define the structure of the data-tree, but
without any kind of validation.

We can start by creating an empty root-container::

    >>> from devilstick.metamodel import DSContainer
    >>> root = DSContainer('testroot')
    >>> root
    <DSContainer 'testroot' at ...>

    >>> root.isRoot
    True

    >>> root.implicit
    True

It has no elements contained::

    >>> list(root.containers)
    []

    >>> list(root.attributes)
    []

Define a structure, where the root container may contain sub containers::

    >>> root['subcontainer'] = DSContainer()
    >>> list(root.containers)
    [<DSContainer 'subcontainer' at ...>]

    >>> root['subcontainer'].isRoot
    False

    >>> root['subcontainer'].implicit
    True

Try self containment::

    >>> from devilstick.metamodel import DSContains
    >>> root['subcontainer']['subcontainer'] = DSContains()
    >>> root['subcontainer']['subcontainer'].reference = root['subcontainer']
    >>> list(root['subcontainer'].containers)
    [<DSContainer 'subcontainer' at ...>]

DSContains can't have children!

::

    >>> root['subcontainer']['subcontainer']['foo'] = 'X'
    Traceback (most recent call last):
    ...
    ValueError: DSContains can't have children.

Root container with attributes::

    >>> from devilstick.metamodel import DSAttribute
    >>> root['title'] = DSAttribute(data_type='string')
    >>> list(root.attributes)
    [<DSAttribute 'title' of type 'string' at ...>]

    >>> root['title'].implicit
    True

Type can be set later::

    >>> root['age'] = DSAttribute()
    >>> root['age']
    <DSAttribute 'age' of type '*' at ...>

    >>> root['age'].data_type = 'integer'
    >>> root['age']
    <DSAttribute 'age' of type 'integer' at ...>

Its not permitted to set structural elements as children of an attribute::

    >>> root['age']['bug'] = DSContainer()
    Traceback (most recent call last):
    ...
    ValueError: Element not permitted as child of IDSAttribute

    >>> root['age']['bug'] = DSAttribute()
    Traceback (most recent call last):
    ...
    ValueError: Element not permitted as child of IDSAttribute

    >>> root['age']['bug'] = DSContains()
    Traceback (most recent call last):
    ...
    ValueError: Element not permitted as child of IDSAttribute

Now lets check the tree by visualizing it. We use the str(root) to visualize
the whole (sub) tree, while repr(root) as used above shows the single element.

::

    >>> print root
    <DSContainer 'testroot' at ...>
      <DSContainer 'subcontainer' at ...>
        <DSContains 'subcontainer' at ...>
      <DSAttribute 'title' of type 'string' at ...>
      <DSAttribute 'age' of type 'integer' at ...>
    <BLANKLINE>

Behavioral Elements
===================
s
Behavioral elements are usally dealing with different kinds of behavior. In the
runtims those are used for prevalidation (which answeres the question: will my
planned action work?) and postvalidation (question: is the current action
allowed?). We support three kinds of behavior here:

Validation
    is defined on an attribute and is valid for one single attribute. It checks
    if a given value for this attribute is allowed.

Constraint
    is defined on the container and checks if the containment of a single
    structural element is allowed.

Invariant
    is defined on the container and checks if the containment or value of two
    or more contained elements are ok.

All of those have a ``type`` (string) and ``settings`` (a dict). The idea for
the runtime is to use the type to lookup an implementation and configure it by
passing the settings to it.

Now lets use those behavioral elements, start with the validation::

    >>> from devilstick.metamodel import DSValidation
    >>> root['age']['validation1'] = DSValidation()
    >>> root['age']['validation1'].type = 'required'
    >>> root['age']['validation1']
    <DSValidation 'validation1' of type 'required' (unsufficient) at ...>

    >>> root['age']['validation1'].sufficient = True
    >>> root['age']['validation1']
    <DSValidation 'validation1' of type 'required' (sufficient) at ...>

Here the constraint::

    >>> from devilstick.metamodel import DSConstraint
    >>> root['constraint1'] = DSConstraint()
    >>> root['constraint1'].type = 'multiplicity'
    >>> root['constraint1'].valid_for = 1
    Traceback (most recent call last):
    ...
    TypeError: string expected, but got <type 'int'>

    >>> root['constraint1'].valid_for = 'nonexistent'
    >>> root['constraint1'].valid_for
    Traceback (most recent call last):
    ...
    KeyError: 'Constraint has no valid target.'

    >>> root['constraint1'].valid_for = 'age'
    >>> root['constraint1'].valid_for
    <DSAttribute 'age' of type 'integer' at ...>

    >>> root['constraint1'].settings = 1
    >>> root['constraint1']
    <DSConstraint 'constraint1' of type 'multiplicity' (unsufficient) for 'age'
    at ...>

    >>> from devilstick.metamodel import DSInvariant
    >>> root['invariant1'] = DSInvariant()
    >>> root['invariant1'].type = 'dependency'
    >>>

Annotations
===========

DSNode offers a generic way to add annotations to the model. DSNode uses
nodespaces and the ``annotations`` attribute access returns a nodepace.
It expects any object implementing zope.annotation.interfaces.IAnnotations.

Add Payload to some DSNode::
    
    >>> from zope.annotation import IAnnotations
    >>> from devilstick.metamodel import DSNode
    >>> modelnode = DSNode()
    >>> annotations = IAnnotations(modelnode)
    >>> interact(locals())
    >>> annotations['foo'] = 'bar'
    >>> annotations['foo']
    'bar'
    