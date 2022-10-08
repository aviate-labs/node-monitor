import unittest
# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from node_monitor import NodeMonitor, NodesSnapshot
import json
from pprint import pprint



class TestNodesSnapshot(unittest.TestCase):
    def test_from_file(self):
        t0 = NodesSnapshot.from_file("tests/t0.json")
        self.assertIsInstance(t0, list)
        self.assertIsInstance(t0[0], dict)

    def test_from_api(self):
        t0 = NodesSnapshot.from_api(
            "rbn2y-6vfsb-gv35j-4cyvy-pzbdu-e5aum-jzjg6-5b4n5-vuguf-ycubq-zae")
        self.assertIsInstance(t0, list)
        self.assertIsInstance(t0[0], dict)



class TestNodeMonitor(unittest.TestCase):

    t0 = NodesSnapshot.from_file("tests/t0.json")
    t1 = NodesSnapshot.from_file("tests/t1.json")
    t3 = NodesSnapshot.from_file("tests/t3.json")

    def test_update(self):
        """make sure queue ability works to popleft at maxlength"""
        nodemonitor = NodeMonitor()
        nodemonitor.snapshots.append(self.t1)
        nodemonitor.snapshots.append(self.t0)
        nodemonitor.snapshots.append(self.t1)
        self.assertEqual(nodemonitor.snapshots[0], self.t0)
        self.assertEqual(nodemonitor.snapshots[1], self.t1)
        self.assertNotEqual(nodemonitor.snapshots[0],
                            nodemonitor.snapshots[1])


    def test_get_diff(self):
        """make sure diff works properly"""
        nodemonitor = NodeMonitor()
        nodemonitor.snapshots.append(self.t0)
        nodemonitor.snapshots.append(self.t1)
        diff = nodemonitor.get_diff()
        self.assertNotEqual(diff.t1, diff.t2)


    def test_get_changed(self):
        """one node goes down"""
        nodemonitor = NodeMonitor()
        nodemonitor.snapshots.append(self.t0)
        nodemonitor.snapshots.append(self.t1)
        diff    = nodemonitor.get_diff()
        changed = nodemonitor.get_changed(diff)
        self.assertEqual(len(changed), 1)
        self.assertGreaterEqual(
            changed[0].items(),
            {
                "node_id": "77fe5-a4oq4-o5pk6-glxt7-ejfpv-tdkrr-24mgs-yuvvz-2tqx6-mowdr-eae",
                "parameter": "status",
                "t1": "UP",
                "t2": "DOWN",
            }.items()
        )


    def test_filter_by(self):
        """filter relevant dicts from list of dicts"""
        nodemonitor = NodeMonitor
        l0 = [{'a': 1, 'b': 2}, {'a': 9, 'b': 3}, {'a': 1, 'b': 4}]
        d  = {'a': 1} 
        l1 = nodemonitor.filter_by(d, l0)
        self.assertEqual(
            l1,
            [{'a': 1, 'b': 2}, {'a': 1, 'b': 4}]
        )



class TestOneNodeDownEmail(unittest.TestCase):
    t0 = NodesSnapshot.from_file("tests/t0.json")
    t1 = NodesSnapshot.from_file("tests/t1.json")

    @unittest.skip("sends an email")
    def test_run_once(self):
        nodemonitor = NodeMonitor()
        nodemonitor.snapshots.append(self.t0)
        nodemonitor.snapshots.append(self.t1)
        nodemonitor.run_once()



class TestOneNodeGoingDown:
    pass

class TestTwoNodesGoingDown:
    pass

class TestOneDownNodeGoingUp:
    pass






if __name__ == '__main__':
    unittest.main()



