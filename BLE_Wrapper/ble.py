import pexpect
import time
import sys

class BluetoothControl:

    ##########################################################
    # Name: __init__
    # Desc: Class constructor, spawns 'bluetoothctl' process
    ##########################################################
    def __init__(self):
        self.target_mac = ""
        self.child = pexpect.spawn("bluetoothctl", echo=False)

    ##########################################################
    # Name: get_mac_address
    # Desc: Given a passed name, attempt to find the mac 
    # address associated with it.
    ##########################################################
    def get_mac_address(self, name):
        self.scan_duration(30)
        devices = self.devices()

        for device in devices:
            n = device.get('name')
            m = device.get('mac_address')
            if n == name:
                return mac

        return None

    ##########################################################
    # Name: scan_on
    # Desc: Starts scanning for devices
    ##########################################################
    def scan_on(self):
        self.child.sendline("scan on")
        self.child.expect("Discovery started")


    ##########################################################
    # Name: scan_off
    # Desc: Stops scanning for devices
    ##########################################################
    def scan_off(self):
        self.child.sendline("scan off")
        self.child.expect(["Discovery stopped", pexpect.EOF], 3)


    ##########################################################
    # Name: scan_duration
    # Desc: Starts and stops a scan within the specified time
    # duration (seconds) argument
    ##########################################################
    def scan_duration(self, duration):
        self.scan_on()
        time.sleep(duration)
        self.scan_off()


    ##########################################################
    # Name: connect
    # Desc: Attempt to connect to passed mac address
    ##########################################################
    def connect(self, mac_address):
        self.child.sendline("connect " + mac_address)
        self.child.expect(["Connection successful", pexpect.EOF])
        print("Connected!")


    ##########################################################
    # Name: disconnect
    # Desc: Attempt to disconnect from pass mac address
    ##########################################################
    def disconnect(self, mac_address):
        self.child.sendline("disconnect " + mac_address)
        self.child.expect(["Successful disconnected", pexpect.EOF])
        print("Disconnected!")

    ##########################################################
    # Name: to_main_menu
    # Desc: Return to the main menu
    ##########################################################
    def to_main_menu(self):
        self.child.sendline("back")
        self.child.expect("Arduino")

    ##########################################################
    # Name: to_gatt_menu
    # Desc: Go to the GATT menu
    ##########################################################
    def to_gatt_menu(self):
        self.child.sendline("menu gatt")
        self.child.expect("Arduino")

    ##########################################################
    # Name: select_attribute
    # Desc: Selects an attribute based on passed in path
    ##########################################################
    def select_attribute(self, attribute):
        self.child.sendline("select-attribute " + attribute)
        self.child.expect("Arduino")


    ##########################################################
    # Name: devices
    # Desc: Returns both paired and discoverable device info
    # in easy to manipulate list of dictionaries. 
    ##########################################################
    def devices(self):
        out = self.execute("devices")
        available_devices = []
        for line in out:
            device = self.parse_device_info(line)
            if device:
                available_devices.append(device)

        return available_devices


    ##########################################################
    # Name: parse_device_info
    # Desc: Given a line of device information, parse that 
    # info into 'mac_address' and 'name' so it can be used.
    # Also filters some garbage information.
    ##########################################################
    def parse_device_info(self, info_string):
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        string_valid = not any(keyword in info_string for keyword in block_list)

        if string_valid:
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(" ", 2)
                    device = {
                            "mac_address": attribute_list[1],
                            "name": attribute_list[2]
                            }
                    return device


    ##########################################################
    # Name: remove
    # Desc: Removes a particular device based on MAC address.
    # Returns True if device was found and removed
    # Returns False if device was not founnd in 'devices'
    ##########################################################
    def remove(self, mac_address):
        out = self.child.sendline("remove " + mac_address)
        res = self.child.expect(["not available", "Device has been removed", pexpect.EOF])
        success = True if res == 1 else False
        return success


    ##########################################################
    # Name: execute
    # Desc: Execute a particular command through bluetoothctl
    # process, and return the output as a list of lines.
    ##########################################################
    def execute(self, cmd):
        self.child.sendline(cmd)

        fail = self.child.expect(["bluetooth", pexpect.EOF])
        if fail:
            print("Failure at command " + cmd)

        return self.child.before.decode("utf-8").split("\r\n")



    def write_to_device(self, mac_address):

        self.to_gatt_menu()

        # May end up passing this in later
        self.child.sendline("select-attribute /org/bluez/hci0/dev_DB_3E_E3_E7_0B_AE/service000c/char000d")
        self.child.expect("Arduino")

        for x in range(0,10):
            self.child.sendline("write 0x00")
            self.child.expect("Arduino")
            time.sleep(3)
            self.child.sendline("write 0x01")
            self.child.expect("Arduino")
            time.sleep(3)
            print("On Off count = {}".format(x))
    
        self.child.sendline("back")
        self.child.expect(["Arduino:", pexpect.EOF])
        
        self.to_main_menu()


    def read_from_device(self, mac_address):
        
        self.to_gatt_menu()

        self.child.sendline("select-attribute /org/bluez/hci0/dev_DB_3E_E3_E7_0B_AE/service000c/char0010")
        self.child.expect("Arduino")

        for x in range(0,10):
            self.child.sendline("read")
            self.child.expect("Arduino")
            print(self.child.before.decode())
            time.sleep(5)

        self.to_main_menu()



MAC   = "DB:3E:E3:E7:0B:AE"
WRITE = "/org/bluez/hci0/dev_DB_3E_E3_E7_0B_AE/service000c/char000d" 
READ  = "/org/bluez/hci0/dev_DB_3E_E3_E7_0B_AE/service000c/char0010"

bc = BluetoothControl()
bc.connect(MAC)
bc.write_to_device(MAC)
time.sleep(1)
bc.read_from_device(MAC)
bc.disconnect(MAC)
