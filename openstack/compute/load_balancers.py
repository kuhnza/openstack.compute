from openstack.compute import base

class VirtualIPType(object):
    PUBLIC = 'PUBLIC' # Virtual IP on the public internet.
    SERVICENET = 'SERVICENET' # Virtual IP on the Rackspace private ServiceNet.

class VirtualIPVersion(object):
    IPV4 = 'IPV4'
    IPV6 = 'IPV6'

class VirtualIP(base.Resource):
    def __repr__(self):
        return "<Node: %s>" % self.address

    def remove(self):
        """
        Remove this virtual IP from the associated load balancer.
        """
        self.manager.remove(self)

class VirtualIPManager(base.ManagerWithFind):
    resource_class = VirtualIP

    def __init__(self, api, load_balancer):
        super(VirtualIPManager, self).__init__(api)
        self.load_balancer = load_balancer

    def list(self):
        """
        Get a list of virtual IPs.
        :rtype: list of :class:`VirtualIP`
        """
        return self._list("/loadbalancers/%s/virtualips" % self.load_balancer.id, "virtualIps")

    def add(self, type, ip_version=None):
        """
        Add a virtual IP to the load balancer.

        :param type: The type of virtualIp to add. See :class:`VirtualIPType` for valid values.
        :param ip_version: The IP version to use. See :class:`VirtualIPVersion` for valid values.
        """
        body = {
            "type": type
        }
        if ip_version:
            body["ipVersion"] = ip_version
        return self._create("/loadbalancers/%s/virtualips" % self.load_balancer.id, body)

    def remove(self, virtual_ip):
        self._delete("/loadbalancers/%s/virtualips/%s" % (self.load_balancer.id, base.getid(virtual_ip)))

class NodeType(object):
    PRIMARY = 'PRIMARY' # Nodes defined as PRIMARY are in the normal rotation to receive traffic from the load balancer.
    SECONDARY = 'SECONDARY'  # Nodes defined as SECONDARY are only in the rotation to receive traffic from the load balancer when all the primary nodes fail.

class NodeCondition(object):
    ENABLED = 'ENABLED' # Node is permitted to accept new connections.
    DISABLED = 'DISABLED' # Node is not permitted to accept any new connections regardless of session persistence configuration. Existing connections are forcibly terminated.
    DRAINING = 'DRAINING' # Node is allowed to service existing established connections and connections that are being directed to it as a result of the session persistence configuration.

class Node(base.Resource):
    def __repr__(self):
        return "<Node: %s>" % self.address

    def update(self, condition=None, node_type=None, weight=None):
        """
        Update the condition, type or weighting of the node.

        :param condition: Condition for the node, which determines its role 
                          within the load balancer. See :class:`NodeCondition` 
                          for valid values.
        :param node_type: The type of node. See :class:`NodeType` for valid values. 
        :param weight: Weight of node. If the WEIGHTED_ROUND_ROBIN load balancer 
                       algorithm mode is selected, then the user should assign 
                       the relevant weight to the node using the weight 
                       attribute for the node. Must be an integer from 1 to 100.
        """
        self.manager.update(self, condition, node_type, weight)

    def remove(self):
        """
        Remove this node from the associated load balancer.
        """
        self.manager.remove(self)

class NodeManager(base.ManagerWithFind):
    resource_class = Node

    def __init__(self, api, load_balancer):
        super(NodeManager, self).__init__(api)
        self.load_balancer = load_balancer

    def get(self, node):
        """
        Get a node from the load balancer.

        :param node: ID of the :class:`Node` to get.
        :rtype: :class:`Node`
        """
        return self._get("/loadbalancers/%s/nodes/%s" % (self.load_balancer.id, base.getid(node)), "node")

    def list(self):
        """
        Get a list of nodes registered with the load balancer.
        :rtype: list of :class:`Node`
        """
        return self._list("/loadbalancers/%s/nodes" % self.load_balancer.id, "nodes")

    def add(self, address, port, condition, node_type=None, weight=None):
        """
        Add a node to the load balancer.

        :param address: IP address or domain name for the node.
        :param port: Port number for the service you are load balancing.
        :param condition: Condition for the node, which determines its role 
                          within the load balancer. See :class:`NodeCondition`
                          for valid values.
        :param node_type: Type of node to add. See :class:`NodeType` for valid values.
        :param weight: Weight of node to add. If the WEIGHTED_ROUND_ROBIN load 
                       balancer algorithm mode is selected, then the user should 
                       assign the relevant weight to the node using the weight 
                       attribute for the node. Must be an integer from 1 to 100.
        """
        body = {
            "nodes": {
                "address": address,
                "port": port,
                "condition": condition
            }
        }
        if node_type:
            body["nodes"]["type"] = node_type
        if weight:
            body["nodes"]["weight"] = weight

        return self._create("/loadbalancers/%s/nodes" % self.load_balancer.id, body, "nodes")

    def update(self, node, condition=None, node_type=None, weight=None):
        """
        Update the condition, type or weighting of the node.

        :param node: The :class:`Node` (or its ID) to update.
        :param condition: Condition for the node, which determines its role 
                          within the load balancer. See :class:`NodeCondition` 
                          for valid values.
        :param node_type: The type of node. See :class:`NodeType` for valid values. 
        :param weight: Weight of node. If the WEIGHTED_ROUND_ROBIN load balancer 
                       algorithm mode is selected, then the user should assign 
                       the relevant weight to the node using the weight 
                       attribute for the node. Must be an integer from 1 to 100.
        """
        if condition is None and node_type is None and weight is None:
            return

        body = {"node": {}}
        if condition:
            body["node"]["condition"] = condition
        if node_type:
            body["node"]["type"] = node_type
        if weight:
            body["node"]["weight"] = weight

        self._update("/loadbalancers/%s/nodes/%s" % (self.load_balancer.id, base.getid(node)), body)

    def remove(self, node):
        """
        Remove the node from the load balancer.

        :param node: The :class:`Node` (or its ID) to remove.
        """
        self._delete("/loadbalancers/%s/nodes/%s" % (self.load_balancer.id, base.getid(node)))

