import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize("node,ip", [
    ('nodelist.node.0.ring0_addr', '192.168.168.2'),
    ('nodelist.node.1.ring0_addr', '192.168.168.3'),
    ('nodelist.node.2.ring0_addr', '192.168.168.4'),
])
def test_cmap_file(host, node, ip):
    with host.sudo():
        cmd = "corosync-cmapctl {}".format(node)
        c = host.run_expect([0], cmd)
        assert ip in c.stdout


def test_quorum(host):
    with host.sudo():
        cmd = "corosync-quorumtool -s -p"
        c = host.run_expect([1], cmd)
        assert "Quorum:           2" in c.stdout


def test_listen(host):
    h_ip = {
        'instance1-corosync-udpu': '192.168.168.2',
        'instance2-corosync-udpu': '192.168.168.3',
        'instance3-corosync-udpu': '192.168.168.4',
    }
    v = host.ansible.get_variables()
    socket = "udp://{}:5405".format(h_ip[v['inventory_hostname']])
    assert host.socket(socket).is_listening


def test_transport(host):
    f = host.file('/var/log/corosync/corosync.log')
    assert b'Initializing transport (UDP/IP Unicast)' in f.content
