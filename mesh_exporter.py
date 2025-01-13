import sys
import time

from pubsub import pub
from prometheus_client import start_http_server, Gauge, Info

import meshtastic
import meshtastic.tcp_interface

# simple arg check
if len(sys.argv) < 2:
    print(f"usage: {sys.argv[0]} host")
    sys.exit(1)

labels = ['num']
metric_user = Info('meshtastic_user', 'meshtastic device info', labels)
metric_uptimeSeconds = Gauge('meshtastic_uptimeSeconds', 'meshtastic device metrics', labels)
metric_snr = Gauge('meshtastic_snr', 'meshtastic device metrics', labels)
metric_hopsAway = Gauge('meshtastic_hopsAway', 'meshtastic device metrics', labels)
metric_lastHeard = Gauge('meshtastic_lastHeard', 'meshtastic device metrics', labels)
#position (optional)
metric_pos_latitudeI = Gauge('meshtastic_pos_latitudeI', 'meshtastic device metrics', labels)
metric_pos_longitudeI = Gauge('meshtastic_pos_longitudeI', 'meshtastic device metrics', labels)
metric_pos_altitude = Gauge('meshtastic_pos_altitude', 'meshtastic device metrics', labels)
metric_pos_time = Gauge('meshtastic_pos_time', 'meshtastic device metrics', labels)
#metrics (optional)
metric_batteryLevel = Gauge('meshtastic_batteryLevel', 'meshtastic device metrics', labels)
metric_voltage = Gauge('meshtastic_voltage', 'meshtastic device metrics', labels)
metric_channelUtilization = Gauge('meshtastic_channelUtilization', 'meshtastic device metrics', labels)
metric_airUtilTx = Gauge('meshtastic_airUtilTx', 'meshtastic device metrics', labels)

def onReceive(node, interface):
    print(f"Received: {node}")
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
    #position (optional)
    if 'position' in node:
        if 'latitudeI' in node['position']:
            metric_pos_latitudeI.labels(num=node['num']).set(node['position']['latitudeI'])
        if 'longitudeI' in node['position']:
            metric_pos_longitudeI.labels(num=node['num']).set(node['position']['longitudeI'])
        if 'altitude' in node['position']:
            metric_pos_altitude.labels(num=node['num']).set(node['position']['altitude'])
        if 'time' in node['position']:
            metric_pos_time.labels(num=node['num']).set(node['position']['time'])
    #metrics (optional)
    if 'deviceMetrics' in node:
        if 'batteryLevel' in node['deviceMetrics']:
            metric_batteryLevel.labels(num=node['num']).set(node['deviceMetrics']['batteryLevel'])
        if 'voltage' in node['deviceMetrics']:
            metric_voltage.labels(num=node['num']).set(node['deviceMetrics']['voltage'])
        if 'channelUtilization' in node['deviceMetrics']:
            metric_channelUtilization.labels(num=node['num']).set(node['deviceMetrics']['channelUtilization'])
        if 'airUtilTx' in node['deviceMetrics']:
            metric_airUtilTx.labels(num=node['num']).set(node['deviceMetrics']['airUtilTx'])

pub.subscribe(onReceive, "meshtastic.node.updated")
start_http_server(8000)
try:
    iface = meshtastic.tcp_interface.TCPInterface(hostname=sys.argv[1])
    while True:
        time.sleep(1000)
    iface.close()
except Exception as ex:
    print(f"Error: Could not connect to {sys.argv[1]} {ex}")
    sys.exit(1)
