import socket
import json

SERVER_IP = "127.0.0.1"
PORT = 5000

with open("food_db.json") as f:
    db = json.load(f)

locations = db["locations"]

print("\nAVAILABLE LOCATIONS\n")

for i, loc in enumerate(locations):
    print(i+1, "-", loc["name"])

choice = int(input("\nSelect location: ")) - 1
location = locations[choice]

print("\nMENU\n")

for i, item in enumerate(location["menu"]):
    print(i+1, "-", item["name"], "₹", item["price"])

orders = []

while True:
    item_no = int(input("\nSelect item number (0 to finish): "))

    if item_no == 0:
        break

    qty = int(input("Quantity: "))
    item = location["menu"][item_no-1]

    orders.append({
        "name": item["name"],
        "qty": qty
    })
if len(orders) == 0:
    print("No items selected. Order cancelled.")
    exit()
payload = {
    "role": "CLIENT",
    "location": location["code"],
    "items": orders
}

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

client.send(json.dumps(payload).encode())


response = client.recv(4096).decode()
order = json.loads(response)

print("\nOrder placed successfully!")
print("Order ID:", order["order_id"])