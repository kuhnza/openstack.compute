import StringIO
from nose.tools import assert_equal
from fakeserver import FakeServer
from openstack.compute.load_balancers import *
from utils import assert_isinstance

cs = FakeServer()


def test_list_load_balancers():
    lbs = cs.load_balancers.list()
    cs.assert_called('GET', '/loadbalancers')
    [assert_isinstance(lb, LoadBalancer) for lb in lbs]

def test_get_load_balancer_details():
    lb = cs.load_balancers.get(71)
    cs.assert_called('GET', '/loadbalancers/71')
    assert_isinstance(lb, LoadBalancer)
    assert_equal(lb.id, 71)
    assert_equal(lb.status, 'ACTIVE')

def test_create_load_balancer():
    lb = cs.load_balancers.create(
        name='my-lb',
        protocol='HTTP',
        nodes=[{'address': '10.0.0.1', 'protocol': 'HTTP', 'condition': NodeCondition.ENABLED}],
        virtual_ips=[{'type': VirtualIPType.PUBLIC}]
    )
    cs.assert_called('POST', '/loadbalancers')
    assert_isinstance(lb, LoadBalancer)

def test_update_load_balancer():
    lb = cs.load_balancers.get(71)

    # Update via instance
    lb.update(name='hi')
    cs.assert_called('PUT', '/loadbalancers/71')
    lb.update(name='hi', protocol='HTTPS')
    cs.assert_called('PUT', '/loadbalancers/71')

    # Silly, but not an error
    lb.update()

    # Update via manager
    cs.load_balancers.update(lb, name='hi')
    cs.assert_called('PUT', '/loadbalancers/71')
    cs.load_balancers.update(71, protocol='HTTPS')
    cs.assert_called('PUT', '/loadbalancers/71')
    cs.load_balancers.update(lb, name='hi', protocol='HTTPS')
    cs.assert_called('PUT', '/loadbalancers/71')

def test_load_balancer_list_virtual_ips():
    lb = cs.load_balancers.get(71)
    virtual_ips = lb.virtual_ips.list()
    cs.assert_called('GET', '/loadbalancers/71/virtualips')
    [assert_isinstance(virtual_ip, VirtualIP) for virtual_ip in virtual_ips]

def test_load_balancer_add_virtual_ip():
    lb = cs.load_balancers.get(71)
    virtual_ip = lb.virtual_ips.add(type='PUBLIC', ip_version='IPV6')
    cs.assert_called('POST', '/loadbalancers/71/virtualips')
    assert_isinstance(virtual_ip, VirtualIP)

def test_load_balancer_remove_virtual_ip():
    lb = cs.load_balancers.get(71)
    lb.virtual_ips.remove(1000)
    cs.assert_called('DELETE', '/loadbalancers/71/virtualips/1000')

def test_load_balancer_list_nodes():
    lb = cs.load_balancers.get(71)
    nodes = lb.nodes.list()
    cs.assert_called('GET', '/loadbalancers/71/nodes')
    [assert_isinstance(node, Node) for node in nodes]   

def test_load_balancer_node_details():
    lb = cs.load_balancers.get(71)
    node = lb.nodes.get(410)
    cs.assert_called('GET', '/loadbalancers/71/nodes/410')
    assert_isinstance(node, Node)
    assert_equal(node.id, 410)

def test_load_balancer_add_node():
    lb = cs.load_balancers.get(71)
    node = lb.nodes.add(address='10.0.0.1', port=80, condition=NodeCondition.ENABLED)
    cs.assert_called('POST', '/loadbalancers/71/nodes')
    assert_equal(node[0].id, 410)

def test_load_balancer_update_node():
    lb = cs.load_balancers.get(71)
    
    node = lb.nodes.get(410)

    # Update via instance
    node.update(condition=NodeCondition.DISABLED)
    cs.assert_called('PUT', '/loadbalancers/71/nodes/410')
    node.update(condition=NodeCondition.DISABLED, node_type=NodeType.SECONDARY, weight=10)
    cs.assert_called('PUT', '/loadbalancers/71/nodes/410')

    # Silly, but not an error
    node.update()

    # Update via manager
    lb.nodes.update(node, condition=NodeCondition.DISABLED)
    cs.assert_called('PUT', '/loadbalancers/71/nodes/410')
    lb.nodes.update(410, condition=NodeCondition.DISABLED)
    cs.assert_called('PUT', '/loadbalancers/71/nodes/410')
    lb.nodes.update(node, condition=NodeCondition.DISABLED, node_type=NodeType.SECONDARY, weight=10)
    cs.assert_called('PUT', '/loadbalancers/71/nodes/410')

def test_load_balancer_delete_node():
    lb = cs.load_balancers.get(71)
        
    node = lb.nodes.get(410)

    # Remove via instance
    node.remove()
    cs.assert_called('DELETE', '/loadbalancers/71/nodes/410')

    # Remove via manager
    lb.nodes.remove(node)
    cs.assert_called('DELETE', '/loadbalancers/71/nodes/410')
    lb.nodes.remove(410)
    cs.assert_called('DELETE', '/loadbalancers/71/nodes/410')
