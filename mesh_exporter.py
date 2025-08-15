import sys
import time

from pubsub import pub
from prometheus_client import start_http_server, Gauge, Info, Counter

import meshtastic
import meshtastic.tcp_interface

# simple arg check
if len(sys.argv) < 2:
    print(f"usage: {sys.argv[0]} host")
    sys.exit(1)

metric_user = Info('meshtastic_user', 'meshtastic device info', ['num'])
metric_snr = Gauge('meshtastic_snr', 'meshtastic device metrics', ['num'])
metric_hopsAway = Gauge('meshtastic_hopsAway', 'meshtastic device metrics', ['num'])
metric_lastHeard = Gauge('meshtastic_lastHeard', 'meshtastic device metrics', ['num'])
metric_hopLimit = Gauge('meshtastic_hopLimit', 'meshtastic device metrics', ['num'])
metric_hopStart = Gauge('meshtastic_hopStart', 'meshtastic device metrics', ['num'])
metric_relayNode = Gauge('meshtastic_relayNode', 'meshtastic device metrics', ['num'])
metric_rxRssi = Gauge('meshtastic_rxRssi', 'meshtastic device metrics', ['num'])
#position (optional)
metric_pos_latitude = Gauge('meshtastic_pos_latitude', 'meshtastic device metrics', ['num'])
metric_pos_longitude = Gauge('meshtastic_pos_longitude', 'meshtastic device metrics', ['num'])
metric_pos_altitude = Gauge('meshtastic_pos_altitude', 'meshtastic device metrics', ['num'])
metric_pos_time = Gauge('meshtastic_pos_time', 'meshtastic device metrics', ['num'])
#device metrics (optional)
metric_batteryLevel = Gauge('meshtastic_batteryLevel', 'meshtastic device metrics', ['num'])
metric_voltage = Gauge('meshtastic_voltage', 'meshtastic device metrics', ['num'])
metric_channelUtilization = Gauge('meshtastic_channelUtilization', 'meshtastic device metrics', ['num'])
metric_airUtilTx = Gauge('meshtastic_airUtilTx', 'meshtastic device metrics', ['num'])
metric_uptimeSeconds = Gauge('meshtastic_uptimeSeconds', 'meshtastic device metrics', ['num'])
#enviroment metrics (optional)
metric_temperature = Gauge('meshtastic_temperature', 'meshtastic enviroment metrics', ['num'])
metric_barometricPressure = Gauge('meshtastic_barometricPressure', 'meshtastic enviroment metrics', ['num'])
metric_relativeHumidity = Gauge('meshtastic_relativeHumidity', 'meshtastic enviroment metrics', ['num'])
#Packets
metric_packets = Counter('meshtastic_packets', 'meshtastic enviroment metrics', ['num', 'type'])

def onConnected(interface, topic=pub.AUTO_TOPIC):
    print("connected")

def on_any_packet(packet, interface):
    sender_num = packet.get("from")
    print(packet.get("portnum"))
    metric_packets.labels(num=sender_num,type=packet['decoded']['portnum']).inc()
    node = interface.nodesByNum.get(sender_num)
    if isinstance(node, dict):
        onNodeUpdate(node, interface)

def onNodeUpdate(node, interface):
    print(f"Node: {node}")
    #strings are required
    for key in node['user']:
        node['user'][key] = str(node['user'][key])
    metric_user.labels(num=node['num']).info(node['user'])
    if 'snr' in node:
        metric_snr.labels(num=node['num']).set(node['snr'])
    if 'hopsAway' in node:
        metric_hopsAway.labels(num=node['num']).set(node['hopsAway'])
    if 'lastHeard' in node:
        metric_lastHeard.labels(num=node['num']).set(node['lastHeard'])
    if 'hopLimit' in node:
        metric_hopLimit.labels(num=node['num']).set(node['hopLimit'])
    if 'hopStart' in node:
        metric_hopStart.labels(num=node['num']).set(node['hopStart'])
    if 'relayNode' in node:
        metric_relayNode.labels(num=node['num']).set(node['relayNode'])
    if 'rxRssi' in node:
        metric_rxRssi.labels(num=node['num']).set(node['rxRssi'])
    #position (optional)
    if 'position' in node:
        if 'latitude' in node['position']:
            metric_pos_latitude.labels(num=node['num']).set(node['position']['latitude'])
        if 'longitude' in node['position']:
            metric_pos_longitude.labels(num=node['num']).set(node['position']['longitude'])
        if 'altitude' in node['position']:
            metric_pos_altitude.labels(num=node['num']).set(node['position']['altitude'])
        if 'time' in node['position']:
            metric_pos_time.labels(num=node['num']).set(node['position']['time'])
    #device metrics (optional)
    if 'deviceMetrics' in node:
        if 'batteryLevel' in node['deviceMetrics']:
            metric_batteryLevel.labels(num=node['num']).set(node['deviceMetrics']['batteryLevel'])
        if 'voltage' in node['deviceMetrics']:
            metric_voltage.labels(num=node['num']).set(node['deviceMetrics']['voltage'])
        if 'channelUtilization' in node['deviceMetrics']:
            metric_channelUtilization.labels(num=node['num']).set(node['deviceMetrics']['channelUtilization'])
        if 'airUtilTx' in node['deviceMetrics']:
            metric_airUtilTx.labels(num=node['num']).set(node['deviceMetrics']['airUtilTx'])
        if 'uptimeSeconds' in node['deviceMetrics']:
            metric_uptimeSeconds.labels(num=node['num']).set(node['deviceMetrics']['uptimeSeconds'])
    #enviroment metrics (optional)
    if 'environmentMetrics' in node:
        if 'temperature' in node['environmentMetrics']:
            metric_temperature.labels(num=node['num']).set(node['environmentMetrics']['temperature'])
        if 'barometricPressure' in node['environmentMetrics']:
            metric_barometricPressure.labels(num=node['num']).set(node['environmentMetrics']['barometricPressure'])
        if 'relativeHumidity' in node['environmentMetrics']:
            metric_relativeHumidity.labels(num=node['num']).set(node['environmentMetrics']['relativeHumidity'])

pub.subscribe(onConnected, "meshtastic.connection.established")
pub.subscribe(onNodeUpdate, "meshtastic.node.updated")
pub.subscribe(on_any_packet, "meshtastic.receive")
start_http_server(8000)
try:
    iface = meshtastic.tcp_interface.TCPInterface(hostname=sys.argv[1])
    while True:
        time.sleep(1000)
    iface.close()
except Exception as ex:
    print(f"Error: Could not connect to {sys.argv[1]} {ex}")
    sys.exit(1)
