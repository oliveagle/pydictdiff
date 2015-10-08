# encoding=utf-8
__author__ = 'rhtang'

import types
import logging
import copy

types_unary = (types.BooleanType, types.IntType, types.LongType, types.FloatType, types.StringType, types.UnicodeType)
types_array = (types.ListType, types.TupleType)

def diff(obj1, obj2):
    # slow but clear version
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
    #internal use only.

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
                k = k.replace(".", "\.")
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
    xobj = obj
    prev_x = ""
    for x in steps:
        if x.endswith("\\"):
            prev_x += x
            continue
        if prev_x != "":
            _x = prev_x + x
            _x = _x.replace("\\", ".")
            xobj = xobj[_x]
            prev_x = ""
        else:
            if len(x) >=3 and x[0]=='[' and x[-1] == ']':
                idx = int(x[1:-1])
                xobj = xobj[idx]
            else:
                xobj = xobj[x]
    return copy.deepcopy(xobj)

def dot_lookup_with_parent(obj, key):
    '''
    difference with `dot_lookup()` is that origin object can be 
    modify with returned result.
    '''
    assert type(key) in types.StringTypes, "key must be string"
    parent = None
    last_key = None

    steps = key.split(".")
    xobj = obj
    prev_x = ""
    for x in steps:
        if x.endswith("\\"):
            prev_x += x
            continue
        if prev_x != "":
            _x = prev_x + x
            _x = _x.replace("\\", ".")
            parent = xobj
            last_key = _x
            xobj = xobj[_x]
            prev_x = ""
        else:
            if len(x) >=3 and x[0]=='[' and x[-1] == ']':
                idx = int(x[1:-1])
                parent = xobj
                last_key = idx
                xobj = xobj[idx]
            else:
                parent = xobj
                last_key = x
                xobj = xobj[x]
    return parent, last_key, xobj, type(xobj) in types_unary


def patch(obj, diff):
    # slow version
    for chg in diff:
        logging.debug("patch: 0 ", chg)
        if len(chg)==3:
            action, key, tobe = chg
        
            if action == 'changed':
                logging.debug("patch: 1.1 changed - ", chg)
                parent, k, v, is_unary = dot_lookup_with_parent(obj, chg[1])
                logging.debug("patch: 1.2 changed - ", parent, k, v, is_unary)
                if is_unary:
                    if len(k) >=3 and k[0]=='[' and k[-1] == ']':
                        idx = int(k[1:-1])
                        parent[idx] = chg[2][1]
                    else:
                        parent[k] = chg[2][1]
            elif action == 'added':
                keys = chg[1].rsplit('.', 1)
                logging.debug("patch:2.1 added - ", keys)
                parent, k, v, is_unary = dot_lookup_with_parent(obj, keys[0])
                logging.debug("patch:2.2 added - ", parent, k, v, is_unary)
                v[keys[1]] = chg[2]
            elif action == 'removed':
                pass
                keys = chg[1].rsplit('.', 1)
                logging.debug("patch:3.1 removed - ", keys)
                parent, k, v, is_unary = dot_lookup_with_parent(obj, keys[0])
                logging.debug("patch:3.2 removed - ", parent, k,  v, is_unary)
                v.pop(keys[1])