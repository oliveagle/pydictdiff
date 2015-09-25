# encoding=utf-8
__author__ = 'rhtang'

import unittest
import dictdiff
import benchmark

class FlattenTest(unittest.TestCase):
    
    # @unittest.skip("")
    def test_flatten_1(self):
        obj = {'a': 1}
        fobj = dictdiff.flatten(obj)
        self.assertEqual(len(fobj), 1)
        self.assertEqual(fobj['a'], 1)

    # @unittest.skip("")
    def test_flatten_2(self):
        obj = {'a': {'b': 1}}
        fobj = dictdiff.flatten(obj)
        self.assertEqual(len(fobj), 1)
        self.assertEqual(fobj.keys()[0], 'a.b')
        self.assertEqual(fobj['a.b'], 1)

        obj = {'a': {'b': 1, 'c':2}}
        fobj = dictdiff.flatten(obj)
        self.assertEqual(len(fobj), 2)
        self.assertEqual(fobj['a.c'], 2)

        obj = {'a': {'b': 1}, 'b': 2}
        fobj = dictdiff.flatten(obj)
        self.assertEqual(len(fobj), 2)
        self.assertEqual(fobj['a.b'], 1)
        self.assertEqual(fobj['b'], 2)

    # @unittest.skip("")
    def test_flatten_3(self):
        obj = {'a': ['b',1]}
        fobj = dictdiff.flatten(obj)
        self.assertEqual(len(fobj), 2)
        self.assertEqual(fobj['a.[0]'],'b')
        self.assertEqual(fobj['a.[1]'], 1)

    # @unittest.skip("")
    def test_flatten_4(self):
        obj = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}}
        fobj = dictdiff.flatten(obj)
        # print fobj
        self.assertEqual(len(fobj), 2)
        self.assertEqual(fobj['a.b.[0].c.[0].d.[0].e'], 1)
        self.assertEqual(fobj['a.b.[0].c.[0].d.[0].f'], 2)

    # @unittest.skip("")
    def test_flatten_5(self):
        obj = ['a', 1]
        fobj = dictdiff.flatten(obj)
        # print fobj
        self.assertEqual(fobj, {})

    # @unittest.skip("")
    def test_flatten_6(self):
        # `.` in key name is not allowed
        obj = {'a.b': {'c':1}}
        with self.assertRaises(KeyError):
            fobj = dictdiff.flatten(obj)
        obj = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f.1': 2}]}]}]}}
        with self.assertRaises(KeyError):
            fobj = dictdiff.flatten(obj)

    # @unittest.skip("")
    def test_flatten_x(self):
        print ""
        obj = {
            "client": {
                "heart_beat": "1s",
                "metric_enabled": True,
                "transport_kafka": {
                    "broker_list": [
                        "10.0.0.1:9092",
                        "10.0.0.2:9092"
                    ]
            },
            "groups": [
                {
                    "prefix:": "oletest", 
                    "collector_win_pdh": [
                        {"interval": "15s"}, 
                        {"interval": "30s"}
                    ]
                }, {
                    "prefix:": "xxxxx", 
                    "collector_win_pdh": [
                        {"interval": "15s", "queries":["q1", "q2", "q3"]}
                    ]
                }
            ]}
        }
        fobj = dictdiff.flatten(obj)
        for k, v in fobj.iteritems():
            print k ,"=", v

