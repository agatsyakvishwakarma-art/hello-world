import qrcode
import uuid
import json
import datetime
import hashlib
from pyzbar.pyzbar import decode
from PIL import Image

# --------------------------
# Simulated Blockchain (JSON ledger)
# --------------------------
LEDGER_FILE = "blockchain.json"

def load_ledger() -> dict:
    try:
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_ledger(data: dict) -> None:
    with open(LEDGER_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --------------------------
# Blockchain utilities
# --------------------------
def generate_hash(data: dict) -> str:
    """Generate a simple SHA256 hash of the block data."""
    block_string = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

# --------------------------
# Farmer creates batch
# --------------------------
def create_batch(crop_name: str, quantity: str, location: str, date: str) -> str:
    ledger = load_ledger()

    batch_id = str(uuid.uuid4())[:8]  # unique ID
    entry = {
        "BatchID": batch_id,
        "Farmer": {
            "Crop": crop_name,
            "Quantity": quantity,
            "Location": location,
            "Harvested": date,
        },
        "History": [],
        "Hash": ""
    }
    entry["Hash"] = generate_hash(entry)
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
def update_batch(batch_id: str, owner: str, price: str) -> None:
    ledger = load_ledger()
    if batch_id not in ledger:
        print("❌ Batch not found!")
        return

    update = {
        "Owner": owner,
        "Price": price,
        "Timestamp": str(datetime.datetime.now())
    }
    ledger[batch_id]["History"].append(update)
    ledger[batch_id]["Hash"] = generate_hash(ledger[batch_id])  # re-hash
    save_ledger(ledger)
    print(f"[🔄] Updated batch {batch_id} with new owner {owner}")

# --------------------------
# QR Code scanner
# --------------------------
def scan_qr(filename: str) -> None:
    try:
        img = Image.open(filename)
        result = decode(img)
        if result:
            batch_id = result[0].data.decode("utf-8")
            print(f"[🔍] Scanned Batch ID: {batch_id}")
            show_journey(batch_id)
        else:
            print("❌ No QR code found in image!")
    except FileNotFoundError:
        print("❌ QR code image not found!")

# --------------------------
# Show journey
# --------------------------
def show_journey(batch_id: str) -> None:
    ledger = load_ledger()
    if batch_id not in ledger:
        print("❌ Batch not found in ledger!")
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