class LoadBalancer(base.Resource):
    def __init__(self, manager, info):
        super(LoadBalancer, self).__init__(manager, info)
        self.nodes = NodeManager(manager.api, self)
        self.virtual_ips = VirtualIPManager(manager.api, self)

    def __repr__(self):
        return "<LoadBalancer: %s>" % self.name

    def delete(self):
        """
        Delete/remove this load balancer.
        """
        self.manager.delete(self)

    def update(self, name=None, algorithm=None, protocol=None, port=None):
        """
        Update the name, algorithm, protocol or port for this load balancer.

        :param name: Update the load balancer's name.
        :param algorithm: Update the load balancer's algorithm for directing traffic between back-end nodes
        :param protocol: Update the protocol the load balancer will accept connections for
        :param port: Update the port which the load balance is listening on
        """
        self.manager.update(self, name, algorithm, protocol, port)

    @property
    def public_ip(self):
        """
        Shortcut to get this server's primary public IP address.
        """
        if self.addresses['public']:
            return self.addresses['public'][0]
        else:
            return u''

    @property
    def private_ip(self):
        """
        Shortcut to get this server's primary private IP address.
        """
        if self.addresses['private']:
            return self.addresses['private'][0]
        else:
            return u''

class LoadBalancerManager(base.ManagerWithFind):
    resource_class = LoadBalancer

    def get(self, load_balancer):
        """
        Get a load balancer.

        :param load_balancer: ID of the :class:`LoadBalancer` to get.
        :rtype: :class:`LoadBalancer`
        """
        return self._get("/loadbalancers/%s" % base.getid(load_balancer), "loadBalancer")

    def list(self):
        """
        Get a list of load balancers.
        :rtype: list of :class:`LoadBalancer`
        """
        return self._list("/loadbalancers", "loadBalancers")

    def create(self, name, nodes, protocol, virtual_ips, access_list=None, 
               algorithm=None, connection_logging=None, connection_throttle=None, 
               health_monitor=None, metadata=None, port=None, session_persistence=None):
        """
        Create a new load balancer.

        :param name: Name of the load balancer to create. The name must be 128 
                     characters or less in length, and all UTF-8 characters are 
                     valid.
        :param nodes: List of dicts representing nodes to be added to the load balancer.
        :param protocol: Protocol of the service which is being load balanced.
        :param virtual_ips: A dict representing a virtual IP to add along with the 
                            creation of the load balancer.
        :param access_list: Allows fine-grained network access controls to be 
                            applied to the load balancer's virtual IP address.
        :param algorithm: Algorithm that defines how traffic should be directed 
                          between back-end nodes.
        :param connection_logging: Current connection logging configuration. 
        :param connection_throttle: Specifies limits on the number of 
                                    connections per IP address to help mitigate 
                                    malicious or abusive traffic to your applications.
        :param health_monitor: The type of health monitor check to perform to 
                               ensure that the service is performing properly.
        :param metadata: Information (metadata) that can be associated with each 
                         load balancer for the client's personal use.
        :param port: Port number for the service you are load balancing.
        :param session_persistence: Specifies whether multiple requests from 
                                    clients are directed to the same node.
        """
        body = {"loadBalancer": {
            "name": name,
            "nodes": nodes,
            "protocol": protocol,
            "virtualIps": virtual_ips
        }}

        if access_list:
            body["accessList"] = access_list
        if algorithm:
            body["algorithm"] = algorithm
        if connection_logging:
            body["connectionLogging"] = connection_logging
        if connection_throttle:
            body["connectionThrottle"] = connection_throttle
        if health_monitor:
            body["healthMonitor"] = health_monitor
        if metadata:
            body["metadata"] = metadata
        if port:
            body["port"] = port
        if session_persistence:
            body["sessionPersistence"] = session_persistence

        return self._create('/loadbalancers', body, 'loadBalancer')

    def update(self, load_balancer, name=None, algorithm=None, protocol=None, port=None):
        """
        Update the name, algorithm, protocol or port of a load balancer.

        :param load_balancer: The :class:`LoadBalancer` (or its ID) to update.
        :param name: The new name for the load balancer. The name must be 128 
                     characters or less in length, and all UTF-8 characters are valid.
        :param algorithm: Algorithm that defines how traffic should be directed 
                          between back-end nodes.
        :param protocol: Protocol of the service which is being load balanced.
        :param port: Port number for the service you are load balancing.
        """

        if name is None and algorithm is None and protocol is None and port is None:
            return

        body = {"loadBalancer": {}}
        if name:
            body["loadBalancer"]["name"] = name
        if algorithm:
            body["loadBalancer"]["algorithm"] = algorithm
        if protocol:
            body["loadBalancer"]["protocol"] = protocol
        if port:
            body["loadBalancer"]["port"] = port   
        self._update("/loadbalancers/%s" % base.getid(load_balancer), body)

    def delete(self, load_balancer):
        """
        Delete this load balancer.

        :param server: The :class:`LoadBalancer` (or its ID) to delete.
        """
        self._delete("/loadbalancers/%s" % base.getid(load_balancer))


