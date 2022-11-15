import unittest
# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from node_monitor.node_monitor import NodeMonitor, NodesSnapshot, NodeMonitorDiff, ChangeEvent, NodeMonitorEmail
import node_monitor.node_monitor
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
        self.nm = NodeMonitor()
        self.nm.snapshots.append(self.t1)
        self.nm.snapshots.append(self.t0)
        self.nm.snapshots.append(self.t1)
        self.assertEqual(self.nm.snapshots[0], self.t0)
        self.assertEqual(self.nm.snapshots[1], self.t1)
        self.assertNotEqual(self.nm.snapshots[0],
                            self.nm.snapshots[1])


    @unittest.skip("sends an email")
    def test_one_node_down_email(self):
        nm = NodeMonitor()
        nm.snapshots.append(self.t0)
        nm.snapshots.append(self.t1)
        nm.run_once()

    @unittest.skip("sends an email")
    def test_one_node_up_email(self):
        pass

    







class TestNodeMonitorEmail(unittest.TestCase):
    @unittest.skip("sends an email")
    def test_send_email(self):
        recipient = node_monitor.node_monitor.emailRecipients[0]
        NodeMonitorEmail(recipient, "test email").send()



class TestChangeEvent(unittest.TestCase):
    def test__ge__(self):
        self.assertGreaterEqual(
            ChangeEvent(
                change_type="value_change",
                changed_parameter="status",
                t1="UP",
                t2="DOWN"
            ),
            ChangeEvent(
                change_type="value_change",
                changed_parameter="status"
            )
        )

    def test__ge__error_first(self):
        assert not (
            ChangeEvent(
                change_type="value_chasdange",
                changed_parameter="status",
                t1="UP",
                t2="DOWN"
            )
            >=
            ChangeEvent(
                change_type="value_change",
                changed_parameter="status"
            )
        )

    def test__ge__error_second(self):
        assert not (
            ChangeEvent(
                change_type="value_change",
                changed_parameter="status",
                t1="UP",
                t2="DOWN"
            )
            >=
            ChangeEvent(
                change_type="value_chasange",
                changed_parameter="status"
            )
        )
    
    def test_not__ge__(self):
        assert not ( 
            ChangeEvent(
                change_type="value_change",
                changed_parameter="status"
            )
            >=
            ChangeEvent(
                change_type="value_change",
                changed_parameter="status",
                t1="UP",
                t2="DOWN"
            )
        )



class TestNodeMonitorDiff(unittest.TestCase):
    t0 = NodesSnapshot.from_file("tests/t0.json")
    t1 = NodesSnapshot.from_file("tests/t1.json")
    t2 = NodesSnapshot.from_file("tests/t2.json")
    t3 = NodesSnapshot.from_file("tests/t3.json")
    t4 = NodesSnapshot.from_file("tests/t4.json")
    t5 = NodesSnapshot.from_file("tests/t5.json")

    def test_diff(self):
        diff = NodeMonitorDiff(self.t0, self.t1)
        self.assertNotEqual(diff.t1, diff.t2)


    def test_one_node_down(self):
        """test one node going down"""
        diff = NodeMonitorDiff(self.t0, self.t1)
        change_events = diff.aggregate_changes()
        self.assertEqual(len(change_events), 1)
        self.assertGreaterEqual(
            change_events[0],
            ChangeEvent(
                change_type="value_change",
                changed_parameter="status",
                t1="UP",
                t2="DOWN",
                node_id="77fe5-a4oq4-o5pk6-glxt7-ejfpv-tdkrr-24mgs-yuvvz-2tqx6-mowdr-eae"
            )
        )

    def test_two_nodes_down(self):
        """test two nodes going down"""
        diff = NodeMonitorDiff(self.t0, self.t2)
        change_events = diff.aggregate_changes()
        self.assertEqual(len(change_events), 2)
        self.assertGreaterEqual(
            change_events[0],
            ChangeEvent(
                change_type="value_change",
                changed_parameter="status",
                t1="UP",
                t2="DOWN",
                node_id="77fe5-a4oq4-o5pk6-glxt7-ejfpv-tdkrr-24mgs-yuvvz-2tqx6-mowdr-eae"
            )
        )
        self.assertGreaterEqual(
            change_events[1],
            ChangeEvent(
                change_type="value_change",
                changed_parameter="status",
                t1="UP",
                t2="DOWN",
                node_id="clb2i-sz6tk-tlcpr-hgnfv-iybzf-ytorn-dmzkz-m2iw2-lpkqb-l455g-pae"
            )
        )


    def test_one_node_change_subnet_id(self):
        diff = NodeMonitorDiff(self.t0, self.t3)
        change_events = diff.aggregate_changes()
        self.assertEqual(len(change_events), 1)
        self.assertGreaterEqual(
            change_events[0],
            ChangeEvent(
                node_id="3ecdy-dk5hn-gmh2r-4wral-uqy4v-4kly2-k6tb2-zqxyl-7ljhv-3xhes-cqe",
                change_type="value_change",
                changed_parameter="subnet_id",
                t1="nl6hn-ja4yw-wvmpy-3z2jx-ymc34-pisx3-3cp5z-3oj4a-qzzny-jbsv3-4qe",
                t2="o3ow2-2ipam-6fcjo-3j5vt-fzbge-2g7my-5fz2m-p4o2t-dwlc4-gt2q7-5ae"
            )
        )

    def test_one_node_removed(self):
        diff = NodeMonitorDiff(self.t0, self.t4)
        change_events = diff.aggregate_changes()
        self.assertGreaterEqual(
            change_events[0],
            ChangeEvent(
                node_id="2ew2x-bmzxs-o6sw6-xbxv6-efhzc-47y5k-vy5ce-luaqo-lecdi-33z4i-gqe",
                change_type="node_removed",
            )
        )

    def test_one_node_added(self):
        diff = NodeMonitorDiff(self.t4, self.t0)
        change_events = diff.aggregate_changes()
        self.assertGreaterEqual(
            change_events[0],
            ChangeEvent(
                node_id="2ew2x-bmzxs-o6sw6-xbxv6-efhzc-47y5k-vy5ce-luaqo-lecdi-33z4i-gqe",
                change_type="node_added",
            )
        )

    def test_node_positions_swapped(self):
        diff = NodeMonitorDiff(self.t0, self.t5)
        self.assertEqual(diff, {})
        









