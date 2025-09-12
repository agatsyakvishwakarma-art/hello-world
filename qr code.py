import qrcode
import uuid
import json
import datetime
from pyzbar.pyzbar import decode
from PIL import Image

# --------------------------
# Simulated Blockchain (just a JSON ledger for demo)
# --------------------------

ledger_file = "blockchain.json"

def load_ledger():
    try:
        with open(ledger_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_ledger(data):
    with open(ledger_file, "w") as f:
        json.dump(data, f, indent=4)

# --------------------------
# Farmer creates batch
# --------------------------

def create_batch(crop_name, quantity, location, date):
    ledger = load_ledger()

    batch_id = str(uuid.uuid4())[:8]  # unique ID
    entry = {
        "Farmer": {
            "Crop": crop_name,
            "Quantity": quantity,
            "Location": location,
            "Harvested": date,
        },
        "History": []
    }
    ledger[batch_id] = entry
    save_ledger(ledger)

    # Generate QR code with batch_id
    qr = qrcode.make(batch_id)
    qr_filename = f"{batch_id}.png"
    qr.save(qr_filename)

    print(f"[✅] Batch created with ID: {batch_id}")
    print(f"[📦] QR Code saved as {qr_filename}")
    return batch_id

# --------------------------
# Distributor / Retailer updates
# --------------------------

def update_batch(batch_id, owner, price):
    ledger = load_ledger()
    if batch_id not in ledger:
        print("❌ Batch not found!")
        return

    update = {
        "Owner": owner,
        "Price": price,
        "Date": str(datetime.date.today())
    }
    ledger[batch_id]["History"].append(update)
    save_ledger(ledger)
    print(f"[🔄] Updated batch {batch_id} with new owner {owner}")

# --------------------------
# Consumer scans QR
# --------------------------

def scan_qr(filename):
    img = Image.open(filename)
    result = decode(img)
    if result:
        batch_id = result[0].data.decode("utf-8")
        print(f"[🔍] Scanned Batch ID: {batch_id}")
        show_journey(batch_id)
    else:
        print("❌ No QR code found!")

# --------------------------
# Show journey
# --------------------------

def show_journey(batch_id):
    ledger = load_ledger()
    if batch_id not in ledger:
        print("❌ Batch not found!")
        return

    print("\n🌾 Product Journey:")
    print(json.dumps(ledger[batch_id], indent=4))

# --------------------------
# DEMO FLOW
# --------------------------

if __name__ == "__main__":
    # Step 1: Farmer creates batch
    batch_id = create_batch("Wheat", "100kg", "Odisha", "2025-09-10")

    # Step 2: Distributor updates
    update_batch(batch_id, "Distributor A", "₹20/kg")

    # Step 3: Retailer updates
    update_batch(batch_id, "Retailer B", "₹25/kg")

    # Step 4: Consumer scans QR
    scan_qr(f"{batch_id}.png")
