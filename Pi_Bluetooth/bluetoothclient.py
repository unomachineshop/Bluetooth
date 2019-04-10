import bluetooth

# The server's MAC address
serverMACAddress = 'XX:XX:XX:XX:XX:XX'
# Specify same port number as client
port = 3
# Initalize the connection protocol
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
# Enable the bluetooth client
s.connect((serverMACAddress, port))

#Transmit data packets to server
while True:
  text = raw_input()
  if text == "quit":
    break
  s.send(text)

sock.close()