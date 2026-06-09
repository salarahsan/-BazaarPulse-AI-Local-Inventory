import sys
import types
import sqlite3
import re

# 🚨 DYNAMIC FIX: Python 3.13 Compatibility Patches
if 'audioop' not in sys.modules:
    dummy_audioop = types.ModuleType('audioop')
    dummy_audioop.error = Exception
    sys.modules['audioop'] = dummy_audioop

import gradio as gr

# Database Initialization (Local Edge Sandbox SQLite)
conn = sqlite3.connect(":memory:", check_same_thread=False)
cursor = conn.cursor()

# Create Local Inventory Matrix Tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS local_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_name TEXT,
    location TEXT,
    item_name TEXT,
    stock_status TEXT
)
""")

# Inject initial mock baseline marketplace data for testing context
mock_data = [
    ("Al-Shifa Medicos", "Main Bazaar, Gate 2", "Panadol CF 500mg", "Available"),
    ("Al-Shifa Medicos", "Main Bazaar, Gate 2", "Augmentin 625mg", "Available"),
    ("Tayyab General Store", "Commercial Market", "Olper's Milk 1L", "Available"),
    ("Tayyab General Store", "Commercial Market", "Panadol CF 500mg", "Low Stock"),
    ("Matrix Pharmacy", "Sector G-11", "Brufen Syrup", "Available"),
    ("Matrix Pharmacy", "Sector G-11", "Augmentin 625mg", "Out of Stock")
]
cursor.executemany("INSERT INTO local_inventory (shop_name, location, item_name, stock_status) VALUES (?, ?, ?, ?)", mock_data)
conn.commit()

def shopkeeper_portal(shop_name, location, raw_manifest):
    if not shop_name or not raw_manifest:
        return "⚠️ Error: Shop Name and Inventory List cannot be empty!"
        
    lines = raw_manifest.strip().split("\n")
    items_added = 0
    
    for line in lines:
        if line.strip():
            item = line.replace("-", "").replace("•", "").strip()
            status = "Available"
            if "out" in item.lower() or "khatam" in item.lower():
                status = "Out of Stock"
                item = re.sub(r'(?i)\(.*?khatam.*?\)', '', item).strip()
                
            cursor.execute(
                "INSERT INTO local_inventory (shop_name, location, item_name, stock_status) VALUES (?, ?, ?, ?)",
                (shop_name.strip(), location.strip(), item, status)
            )
            items_added += 1
            
    conn.commit()
    return f"✅ Success! Managed to parse and upload `{items_added}` items natively to the marketplace directory database."

def whatsapp_chat_agent(user_message, history):
    if not user_message.strip():
        return history, ""
        
    query = user_message.strip()
    
    cursor.execute(
        "SELECT shop_name, location, stock_status, item_name FROM local_inventory WHERE item_name LIKE ?", 
        ('%' + query + '%',)
    )
    results = cursor.fetchall()
    
    if not results:
        bot_response = (
            f"❌ **No matching items found in the marketplace grid for '{query}'.**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Salam! Afsos yar, pooray bazaar ki inventory matrix mein '{query}' nahi mila. Kisi aur dukan ka check karoon?"
        )
    else:
        bot_response = f"📋 **Live Marketplace Status for: '{query}'**\n"
        bot_response += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for row in results:
            shop, loc, status, matched_item = row
            icon = "✅" if status == "Available" else ("⚠️" if status == "Low Stock" else "❌")
            
            bot_response += (
                f"🏪 **{shop}**\n"
                f"📍 Location: {loc}\n"
                f"📦 Item: {matched_item}\n"
                f"⚡ Status: {icon} **{status}**\n\n"
            )
            
        bot_response += (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 *Chakkar kaatne ki zaroorat nahi hai, seedha dukaan par chale jaein!* 🚀"
        )
        
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": bot_response})
    
    return history, ""

# Custom WhatsApp Dark Mode UI Styling
custom_css = """
body, .gradio-container { background-color: #0b141a !important; color: #e9edef !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.wa-btn { background-color: #00a884 !important; color: #ffffff !important; font-weight: bold !important; border-radius: 8px !important; }
.wa-btn:hover { background-color: #008f72 !important; box-shadow: 0 0 10px rgba(0,168,132,0.4); }
.video-btn { background-color: #ff0050 !important; color: #ffffff !important; font-weight: bold !important; border-radius: 8px !important; text-align: center; text-decoration: none; display: inline-block; padding: 10px 20px; }
.video-btn:hover { background-color: #ee0047 !important; box-shadow: 0 0 10px rgba(255,0,80,0.4); }
.panel-border { border: 1px solid #222e35 !important; border-radius: 10px; padding: 20px; background: #111b21 !important; }
textarea, input { background-color: #2a3942 !important; color: #e9edef !important; border: 1px solid #222e35 !important; }
"""

with gr.Blocks(title="BazaarPulse AI v1.0") as demo:
    gr.HTML(
        """
        <div style="text-align: center; margin-bottom: 20px; padding: 15px; background: #202c33; border-radius: 10px; border-bottom: 4px solid #00a884;">
            <h1 style='margin: 0; font-size: 26px; color: #00a884; letter-spacing: 1px;'>🟢 BAZAARPULSE AI (WhatsApp Bot Sim)</h1>
            <p style='margin: 5px 0 0 0; color: #8696a0; font-size: 13px;'>Localized Micro-Inventory Search Matrix // Edge Database Querying</p>
        </div>
        """
    )
    
    # 🔥 NEW: Video Link Option Block Added Here Natively
    with gr.Row():
        gr.HTML(
            """
            <div style="text-align: center; margin-bottom: 15px; width: 100%;">
                <a href="https://www.tiktok.com/@salarai123/video/7648566501598940436" target="_blank" class="video-btn">
                    🎬 Watch Project Video Walkthrough / Demo on TikTok
                </a>
            </div>
            """
        )
    
    with gr.Row():
        with gr.Column(scale=3, elem_classes="panel-border"):
            gr.Markdown("### 🏪 Shopkeeper Inventory Portal")
            s_name = gr.Textbox(label="Shop Name", placeholder="e.g., Al-Shifa Medicos")
            s_loc = gr.Textbox(label="Shop Location / Market Address", placeholder="e.g., G-11 Markaz, Block B")
            
            s_manifest = gr.Textbox(
                label="Inventory List (Type line-by-line)", 
                placeholder="Panadol CF\nAugmentin 625mg\nBrufen Syrup (Khatam)",
                lines=8
            )
            upload_btn = gr.Button("📤 Sync Inventory Matrix", elem_classes="wa-btn")
            status_logs = gr.Markdown("`Status: Portal idle. Standing by for stock upload registry...`")
            
        with gr.Column(scale=4, elem_classes="panel-border"):
            gr.Markdown("### 💬 WhatsApp AI Simulation Interface")
            
            chatbot = gr.Chatbot(label="WhatsApp Chat Window", height=400)
            msg_input = gr.Textbox(
                label="Type medicine or product name to search...", 
                placeholder="e.g., Panadol, Augmentin, Milk..."
            )
            send_btn = gr.Button("🟢 Send Chat Command", elem_classes="wa-btn")

    upload_btn.click(fn=shopkeeper_portal, inputs=[s_name, s_loc, s_manifest], outputs=status_logs)
    send_btn.click(fn=whatsapp_chat_agent, inputs=[msg_input, chatbot], outputs=[chatbot, msg_input])
    msg_input.submit(fn=whatsapp_chat_agent, inputs=[msg_input, chatbot], outputs=[chatbot, msg_input])

demo.launch(css=custom_css)
