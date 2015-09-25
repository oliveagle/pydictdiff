# encoding=utf-8
__author__ = 'rhtang'

import types
import logging
import copy
import weakref


types_unary = (types.BooleanType, types.IntType, types.LongType, types.FloatType, types.StringType, types.UnicodeType)
types_array = (types.ListType, types.TupleType)

# class Changes(object):
#     ctype = "changed"
#     def __init__(self, ctype, key, unary):
#         self.ctype = ctype
#         self.key = key
#         self.unary = unary
#     def __str__(self):
#         return str((self.ctype, self.key, self.unary))
#     def __unicode__(self):
#         return unicode((self.ctype, self.key, self.unary))

# class CHANGED(Changes):
#     def __init__(self, key, frm, to):
#         self.ctype="changed"
#         self.key = key
#         self.unary = (frm, to)
# class REMOVED(Changes):
#     def __init__(self, key, v):
#         self.ctype="removed"
#         self.key = key
#         self.unary = v
# class DELETED(Changes):
#     def __init__(self, key, v):
#         self.ctype="deleted"
#         self.key = key
#         self.unary = v

def diff(obj1, obj2):
    # slow bud clear version
    flat_dict1 = flatten(obj1)
    flat_dict2 = flatten(obj2)
    res = []
    for fk, fv in flat_dict2.iteritems():
        if fk in flat_dict1:
            old_v = flat_dict1.pop(fk)
            if old_v != fv:
                res.append(("changed", fk, (old_v, fv)))
        else:
            res.append(("added", fk, fv))
    for fk, fv in flat_dict1.iteritems():
        res.append(("removed", fk, fv))
    return res

def flatten(obj, key=""):
    '''
    >>> flatten({'a': 1})
    {'a': 1}

    >>> flatten({'a': {'b': 1, 'c':2}})
    {'a.b':1, 'a.c':2}

    >>> flatten({'a': {'b': 1}, 'b': 2})
    {'a.b':1, 'b': 2}

    >>> flatten({'a': ['b',1]})
    {'a.[0]': 'b', 'a.[1]': 1}

    >>> flatten({'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}})
    {'a.b.[0].c.[0].d.[0].e': 1, 'a.b.[0].c.[0].d.[0].f': 2}
    '''
    assert type(key) in types.StringTypes, "key must be string"
    res = {}
    if type(obj) in types_unary:
        return {key: obj}
    elif type(obj) == types.DictType:
        for k, v in obj.iteritems():
            if "." in k:
                raise KeyError("`.` in key name is not allowed")
            nkey = "%s.%s" % (str(key),str(k)) if key != "" else str(k)
            flatten_value = flatten(v, key=nkey)
            if type(flatten_value) == types.DictType:
                for fk, fv in flatten_value.iteritems():
                    res[fk] = fv
    elif type(obj) in types_array:
        for idx, v in enumerate(obj):
            nkey = "%s.[%d]" % (key, idx) if key != "" else None
            if nkey:
                flatten_value = flatten(v, key=nkey)
                if type(flatten_value) == types.DictType:
                    for fk, fv in flatten_value.iteritems():
                        res[fk] = fv
    return res

def dot_lookup(obj, key):
    '''
    you cannot modify obj with dot_lookup result.
    '''
    assert type(key) in types.StringTypes, "key must be string"

    steps = key.split(".")
    xobj = copy.deepcopy(obj)
    # xobj = obj
    for x in steps:
        if len(x) >=3 and x[0]=='[' and x[-1] == ']':
            idx = int(x[1:-1])
            xobj = xobj[idx]
        else:
            xobj = xobj[x]
    return xobj

def dot_lookup_with_parent(obj, key):
    '''
    difference with `dot_lookup()` is that origin object can be 
    modify with returned result.
    '''
    assert type(key) in types.StringTypes, "key must be string"
    parent = None

    steps = key.split(".")
    xobj = obj
    for x in steps:
        if len(x) >=3 and x[0]=='[' and x[-1] == ']':
            idx = int(x[1:-1])
            parent = xobj
            xobj = xobj[idx]
        else:
            parent = xobj
            xobj = xobj[x]
    return parent, xobj, type(xobj) in types_unary


def patch(obj, diff):
    # slow version
    for chg in diff:
        print "patch: 0 ", chg
        if len(chg)==3:
            action, key, tobe = chg
        
            if action == 'changed':
                print "patch: 1 ", chg
                # if len(chg[2])==2 and type(chg[1]) in types.StringTypes:
                parent, res, is_unary = dot_lookup_with_parent(obj, chg[1])
                print "patch: 1 ", parent, res, is_unary
                if is_unary:
                    last_key = chg[1].split('.')[-1]
                    if len(last_key) >=3 and last_key[0]=='[' and last_key[-1] == ']':
                        idx = int(last_key[1:-1])
                        parent[idx] = chg[2][1]
                    else:
                        parent[last_key] = chg[2][1]
            elif action == 'added':
                keys = chg[1].rsplit('.', 1)
                print "patch:2.1 ", keys
                parent, res, is_unary = dot_lookup_with_parent(obj, keys[0])
                print "patch:2.2 ", parent, res, is_unary
                res[keys[1]] = chg[2]
            elif action == 'removed':
                pass
                keys = chg[1].rsplit('.', 1)
                print "patch:3.1 ", keys
                parent, res, is_unary = dot_lookup_with_parent(obj, keys[0])
                print "patch:3.2 ", parent, res, is_unary
                res.pop(keys[1])