"""
🛒 Shop Inventory — Web MCP Server
------------------------------------
Runs as a WEB SERVER with PostgreSQL (Supabase) for persistent storage.

Transport: SSE (Server Sent Events) over HTTP
URL:       https://your-app.onrender.com/sse
"""

import os
import psycopg2
import psycopg2.extras
from mcp.server.fastmcp import FastMCP

# ─── Setup ────────────────────────────────────────────────────────────────────

PORT = int(os.environ.get("PORT", 8000))

# ⚠️ Move this to Render Environment Variables for security!
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:YOzTBDk5pQpCuXhM@db.zkgqbcdlxrwdioiwddvi.supabase.co:5432/postgres"
)

mcp = FastMCP(
    "Shop Inventory Manager",
    host="0.0.0.0",
    port=PORT,
)


# ─── Database Helpers ─────────────────────────────────────────────────────────

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = psycopg2.extras.RealDictCursor  # dict-style rows
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id              SERIAL PRIMARY KEY,
            name            TEXT    NOT NULL UNIQUE,
            quantity        REAL    NOT NULL DEFAULT 0,
            unit            TEXT    NOT NULL DEFAULT 'kg',
            low_stock_alert REAL    NOT NULL DEFAULT 10
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


init_db()


# ─── MCP Tools ────────────────────────────────────────────────────────────────

@mcp.tool()
def add_product(name: str, quantity: float, unit: str = "kg", low_stock_alert: float = 10) -> str:
    """
    Add a new product to the shop inventory.

    Args:
        name: Product name (e.g. "Rice", "Sugar")
        quantity: How much stock (e.g. 50)
        unit: Unit of measurement (e.g. "kg", "liters", "pieces")
        low_stock_alert: Alert when stock falls below this number
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products (name, quantity, unit, low_stock_alert) VALUES (%s, %s, %s, %s)",
            (name.strip(), quantity, unit, low_stock_alert)
        )
        conn.commit()
        cur.close()
        conn.close()
        return f"✅ Added '{name}' — {quantity} {unit} (alert at {low_stock_alert} {unit})"
    except psycopg2.errors.UniqueViolation:
        return f"❌ Product '{name}' already exists. Use update_stock to change quantity."


@mcp.tool()
def update_stock(name: str, quantity: float) -> str:
    """
    Update the stock quantity of an existing product.

    Args:
        name: Product name to update
        quantity: New quantity value
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE products SET quantity = %s WHERE name = %s",
        (quantity, name.strip())
    )
    conn.commit()
    rowcount = cur.rowcount
    cur.close()
    conn.close()

    if rowcount == 0:
        return f"❌ Product '{name}' not found. Use add_product first."
    return f"✅ Updated '{name}' stock to {quantity}"


@mcp.tool()
def get_stock(name: str) -> str:
    """
    Check the current stock of a specific product.

    Args:
        name: Product name to check
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE name = %s", (name.strip(),))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return f"❌ Product '{name}' not found."

    status = "⚠️ LOW STOCK" if row["quantity"] <= row["low_stock_alert"] else "✅ OK"
    return (
        f"📦 {row['name']}\n"
        f"   Stock    : {row['quantity']} {row['unit']}\n"
        f"   Alert at : {row['low_stock_alert']} {row['unit']}\n"
        f"   Status   : {status}"
    )


@mcp.tool()
def list_all_products() -> str:
    """
    List all products in the inventory with their current stock.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY name")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return "📭 Inventory is empty. Use add_product to add items."

    lines = ["📋 FULL INVENTORY\n" + "─" * 40]
    for row in rows:
        status = "⚠️ LOW" if row["quantity"] <= row["low_stock_alert"] else "✅"
        lines.append(f"{status} {row['name']:<20} {row['quantity']} {row['unit']}")
    lines.append("─" * 40)
    lines.append(f"Total products: {len(rows)}")
    return "\n".join(lines)


@mcp.tool()
def list_low_stock() -> str:
    """
    Show all products that are low in stock (below their alert level).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE quantity <= low_stock_alert ORDER BY quantity")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return "✅ All products are sufficiently stocked!"

    lines = ["⚠️ LOW STOCK PRODUCTS\n" + "─" * 40]
    for row in rows:
        lines.append(
            f"🔴 {row['name']:<20} {row['quantity']} {row['unit']}  "
            f"(alert: {row['low_stock_alert']} {row['unit']})"
        )
    return "\n".join(lines)


@mcp.tool()
def add_stock(name: str, amount: float) -> str:
    """
    Add more stock to an existing product.

    Args:
        name: Product name
        amount: How much to ADD to current stock
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE name = %s", (name.strip(),))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return f"❌ Product '{name}' not found."

    new_qty = row["quantity"] + amount
    cur.execute(
        "UPDATE products SET quantity = %s WHERE name = %s",
        (new_qty, name.strip())
    )
    conn.commit()
    cur.close()
    conn.close()

    return (
        f"✅ Added {amount} {row['unit']} to '{name}'\n"
        f"   Previous : {row['quantity']} {row['unit']}\n"
        f"   New stock: {new_qty} {row['unit']}"
    )


@mcp.tool()
def delete_product(name: str) -> str:
    """
    Remove a product from the inventory.

    Args:
        name: Product name to delete
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE name = %s", (name.strip(),))
    conn.commit()
    rowcount = cur.rowcount
    cur.close()
    conn.close()

    if rowcount == 0:
        return f"❌ Product '{name}' not found."
    return f"🗑️ Deleted '{name}' from inventory."


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"🌐 Shop Inventory Web MCP Server starting on port {PORT}...")
    print(f"🔗 MCP URL  : http://0.0.0.0:{PORT}/sse")
    print("✅ Ready!\n")
    mcp.run(transport="sse")