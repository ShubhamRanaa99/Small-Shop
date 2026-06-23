# 🌐 Shop Inventory — Web MCP Server

A **Web MCP Server** that lets Claude manage your shop inventory
from **anywhere** via a public URL hosted on Render.

---

## 🆚 What's Different from Local MCP?

| | Local MCP | This (Web MCP) |
|---|---|---|
| Where it runs | Your laptop | Render's servers |
| How Claude connects | `stdio` (direct) | `https://yourapp.onrender.com/sse` |
| Works when laptop is off? | ❌ No | ✅ Yes |
| Access from claude.ai? | ❌ No | ✅ Yes |
| Access from anywhere? | ❌ No | ✅ Yes |

---

## 📁 Project Structure

```
shop-web-mcp/
├── server.py           ← Web MCP server (SSE transport)
├── requirements.txt    ← Python dependencies
├── render.yaml         ← Render deployment config
├── .gitignore          ← Git ignore rules
└── README.md           ← This file
```

---

## 🚀 Deploy to Render (Step by Step)

### Step 1 — Push to GitHub

First, put this project on GitHub:

```bash
cd shop-web-mcp

git init
git add .
git commit -m "Initial Web MCP server"

# Create a repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/shop-web-mcp.git
git push -u origin main
```

---

### Step 2 — Create a Render Account

Go to 👉 https://render.com and sign up (free).

---

### Step 3 — Deploy on Render

1. Go to **Render Dashboard** → click **"New +"** → **"Web Service"**
2. Connect your **GitHub account**
3. Select your **shop-web-mcp** repository
4. Render auto-detects `render.yaml` — settings are filled automatically!
5. Click **"Create Web Service"**
6. Wait ~2 minutes for deployment ⏳

---

### Step 4 — Get Your Public URL

After deployment, Render gives you a URL like:

```
https://shop-inventory-mcp.onrender.com
```

Your **MCP URL** will be:
```
https://shop-inventory-mcp.onrender.com/sse
```

**Save this URL — you'll need it to connect Claude!**

---

## 🔗 Connect to Claude Desktop

Edit your Claude Desktop config file:

| OS      | Path |
|---------|------|
| Mac     | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

Add this (replace with your actual Render URL):

```json
{
  "mcpServers": {
    "shop-inventory-web": {
      "url": "https://shop-inventory-mcp.onrender.com/sse"
    }
  }
}
```

Notice the difference from Local MCP config:
- ❌ No `command` or `args` (no local process!)
- ✅ Just a `url` pointing to Render

Then **restart Claude Desktop**.

---

## 🔗 Connect to claude.ai (Web)

1. Go to **claude.ai** → Settings → **Integrations**
2. Click **"Add Integration"**
3. Enter your URL:
   ```
   https://shop-inventory-mcp.onrender.com/sse
   ```
4. Save — Claude can now use your server from the browser!

---

## 💬 Example Conversations

```
"Add 50kg of Rice to my inventory, alert at 10kg"
"How much Sugar do we have?"
"Show all products"
"Which products are low in stock?"
"Add 20 more kg of Rice"
"Update Oil stock to 15 liters"
"Delete Sugar from inventory"
```

---

## 🛠️ Available Tools

| Tool | What Claude can do |
|------|-------------------|
| `add_product` | Add new product with quantity & unit |
| `get_stock` | Check one product's stock |
| `list_all_products` | See full inventory |
| `list_low_stock` | See only low stock items |
| `update_stock` | Set exact new quantity |
| `add_stock` | Add more to existing stock |
| `delete_product` | Remove a product |

---

## ⚠️ Free Tier Note (Render)

On Render's free tier:
- Server **sleeps after 15 min** of inactivity
- First request after sleep takes ~30 seconds to wake up
- To avoid this, upgrade to paid tier ($7/month) or use a free uptime monitor like https://uptimerobot.com

---

## 🧪 Test Locally First (Optional)

Before deploying, test it runs:

```bash
pip install -r requirements.txt
python server.py
```

You should see:
```
🌐 Shop Inventory Web MCP Server starting on port 8000...
📂 Database : /path/to/inventory.db
🔗 MCP URL  : http://0.0.0.0:8000/sse
✅ Ready!
```

Test the SSE endpoint:
```bash
curl http://localhost:8000/sse
```

---

## ❓ Troubleshooting

**Render deployment fails?**
- Check logs in Render Dashboard → your service → "Logs" tab

**Claude can't connect?**
- Make sure URL ends with `/sse`
- Check your service is "Live" on Render dashboard
- Wait 30 sec if server was sleeping (free tier)

**Tools not showing in Claude?**
- Restart Claude Desktop after editing config
- Double-check the URL is correct
