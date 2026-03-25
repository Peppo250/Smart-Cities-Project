import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5000

outlets = {}

order_counter = 1   


def handle_connection(conn):

    global order_counter

    data = conn.recv(4096).decode()
    msg = json.loads(data)

    if msg["role"] == "OUTLET":

        outlet = msg["location"]
        outlets[outlet] = conn

        print(outlet, "connected")

        while True:
            pass

    elif msg["role"] == "CLIENT":

        location = msg["location"]

        
        order_id = f"ORD{order_counter:04d}"
        order_counter += 1

        msg["order_id"] = order_id

        print("\nORDER RECEIVED:", msg)

        if location in outlets:
            outlets[location].send(json.dumps(msg).encode())
        
        conn.send(json.dumps(msg).encode())
        conn.close()


def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("SERVER STARTED")

    while True:

        conn, addr = server.accept()

        threading.Thread(target=handle_connection, args=(conn,)).start()


main()