class DiffTest(unittest.TestCase):

    # @unittest.skip("")
    def test_diff_1(self):
        # simple change
        a = {'a': 1}
        b = {'a': 2}
        diff = dictdiff.diff(a, b)
        self.assertEqual(len(diff), 1)
        # print diff
        res = diff[0]
        self.assertEqual(res[0], "changed")
        self.assertEqual(res[1], "a")
        self.assertEqual(res[2][0], 1)
        self.assertEqual(res[2][1], 2)

    # @unittest.skip("")
    def test_diff_2(self):
        # simple add
        a = {'a': 1}
        b = {'a': 1, 'b': 2}
        diff = dictdiff.diff(a, b)
        self.assertEqual(len(diff), 1)
        # print diff
        res = diff[0]
        self.assertEqual(res[0], "added")
        self.assertEqual(res[1], "b")
        self.assertEqual(res[2], 2)

    # @unittest.skip("")
    def test_diff_2(self):
        # simple removed
        a = {'a': 1}
        b = {}
        diff = dictdiff.diff(a, b)
        self.assertEqual(len(diff), 1)
        # print diff
        res = diff[0]
        self.assertEqual(res[0], "removed")
        self.assertEqual(res[1], "a")
        self.assertEqual(res[2], 1)    

    # @unittest.skip("")
    def test_diff_3(self):
        a = {'a': 1}
        b = {'b': 1}
        diff = dictdiff.diff(a,b)
        self.assertEqual(len(diff), 2)
        print diff
        res = diff[0]
        self.assertEqual(res[0], "added")
        self.assertEqual(res[1], "b")
        self.assertEqual(res[2], 1)

        res = diff[1]
        self.assertEqual(res[0], "removed")
        self.assertEqual(res[1], "a")
        self.assertEqual(res[2], 1)            

    # @unittest.skip("")
    def test_diff_4(self):
        a = {'a': {'b': 1, 'c':2}}
        b = {'a': {'b': 1, 'c':3}}
        diff = dictdiff.diff(a,b)
        self.assertEqual(len(diff), 1)
        print diff
        res = diff[0]
        self.assertEqual(res[0], "changed")
        self.assertEqual(res[1], "a.c")
        self.assertEqual(res[2][0], 2)
        self.assertEqual(res[2][1], 3)

    # @unittest.skip("")
    def test_diff_5(self):
        a = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}}
        b = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 3}]}]}]}}
        diff = dictdiff.diff(a,b)
        self.assertEqual(len(diff), 1)
        print diff
        res = diff[0]
        self.assertEqual(res[0], "changed")
        self.assertEqual(res[1], 'a.b.[0].c.[0].d.[0].f')
        self.assertEqual(res[2][0], 2)
        self.assertEqual(res[2][1], 3)

    # @unittest.skip("")
    def test_diff_6(self):
        a = {'a':{'b':[{'c': [{'d':[{'e': 1}]}]}]}}
        b = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 3}]}]}]}}
        diff = dictdiff.diff(a,b)
        self.assertEqual(len(diff), 1)
        print diff
        res = diff[0]
        self.assertEqual(res[0], "added")
        self.assertEqual(res[1], 'a.b.[0].c.[0].d.[0].f')
        self.assertEqual(res[2], 3)

    # @unittest.skip("")
    def test_diff_7(self):
        a = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}}
        b = {'a':{'b':[{'c': [{'d':[{'e': 1}]}]}]}}
        diff = dictdiff.diff(a,b)
        self.assertEqual(len(diff), 1)
        print diff
        res = diff[0]
        self.assertEqual(res[0], "removed")
        self.assertEqual(res[1], 'a.b.[0].c.[0].d.[0].f')
        self.assertEqual(res[2], 2)

    # @unittest.skip("")
    def test_diff_8(self):
        a = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}, 'b': 1}
        b = {'b': 1}
        diff = dictdiff.diff(a,b)
        self.assertEqual(len(diff), 2)
        print diff
        self.assertEqual(diff[0][0], "removed")
        self.assertEqual(diff[1][0], "removed")

    # @unittest.skip("")
    def test_flatten_x(self):
        a = {
            "client": {
                "heart_beat": "1s",
                "metric_enabled": True,
                "transport_kafka": {
                    "broker_list": [
                        "10.0.0.1:9092",
                        "10.0.0.2:9092"
                    ]
            },
            "groups": [
                {
                    "prefix:": "oletest", 
                    "collector_win_pdh": [
                        {"interval": "15s"}, 
                        {"interval": "30s"}
                    ]
                }, {
                    "prefix:": "xxxxx", 
                    "collector_win_pdh": [
                        {"interval": "15s", "queries":["q1", "q2", "q3"]}
                    ]
                }
            ]}
        }
        b = {
            "client": {
                "heart_beat": "1s",
                "metric_enabled": True,
                "transport_kafka": {
                    "broker_list": [
                        "10.0.0.1:9092",
                        "10.0.0.2:9092",
                        "10.0.0.3:9092"
                    ]
            },
            "groups": [
                {
                    "collector_win_pdh": [
                        {"interval": "10s"},
                        {"interval": "15s"} 
                    ],
                    "prefix:": "oletest", 
                }
            ]}
        }
        diff = dictdiff.diff(a,b)
        # print diff
        print ""
        for x in diff:
            print x
        # self.assertEqual(len(diff), 2)

