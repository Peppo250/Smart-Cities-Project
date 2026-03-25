import socket
import json

SERVER_IP = "127.0.0.1"
PORT = 5000

OUTLET_CODE = input("Enter outlet code: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

payload = {
    "role": "OUTLET",
    "location": OUTLET_CODE
}

client.send(json.dumps(payload).encode())

print("Connected as outlet:", OUTLET_CODE)

while True:
    try:
        data = client.recv(4096)

        if not data:
            continue

        order = json.loads(data.decode())

        order_id = order.get("order_id", "UNKNOWN")

        print("\n==============================")
        print("        NEW ORDER")
        print("==============================")
        print("Outlet :", OUTLET_CODE)
        print("Order ID:", order_id)
        print("------------------------------")

        for item in order["items"]:
            print(item["name"], "x", item["qty"])

        print("==============================")

    except Exception as e:
        print("Connection error:", e)
        break

client.close()