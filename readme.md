pydictdiff
---------

yet another python dict diff library. it's not designed to solve all cases.

It has many limitations:
* some modifications will be ignored.
* ...

usage
-----
sample scenario
```python
>>> import dictdiff as dd
>>> a = {'a':1, 'b': 2}
>>> b = {'a':2, 'c': 2}
>>> diff = dd.diff(a, b)
>>> print diff
[('changed', 'a', (1, 2)), ('added', 'c', 2), ('removed', 'b', 2)]
```

nested json object.
```python
>>> import dictdiff as dd
>>> a = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}}
>>> b = {'a':{'b':[{'c': [{'d':[{'e': 1}]}]}]}}
>>> diff = dd.diff(a,b)
>>> print diff
[('removed', 'a.b.[0].c.[0].d.[0].f', 2)]

```

if keyname within object has dot`.`, we will escape it to `\.`.
```python
>>> import dictdiff as dd
>>> a = {'a.b':1}
>>> dd.flatten(a)
{'a\\.b': 1}

>>> dd.dot_lookup(a, 'a\\.b')
1
>>> dd.dot_lookup(a, 'a\.b')
1

```


dot_lookup
```python
>>> import dictdiff as dd
>>> a = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}, 'b': [1,2]}
>>> res = dd.dot_lookup(a, 'a.b.[0].c.[0].d.[0].f')
>>> print res
2

# any changes on dot_lookup() returned object will not reflected on original object.
>>> res = dd.dot_lookup(a, 'b')
>>> print res
[1, 2]
>>> res[0] = 3
>>> print res
[3, 2]

# but original object stays the same: [1, 2]
>>> print dd.dot_lookup(a, 'b')
[1, 2]
```

dot_lookup_with_parent, changes on returend result `maybe` reflected on original object. you have to use it carefully.
```python
>>> import dictdiff as dd
>>> a = {'a': 1}
>>> parent, res, is_unary = dd.dot_lookup_with_parent(a, 'a')
>>> print "parent: %s, res: %s, is_unary: %s" %(parent, res, is_unary)
parent: {'a': 1}, res: 1, is_unary: True
>>> res = 2
>>> print a
{'a': 1}
# is_unary == True, so modifications directly on res will not reflected on original object.
# you have to modifiy it on parent object.

>>> parent['a'] = 2
>>> print a
{'a': 2}

>>> a = {'a': [1, "h", {'b': 2}]}
>>> parent, res, is_unary = dd.dot_lookup_with_parent(a, 'a.[2]')
>>> print "parent: %s, res: %s, is_unary: %s" %(parent, res, is_unary)
parent: [1, 'h', {'b': 2}], res: {'b': 2}, is_unary: False
>>> res['b'] = 3
>>> print a
{'a': [1, 'h', {'b': 3}]}
# original object has been changed!!
```

patch
```python
>>> import dictdiff as dd
>>> a = {'a': {'b': 1}}
>>> b = {'a': {'b': 2}}
>>> diff = dd.diff(a, b)
>>> print diff
[('changed', 'a.b', (1, 2))]
>>> dd.patch(a, diff)
>>> print a
{'a': {'b': 2}}

# limitations, some modifications will be ignored. !!!
>>> a = {'a': {'b': 1, 'c': {'e': 1}}}
>>> b = {'a': {'b': 1}}
>>> print dd.diff(a,b)
[('removed', 'a.c.e', 1)]

>>> a = {'a': {'b': 1, 'c': {'e': 1}}}
>>> b = {'a': {'b': 1, 'c': {}}}
>>> print dd.diff(a,b)
[('removed', 'a.c.e', 1)]

# path support '.' in keyname
>>> a = {'a.b.c': 1, 'a':{'b':{'c':2}}}
>>> b = {'a.b.c': 2, 'a':{'b':{'c':3}}}
>>> diff = dd.diff(a, b)
>>> dd.patch(a, diff)
>>> print a
{'a': {'b': {'c': 3}}, 'a.b.c': 2}
```