class Benchmark_x(benchmark.Benchmark):

    each = 100
    
    def setUp(self):
        # Only using setUp in order to subclass later
        # Can also specify tearDown, eachSetUp, and eachTearDown
        self.size = 100

    def test_flatten_1(self):
        obj = {'a': 1}
        for x in xrange(self.size):
            dictdiff.flatten(obj)

    def test_flatten_2(self):
        obj = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}}
        for x in xrange(self.size):
            dictdiff.flatten(obj)

    def test_flatten_x(self):
        obj = {
            "client": {
                "heart_beat": "1s",
                "metric_enabled": True,
                "transport_kafka": {
                    "broker_list": [
                        "10.0.0.1:9092",
                        "10.0.0.2:9092"
                    ]
            },
            "groups": [
                {
                    "prefix:": "oletest", 
                    "collector_win_pdh": [
                        {"interval": "15s"}, 
                        {"interval": "30s"}
                    ]
                }, {
                    "prefix:": "xxxxx", 
                    "collector_win_pdh": [
                        {"interval": "15s", "queries":["q1", "q2", "q3"]}
                    ]
                }
            ]}
        }
        for x in xrange(self.size):
            dictdiff.flatten(obj)

    def test_diff_1(self):
        a = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}}
        b = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 3}]}]}]}}
        for x in xrange(self.size):
            dictdiff.diff(a,b)

    def test_diff_x(self):
        a = {
            "client": {
                "heart_beat": "1s",
                "metric_enabled": True,
                "transport_kafka": {
                    "broker_list": [
                        "10.0.0.1:9092",
                        "10.0.0.2:9092"
                    ]
            },
            "groups": [
                {
                    "prefix:": "oletest", 
                    "collector_win_pdh": [
                        {"interval": "15s"}, 
                        {"interval": "30s"}
                    ]
                }, {
                    "prefix:": "xxxxx", 
                    "collector_win_pdh": [
                        {"interval": "15s", "queries":["q1", "q2", "q3"]}
                    ]
                }
            ]}
        }
        b = {
            "client": {
                "heart_beat": "1s",
                "metric_enabled": True,
                "transport_kafka": {
                    "broker_list": [
                        "10.0.0.1:9092",
                        "10.0.0.2:9092",
                        "10.0.0.3:9092"
                    ]
            },
            "groups": [
                {
                    "collector_win_pdh": [
                        {"interval": "10s"},
                        {"interval": "15s"} 
                    ],
                    "prefix:": "oletest", 
                }
            ]}
        }
        diff = dictdiff.diff(a,b)
        for x in xrange(self.size):
            dictdiff.diff(a,b)


class DotLookupTest(unittest.TestCase):

    # @unittest.skip("")
    def test_dot_lookup_1(self):
        # simple change
        a = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}, 'b': 1}
        res = dictdiff.dot_lookup(a, 'a')
        print res
        self.assertEqual(type(res), type({}))
        res = dictdiff.dot_lookup(a, 'a.b')
        self.assertEqual(type(res), type([]))

        res = dictdiff.dot_lookup(a, 'a.b.[0].c.[0].d.[0].f')
        print res
        self.assertEqual(res, 2)

        res = dictdiff.dot_lookup(a, 'a.b.[0].c.[0].d.[0]')
        print res
        self.assertEqual(res['e'], 1)
        self.assertEqual(res['f'], 2)

    def test_dot_lookup_2(self):
        """
        make sure we cannot modify original object with return result of dot_lookup
        """
        a = {'a': 1}
        res = dictdiff.dot_lookup(a, 'a')
        res = 2
        self.assertEqual(a['a'], 1)

        a = {'a': [1, "h", {'b': 2}]}
        res = dictdiff.dot_lookup(a, 'a')
        res[0] = 2
        self.assertEqual(a['a'][0], 1)

        res = dictdiff.dot_lookup(a, 'a.[2]')
        res['b'] = 3
        self.assertEqual(a['a'][2]['b'], 2)

    # @unittest.skip("")
    def test_dot_lookup_with_parent_unary_true(self):
        a = {'a': 1}
        parent, res, is_unary = dictdiff.dot_lookup_with_parent(a, 'a')
        self.assertTrue(is_unary)
        # when is_unary is true, modification on res will not be reflected on 
        # original object.
        res = 2
        self.assertEqual(a['a'], 1)
        # but modifications on parent will be re reflected on original object.
        parent['a'] = 2
        self.assertEqual(a['a'], 2)

        a = {'a': 'b'}
        parent, res, is_unary = dictdiff.dot_lookup_with_parent(a, 'a')
        self.assertTrue(is_unary)
        res = 'c'
        self.assertEqual(a['a'], 'b')
        parent['a'] = 'c'
        self.assertEqual(a['a'], 'c')

        a = {'a': True}
        parent, res, is_unary = dictdiff.dot_lookup_with_parent(a, 'a')
        self.assertTrue(is_unary)
        res = False
        self.assertEqual(a['a'], True)
        parent['a'] = False
        self.assertEqual(a['a'], False)

        a = {'a': long(1)}
        parent, res, is_unary = dictdiff.dot_lookup_with_parent(a, 'a')
        self.assertTrue(is_unary)
        res = long(2)
        self.assertEqual(a['a'], long(1))
        parent['a'] = long(2)
        self.assertEqual(a['a'], long(2))

        a = {'a': u'中文'}
        parent, res, is_unary = dictdiff.dot_lookup_with_parent(a, 'a')
        self.assertTrue(is_unary)
        res = False
        self.assertEqual(a['a'], u'中文')
        parent['a'] = False
        self.assertEqual(a['a'], False)


    # @unittest.skip("")
    def test_dot_lookup_with_parent_unary_false(self):
        a = {'a': [1, "h", {'b': 2}]}
        parent, res, is_unary = dictdiff.dot_lookup_with_parent(a, 'a')
        self.assertFalse(is_unary)
        # when is_unary == false, modifications on res will directly reflected on original
        # object.  but with some exceptions, see below
        # print '---------: ', a
        res[0] = 2
        self.assertEqual(a['a'][0], 2)

        # exceptions:
        #   del(res)     : will not delete on original object
        #   res = None   : will not work

        # print '---------: ', a
        del(res)
        self.assertEqual(a['a'][0], 2)
        # print '---------: ', a

        res = None
        self.assertEqual(a['a'][0], 2)
        # print '---------: ', a

        parent.pop('a')
        self.assertEqual(a, {})
        # print '---------: ', a


        a = {'a': [1, "h", {'b': 2}]}
        # print "parent: %s, res: %s" % (parent, res)
        parent, res, is_unary = dictdiff.dot_lookup_with_parent(a, 'a.[2]')
        self.assertFalse(is_unary)
        res['b'] = 3
        self.assertEqual(a['a'][2]['b'], 3)

        a = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}, 'b': 1}
        parent, res, is_unary = dictdiff.dot_lookup_with_parent(a, 'a.b.[0].c.[0].d.[0]')
        self.assertFalse(is_unary)
        print "parent: %s, res: %s" % (parent, res)
        res['f'] = 100
        parent, res, is_unary = dictdiff.dot_lookup_with_parent(a, 'a.b.[0].c.[0].d.[0].f')
        self.assertEqual(res, 100)

