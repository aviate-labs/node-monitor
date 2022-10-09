import unittest
# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from node_monitor.node_monitor import NodeMonitor, NodesSnapshot
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


    def test_extract_from_diff(self):
        """one node goes down"""
        nodemonitor = NodeMonitor()
        nodemonitor.snapshots.append(self.t0)
        nodemonitor.snapshots.append(self.t1)
        diff    = nodemonitor.get_diff()
        changed = nodemonitor.extract_from_diff(diff)
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






class TestTwoNodesDown(unittest.TestCase):
    """Test two nodes going down"""
    t0 = NodesSnapshot.from_file("tests/t0.json")
    t2 = NodesSnapshot.from_file("tests/t2.json")

    def test_extract_from_diff(self):
        nodemonitor = NodeMonitor()
        nodemonitor.snapshots.append(self.t0)
        nodemonitor.snapshots.append(self.t2)
        diff    = nodemonitor.get_diff()
        changed = nodemonitor.extract_from_diff(diff)
        self.assertEqual(len(changed), 2)
        self.assertGreaterEqual(
            changed[0].items(),
            {
                "node_id": "77fe5-a4oq4-o5pk6-glxt7-ejfpv-tdkrr-24mgs-yuvvz-2tqx6-mowdr-eae",
                "parameter": "status",
                "t1": "UP",
                "t2": "DOWN",
            }.items()
        )
        self.assertGreaterEqual(
            changed[1].items(),
            {
                "node_id": "clb2i-sz6tk-tlcpr-hgnfv-iybzf-ytorn-dmzkz-m2iw2-lpkqb-l455g-pae",
                "parameter": "status",
                "t1": "UP",
                "t2": "DOWN",
            }.items()
        )



class TestOneNodeChangeSubnetId(unittest.TestCase):
    """test one node switching to join another subnet ID"""
    t0 = NodesSnapshot.from_file("tests/t0.json")
    t3 = NodesSnapshot.from_file("tests/t3.json")

    def test_extract_from_diff(self):
        nodemonitor = NodeMonitor()
        nodemonitor.snapshots.append(self.t0)
        nodemonitor.snapshots.append(self.t3)
        diff    = nodemonitor.get_diff()
        changed = nodemonitor.extract_from_diff(diff)
        self.assertEqual(len(changed), 1)
        self.assertGreaterEqual(
            changed[0].items(),
            {
                "node_id": "3ecdy-dk5hn-gmh2r-4wral-uqy4v-4kly2-k6tb2-zqxyl-7ljhv-3xhes-cqe",
                "parameter": "subnet_id",
                "t1": "nl6hn-ja4yw-wvmpy-3z2jx-ymc34-pisx3-3cp5z-3oj4a-qzzny-jbsv3-4qe",
                "t2": "o3ow2-2ipam-6fcjo-3j5vt-fzbge-2g7my-5fz2m-p4o2t-dwlc4-gt2q7-5ae",
            }.items()
        )

class TestOneNodeRemoved(unittest.TestCase):
    """test one entry being completely removed from list"""
    t0 = NodesSnapshot.from_file("tests/t0.json")
    t4 = NodesSnapshot.from_file("tests/t4.json")

    def test_extract_from_diff(self):
        nodemonitor = NodeMonitor()
        nodemonitor.snapshots.append(self.t0)
        nodemonitor.snapshots.append(self.t4)
        diff    = nodemonitor.get_diff()
        changed = nodemonitor.extract_from_diff(diff)
        self.assertGreaterEqual(
            changed[0].items(),
            {
                "node_id": "2ew2x-bmzxs-o6sw6-xbxv6-efhzc-47y5k-vy5ce-luaqo-lecdi-33z4i-gqe",
                "parameter": "removed_node",
            }.items())



class TestOneNodeAddded(unittest.TestCase):
    """test one complete new entry being added to list"""
    t0 = NodesSnapshot.from_file("tests/t0.json")
    t4 = NodesSnapshot.from_file("tests/t4.json")

    def test_extract_from_diff(self):
        nodemonitor = NodeMonitor()
        nodemonitor.snapshots.append(self.t4)
        nodemonitor.snapshots.append(self.t0)
        diff    = nodemonitor.get_diff()
        changed = nodemonitor.extract_from_diff(diff)
        self.assertGreaterEqual(
            changed[0].items(),
            {
                'node_id': '2ew2x-bmzxs-o6sw6-xbxv6-efhzc-47y5k-vy5ce-luaqo-lecdi-33z4i-gqe',
                "parameter": "added_node",
            }.items()
        )


class TestNodePositionsSwapped(unittest.TestCase):
    """test change for two differently ordered datasets"""
    t0 = NodesSnapshot.from_file("tests/t0.json")
    t5 = NodesSnapshot.from_file("tests/t5.json")

    # @unittest.skip("not implemented yet: 'dictionary_item_removed'")
    def test_extract_from_diff(self):
        nodemonitor = NodeMonitor()
        nodemonitor.snapshots.append(self.t0)
        nodemonitor.snapshots.append(self.t5)
        diff    = nodemonitor.get_diff()
        self.assertEqual(diff, {})
