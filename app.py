#!/usr/bin/env python

# Open Pixel Control client: All lights to solid white
import paho.mqtt.client as paho
import opc, time
from numpy import interp
import time

numLEDs = 64
light_client = opc.Client('localhost:7890')

mqtt_client_id = "rPiCandy14"

# Globals State
State = 0
Red = 0
Green = 0
Blue = 0
Brightness = 0
iRed = 0
iGreen = 0
iBlue = 0

#black = [ (0,0,0) ] * numLEDs
#white = [ (0,128,0) ] * numLEDs

def on_connect(client, data, flags, rc):
	print("Connected rc: " + str(rc))

def on_subscribe(client, userdata, mid, gqos):
	print('Subscribed: ' + str(mid))

def on_message(client, obj, msg):
	global State
	global Brightness
	global Red
	global iRed
	global Green
	global iGreen
	global Blue
	global iBlue
	print('Message: ' + msg.topic + ' :: ' + str(msg.payload))
	topic = msg.topic
	if topic == 'office/candy/light/set':
		if msg.payload == "ON":
			State = 1
			print('Turning ON light')
		else:
			State = 0
			print('Turning OFF light')

	elif topic == 'office/candy/brightness/set':
		Brightness = int(msg.payload)
		set_brightness()
	elif topic == 'office/candy/rgb/set':
		colors = msg.payload.split(",")
		Red = int(colors[0])
		Green = int(colors[1])
		Blue = int(colors[2])
		set_brightness()
		# Not sure what to do yet.
	send_messages()
	set_lights()

def set_brightness():
	global iRed
	global iGreen
	global iBlue
	iRed = int(interp(Brightness,(0,255),(0,Red)))
	iGreen = int(interp(Brightness,(0,255),(0,Green)))
	iBlue = int(interp(Brightness,(0,255),(0,Blue)))

def send_messages():	
	if State == 1:
		client.publish('office/candy/light/status', "ON")
	else:
		client.publish('office/candy/light/status', "OFF")

	client.publish('office/candy/brightness/status', str(Brightness))
	rgb = str(Red) +","+str(Green)+","+str(Blue)
	client.publish('office/candy/rgb/status', rgb)

	
def set_lights():
	if State == 1:
		color = [ (iRed, iGreen, iBlue) ] * numLEDs
		light_client.put_pixels(color)
	else:
		color = [ (0, 0, 0) ] * numLEDs
		light_client.put_pixels(color)

client = paho.Client(client_id=mqtt_client_id, protocol=paho.MQTTv31)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

client.connect('192.168.2.20', 1883, 60)

client.subscribe('office/candy/light/set')
client.subscribe('office/candy/brightness/set')
client.subscribe('office/candy/rgb/set')

announce_freq = 2
rc = 0
last_update_time = time.time()

while rc == 0:
	rc = client.loop()

	if time.time() - last_update_time > announce_freq:
		last_update_time = time.time()
		send_messages()