class PathTest(unittest.TestCase):

    # @unittest.skip("")
    def test_path_1(self):
        a = {'a':1}
        b = {'a':2}
        diff1 = dictdiff.diff(a, b)
        dictdiff.patch(a, diff1)
        self.assertEqual(a['a'], 2)

        diff2 = dictdiff.diff(a, b)
        self.assertEqual(len(diff2), 0)

        a = {'a': {'b': 1}}
        b = {'a': {'b': 2}}
        diff1 = dictdiff.diff(a, b)
        dictdiff.patch(a, diff1)
        self.assertEqual(a['a']['b'], 2)

        a = {'a': {'b': 1}}
        b = {'a': {'c': 1}}
        diff1 = dictdiff.diff(a, b)

        dictdiff.patch(a, diff1)
        # print a
        # print "0------------------------"

        self.assertEqual(a['a']['c'], 1)
        with self.assertRaises(KeyError):
            a['a']['b']

        a = {'a': {'b': 1, 'c': {'e': 1}}}
        b = {'a': {'b': 1}}
        diff1 = dictdiff.diff(a, b)
        print "0------------------------"
        print diff1
        dictdiff.patch(a, diff1)
        print a
        print "0------------------------"

        a = {'a': {'b': 1, 'c': {'e': 1}}}
        b = {'a': {'b': 1, 'c': {}}}
        diff1 = dictdiff.diff(a, b)
        print "0------------------------"
        print diff1
        dictdiff.patch(a, diff1)
        print a
        print "0------------------------"

    # @unittest.skip("")
    def test_patch_2(self):
        a = {'a':{'b':[{'c': [{'d':[{'e': 1, 'f': 2}]}]}]}, 'b': 1}
        b = {'a':{'b':[{'c': [{'d':[{'e': 1}]}]}]}, 'b': 5}
        print " 1 ====================-----"
        print " 1 ---- ", a
        diff1 = dictdiff.diff(a, b)
        print diff1
        dictdiff.patch(a, diff1)
        print " 1 ---- ", a
        print " 1 ====================-----"

        with self.assertRaises(KeyError):
            dictdiff.dot_lookup(a, 'a.b.[0].c.[0].d.[0].f')
        self.assertEqual(a['b'], 5)


if __name__ == '__main__':
    # benchmark.main(format="markdown", numberFormat="%.4g")
    unittest.main()
