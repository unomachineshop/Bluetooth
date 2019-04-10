import bluetooth

# The server's MAC address
hostMACAddress = 'cc:b0:da:a4:9e:8a'
# Specify same port number as server
port = 3
# Specify number of allowed queued connections
backlog = 1
# Specify size of a data packet to send (bytes)
size = 1024
# Initialize the connection protocol
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
# Binds the script on host
s.bind((hostMACAddress, port))
# Server listens to accept ONE connection at a time
s.listen(backlog)

# Communication loop between client and server
try:
	client, clientInfo = s.accept()
	while True:
		data = client.recv(size)
		if data:
			print(data)
			client.send(data)
except:	
	print("Closing socket")
	client.close()
	s.close()
	