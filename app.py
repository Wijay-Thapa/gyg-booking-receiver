from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Tour Bookings").sheet1

def guess_country(phone):
    if phone.startswith("+61"): return "Australia"
    if phone.startswith("+44"): return "United Kingdom"
    if phone.startswith("+1"): return "United States"
    if phone.startswith("+351"): return "Portugal"
    if phone.startswith("+420"): return "Czech Republic"
    return ""

@app.route('/gyg/booking-receiver', methods=['POST'])
def receive_booking():
    data = request.json.get("data", {})
    dt = datetime.fromisoformat(data.get("dateTime"))
    traveler = data.get("travelers", [{}])[0]
    full_name = f"{traveler.get('firstName')} {traveler.get('lastName')}"
    phone = traveler.get("phoneNumber", "").replace(" ", "")
    country = guess_country(phone)

    product_map = {"prod123": "Jamche Tour", "prod456": "Spiritual Walk"}
    product_title = product_map.get(data.get("productId", ""), "Unknown Tour")

    total_people = 0
    total_price = 0
    for item in data.get("bookingItems", []):
        total_people += item.get("count", 0)
        total_price += item.get("count", 0) * item.get("retailPrice", 0)

    net_price = round(total_price * 0.69)

    excel_row = [
        dt.strftime("%#d, %b, %a"),
        dt.strftime("%H:%M"),
        data.get("travelerHotel", "Unknown Pickup"),
        "None",
        "GYG",
        product_title,
        full_name,
        country,
        phone,
        total_people,
        total_price,
        net_price,
        "English",
        "", "", "",
        "Auto-filled from GYG API"
    ]

    sheet.append_row(excel_row, value_input_option="USER_ENTERED")
    return jsonify({"status": "Booking added successfully."}), 200
