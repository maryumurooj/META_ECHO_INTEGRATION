from flask import Flask, request
import requests
import json

app = Flask(__name__)

# ========== CONFIGURATION ==========
VERIFY_TOKEN = "my_secret_token"  # Change this if you want
WHATSAPP_TOKEN = "EAAM6djJZAyBwBQmOo7QqQPpuhatt0SZCtQWf6axG4EqM7Vu7PaQIWmyUO11L3ExBnVFfQG2ZCQLE0uWtrpTuSiqUcXOFOHyBnF7RwOFXIEgeBZCjg5XGRZC80ZAZAp0mtqoE3K7UwtNkM55ZC07y2Ss9flWEB580M5T8wBsHyRqSIjwxB8MqsoLyyTV3z83l4fpIDhFHlzMemBB5tavNOZCSkiKbgoZCsZCOWuG255SvR4a3vzvcezuCMRTtHlwKGuCZAcwUZAbf4CVjLZB2VH2o7e3bLX"  # From Meta API Setup
PHONE_NUMBER_ID = "1085621054627755"  # Your Phone Number ID from Meta
WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

# ========== WEBHOOK VERIFICATION ==========
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    print(f"\n[VERIFY] Mode: {mode}, Token: {token}")
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("[VERIFY] ✓ Success!")
        return challenge, 200
    else:
        print("[VERIFY] ✗ Failed!")
        return 'Verification failed', 403

# ========== RECEIVE & REPLY ==========
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print(f"\n{'='*60}")
        print(f"📩 RAW RECEIVED DATA:")
        print(json.dumps(data, indent=2))
        print(f"{'='*60}")
        
        # Extract message
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        
        if 'messages' in value:
            message = value['messages'][0]
            from_number = message['from']
            msg_text = message['text']['body']
            user_name = value['contacts'][0]['profile']['name']
            
            print(f"\n📱 FROM: {user_name} ({from_number})")
            print(f"💬 MESSAGE: {msg_text}")
            
            # Send reply
            reply = f"Welcome to XIT Law! You said: '{msg_text}'. How can we help you today?"
            result = send_message(from_number, reply)
            
            print(f"\n📤 SENT REPLY: {reply}")
            print(f"✅ API RESPONSE: {json.dumps(result, indent=2)}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    return 'OK', 200

# ========== SEND MESSAGE FUNCTION ==========
def send_message(to_number, text):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    return response.json()

# ========== RUN ==========
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 XIT LAW WhatsApp Bot Starting...")
    print("="*60)
    print(f"📡 Local: http://127.0.0.1:5000/webhook")
    print(f"🔑 Verify Token: {VERIFY_TOKEN}")
    print(f"📱 Phone Number ID: {PHONE_NUMBER_ID}")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
