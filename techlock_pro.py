"""
╔══════════════════════════════════════════════════════════════════════╗
║          TechLock Pro — Sistema de Gestión de Negocio               ║
║          Instalaciones de cerraduras + Servicios técnicos           ║
╠══════════════════════════════════════════════════════════════════════╣
║  Instalación:   pip install streamlit plotly                        ║
║  Ejecutar:      streamlit run techlock_pro.py                       ║
║  Python:        3.8+   |   Streamlit: 1.29+                        ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import copy
import json
import os
from datetime import date, datetime

import plotly.graph_objects as go
import streamlit as st

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TechLock Pro",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
DATA_FILE = "techlock_data.json"
MONTHS = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
MONTHS_FULL = ["enero","febrero","marzo","abril","mayo","junio",
               "julio","agosto","septiembre","octubre","noviembre","diciembre"]
PAYMENT_METHODS = ["Efectivo","Transferencia","Nequi","Daviplata","Tarjeta","A crédito"]

ORDER_TYPES = {
    "cerradura": {"label": "Cerradura inteligente", "icon": "🔐", "color": "#3b82f6"},
    "tecnico":   {"label": "Servicio técnico",       "icon": "🖥️",  "color": "#8b5cf6"},
}
STATUSES = {
    "pendiente":  {"label": "Pendiente",  "emoji": "🟡", "badge": "🟡 Pendiente"},
    "en_proceso": {"label": "En proceso", "emoji": "🔵", "badge": "🔵 En proceso"},
    "completado": {"label": "Completado", "emoji": "🟢", "badge": "🟢 Completado"},
    "cancelado":  {"label": "Cancelado",  "emoji": "🔴", "badge": "🔴 Cancelado"},
}
NEXT_STATUS = {
    "pendiente":  ["en_proceso", "cancelado"],
    "en_proceso": ["completado", "cancelado"],
    "completado": [],
    "cancelado":  [],
}
STATUS_LABELS = {
    "en_proceso": "▶️ Iniciar servicio",
    "completado": "✅ Marcar completado",
    "cancelado":  "✕ Cancelar pedido",
}

# ─── SEED DATA ────────────────────────────────────────────────────────────────
SEED_DATA = {
    "clients": [
        {"id":1,"name":"María García","phone":"3001234567","addr":"Cl 80 #45-23, Medellín","since":"2025-01-15"},
        {"id":2,"name":"Carlos Rodríguez","phone":"3109876543","addr":"Kr 65 #12-34, Medellín","since":"2025-02-01"},
        {"id":3,"name":"Ana Martínez","phone":"3205551234","addr":"Av El Poblado #15-44, Medellín","since":"2025-03-10"},
    ],
    "products": [
        {"id":1,"name":"Cerradura Yale YDM4109 WiFi","cat":"cerradura","stock":5,"min":2,"price":450000,"cost":280000},
        {"id":2,"name":"Cerradura Ultraloq UL3 BT","cat":"cerradura","stock":3,"min":2,"price":380000,"cost":220000},
        {"id":3,"name":"Cerradura Tuya Smart Pro","cat":"cerradura","stock":7,"min":3,"price":290000,"cost":165000},
        {"id":4,"name":"Teclado Redragon Kumara RGB","cat":"accesorio","stock":8,"min":3,"price":120000,"cost":72000},
        {"id":5,"name":"Mouse Logitech G305","cat":"accesorio","stock":6,"min":3,"price":145000,"cost":88000},
        {"id":6,"name":"RAM 8GB DDR4 Kingston","cat":"accesorio","stock":4,"min":2,"price":95000,"cost":58000},
        {"id":7,"name":"SSD 240GB Kingston A400","cat":"accesorio","stock":5,"min":2,"price":110000,"cost":68000},
        {"id":8,"name":"Cable HDMI 2m Premium","cat":"accesorio","stock":20,"min":5,"price":22000,"cost":10000},
        {"id":9,"name":"Pasta térmica Arctic MX-4","cat":"accesorio","stock":12,"min":4,"price":18000,"cost":8000},
    ],
    "services": [
        {"id":1,"name":"Instalación cerradura estándar","cat":"instalacion","price":80000},
        {"id":2,"name":"Instalación cerradura premium","cat":"instalacion","price":130000},
        {"id":3,"name":"Formateo + Windows 10/11","cat":"tecnico","price":70000},
        {"id":4,"name":"Mantenimiento preventivo","cat":"tecnico","price":55000},
        {"id":5,"name":"Mantenimiento correctivo","cat":"tecnico","price":90000},
        {"id":6,"name":"Instalación de software","cat":"tecnico","price":35000},
        {"id":7,"name":"Recuperación de datos","cat":"tecnico","price":120000},
        {"id":8,"name":"Diagnóstico técnico","cat":"tecnico","price":30000},
    ],
    "orders": [
        {"id":1,"cid":1,"type":"cerradura","status":"completado","date":"2025-05-02","done":"2025-05-03",
         "items":[{"k":"p","id":1,"name":"Cerradura Yale YDM4109 WiFi","qty":1,"price":450000},
                  {"k":"s","id":1,"name":"Instalación estándar","qty":1,"price":80000}],
         "total":530000,"pay":"Transferencia","notes":"Puerta principal apto 301"},
        {"id":2,"cid":2,"type":"tecnico","status":"completado","date":"2025-05-08","done":"2025-05-08",
         "items":[{"k":"s","id":3,"name":"Formateo + Windows","qty":1,"price":70000},
                  {"k":"p","id":9,"name":"Pasta térmica Arctic MX-4","qty":1,"price":18000}],
         "total":88000,"pay":"Efectivo","notes":"HP Pavilion i5 10th gen"},
        {"id":3,"cid":3,"type":"cerradura","status":"completado","date":"2025-05-20","done":"2025-05-21",
         "items":[{"k":"p","id":2,"name":"Cerradura Ultraloq UL3 BT","qty":1,"price":380000},
                  {"k":"s","id":2,"name":"Instalación premium","qty":1,"price":130000}],
         "total":510000,"pay":"Nequi","notes":"Casa nueva, puerta principal"},
        {"id":4,"cid":1,"type":"tecnico","status":"completado","date":"2025-05-25","done":"2025-05-25",
         "items":[{"k":"s","id":4,"name":"Mantenimiento preventivo","qty":1,"price":55000},
                  {"k":"s","id":6,"name":"Instalación software","qty":1,"price":35000}],
         "total":90000,"pay":"Efectivo","notes":"PC escritorio Dell"},
        {"id":5,"cid":2,"type":"cerradura","status":"en_proceso","date":"2025-06-03","done":None,
         "items":[{"k":"p","id":3,"name":"Cerradura Tuya Smart Pro","qty":1,"price":290000},
                  {"k":"s","id":1,"name":"Instalación estándar","qty":1,"price":80000}],
         "total":370000,"pay":"","notes":"Oficina 2do piso"},
        {"id":6,"cid":3,"type":"tecnico","status":"pendiente","date":"2025-06-06","done":None,
         "items":[{"k":"s","id":5,"name":"Mantenimiento correctivo","qty":1,"price":90000}],
         "total":90000,"pay":"","notes":"Laptop ASUS no enciende"},
    ],
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def fmt(n: int) -> str:
    """Formato peso colombiano: $ 1.234.567"""
    n = int(n or 0)
    return "$ " + f"{n:,}".replace(",", ".")

def fmt_short(n: int) -> str:
    """Formato corto: $ 1.2M, $ 530k, $ 88k"""
    n = n or 0
    if n >= 1_000_000:
        return f"$ {n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"$ {n / 1_000:.0f}k"
    return fmt(n)

def today() -> str:
    return date.today().isoformat()

def nid(lst: list) -> int:
    return max((x["id"] for x in lst), default=0) + 1

def get_client(cid: int) -> dict | None:
    return next((c for c in st.session_state.data["clients"] if c["id"] == cid), None)

# ─── DATA PERSISTENCE ─────────────────────────────────────────────────────────
def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return copy.deepcopy(SEED_DATA)

def save_data(data: dict) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"⚠️ No se pudo guardar: {e}")

# ─── SESSION STATE ────────────────────────────────────────────────────────────
def init_state() -> None:
    defaults = {
        "data": load_data(),
        "page": "dashboard",
        # Orders
        "new_order": False,
        "order_items": [],
        "order_type": "cerradura",
        "selected_order_id": None,
        # Inventory
        "product_form": False,
        "edit_product": None,
        "stock_product": None,
        # Clients
        "client_form": False,
        "edit_client": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ─── DATA OPERATIONS ─────────────────────────────────────────────────────────
def mutate(fn) -> None:
    """Apply a pure function to a deep copy of data, then save."""
    new_data = fn(copy.deepcopy(st.session_state.data))
    st.session_state.data = new_data
    save_data(new_data)

def op_add_order(order: dict) -> None:
    def fn(d):
        order["id"] = nid(d["orders"])
        d["orders"].append(order)
        return d
    mutate(fn)
    st.toast("✅ Pedido creado correctamente")

def op_update_order(order: dict) -> None:
    def fn(d):
        d["orders"] = [order if o["id"] == order["id"] else o for o in d["orders"]]
        return d
    mutate(fn)
    st.toast("✅ Pedido actualizado")

def op_add_client(client: dict) -> None:
    def fn(d):
        client["id"] = nid(d["clients"])
        client.setdefault("since", today())
        d["clients"].append(client)
        return d
    mutate(fn)
    st.toast("✅ Cliente agregado")

def op_update_client(client: dict) -> None:
    def fn(d):
        d["clients"] = [client if c["id"] == client["id"] else c for c in d["clients"]]
        return d
    mutate(fn)
    st.toast("✅ Cliente actualizado")

def op_add_product(product: dict) -> None:
    def fn(d):
        product["id"] = nid(d["products"])
        d["products"].append(product)
        return d
    mutate(fn)
    st.toast("✅ Producto agregado al inventario")

def op_update_product(product: dict) -> None:
    def fn(d):
        d["products"] = [product if p["id"] == product["id"] else p for p in d["products"]]
        return d
    mutate(fn)
    st.toast("✅ Inventario actualizado")

def op_stock_in(product_id: int, qty: int) -> None:
    def fn(d):
        for p in d["products"]:
            if p["id"] == product_id:
                p["stock"] += qty
                break
        return d
    mutate(fn)
    st.toast(f"📦 +{qty} unidades ingresadas al inventario")

# ─── COMPUTED DATA ────────────────────────────────────────────────────────────
def get_stats() -> dict:
    d = st.session_state.data
    done   = [o for o in d["orders"] if o["status"] == "completado"]
    active = [o for o in d["orders"] if o["status"] in ["pendiente", "en_proceso"]]
    total_rev = sum(o["total"] for o in done)
    this_m    = datetime.now().strftime("%Y-%m")
    month_rev = sum(o["total"] for o in done if (o.get("done") or "").startswith(this_m))
    low_stock = [p for p in d["products"] if p["stock"] <= p["min"]]
    return dict(done=done, active=active, total_rev=total_rev,
                month_rev=month_rev, low_stock=low_stock)

def get_chart_data() -> list:
    result = {}
    for o in st.session_state.data["orders"]:
        if o["status"] != "completado" or not o.get("done"):
            continue
        m_idx = int(o["done"][5:7]) - 1
        key   = MONTHS[m_idx]
        if key not in result:
            result[key] = {"name": key, "cerraduras": 0, "servicios": 0}
        if o["type"] == "cerradura":
            result[key]["cerraduras"] += o["total"]
        else:
            result[key]["servicios"] += o["total"]
    return list(result.values())[-6:]

# ─── CSS ──────────────────────────────────────────────────────────────────────
def inject_css() -> None:
    st.markdown("""
    <style>
    #MainMenu, header, footer { visibility: hidden; }

    [data-testid="stSidebar"] {
        background: #0b1120 !important;
        border-right: 1px solid #1a2540 !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #64748b !important;
        text-align: left !important;
        font-weight: 400 !important;
        padding: 10px 16px !important;
        width: 100% !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(59,130,246,0.1) !important;
        color: #f1f5f9 !important;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 16px 18px;
        border-radius: 12px;
        border: 1.5px solid #e5e7eb;
    }
    div[data-testid="stMetricLabel"] * {
        color: #6b7280 !important;
        opacity: 1 !important;
    }
    div[data-testid="stMetricValue"] * {
        color: #111827 !important;
        font-weight: 800 !important;
    }

    .block-container { padding-top: 1.5rem !important; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; }
    .stButton > button { border-radius: 8px !important; font-weight: 600 !important; }
    div[data-testid="stHorizontalBlock"] { gap: 12px; }
    </style>
    """, unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
def render_sidebar() -> None:
    s = get_stats()

    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:18px 0 14px">
            <div style="font-size:38px">🔐</div>
            <div style="font-weight:800; font-size:18px; color:#f1f5f9; margin-top:6px">
                TechLock Pro
            </div>
            <div style="font-size:10px; color:#475569; letter-spacing:1.2px; margin-top:4px">
                GESTIÓN DE NEGOCIO
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        nav_items = [
            ("dashboard",  "⊞  Dashboard"),
            ("orders",     f"📋  Pedidos {'🔴 ' + str(len(s['active'])) if s['active'] else ''}"),
            ("inventory",  f"📦  Inventario {'⚠️' if s['low_stock'] else ''}"),
            ("clients",    "👥  Clientes"),
            ("revenue",    "💰  Ingresos"),
            ("services",   "🛠️  Servicios"),
        ]

        for page_id, label in nav_items:
            is_active = st.session_state.page == page_id
            style = "color:#ffffff !important; font-weight:700 !important; background:rgba(59,130,246,0.15) !important; border-left: 3px solid #3b82f6 !important;"
            st.markdown(
                f'<div style="{"border-left:3px solid #3b82f6;background:rgba(59,130,246,0.12);border-radius:0 8px 8px 0;" if is_active else ""}">',
                unsafe_allow_html=True
            )
            if st.button(label, key=f"nav_{page_id}", use_container_width=True):
                st.session_state.page = page_id
                st.session_state.selected_order_id = None
                st.session_state.new_order = False
                st.session_state.product_form = False
                st.session_state.client_form = False
                st.rerun()

        st.divider()

        if s["low_stock"]:
            names = ", ".join(p["name"].split()[0] for p in s["low_stock"][:2])
            extra = f" +{len(s['low_stock'])-2} más" if len(s["low_stock"]) > 2 else ""
            st.warning(f"⚠️ **Stock bajo:** {names}{extra}")

        st.markdown(f"""
        <div style="padding: 12px 8px; text-align:center">
            <div style="font-size:10px; color:#475569; font-weight:600;
                        text-transform:uppercase; letter-spacing:.8px">
                INGRESOS TOTALES
            </div>
            <div style="font-size:20px; font-weight:800; color:#38bdf8; margin-top:5px">
                {fmt_short(s["total_rev"])}
            </div>
            <div style="font-size:10px; color:#334155; margin-top:6px">
                Medellín, Colombia 🇨🇴
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── DASHBOARD VIEW ────────────────────────────────────────────────────────────
def view_dashboard() -> None:
    s = get_stats()
    cd = get_chart_data()
    d  = st.session_state.data
    this_m = datetime.now().strftime("%Y-%m")
    m_orders = [o for o in s["done"] if (o.get("done") or "").startswith(this_m)]

    col_h, col_btn = st.columns([4, 1])
    with col_h:
        st.title("⊞ Panel de control")
        _hoy = datetime.now()
        st.caption(f"TechLock Pro · {_hoy.day} de {MONTHS_FULL[_hoy.month - 1]} de {_hoy.year}")
    with col_btn:
        st.write("")
        if st.button("＋ Nuevo pedido", type="primary", use_container_width=True, key="dash_new"):
            st.session_state.page = "orders"
            st.session_state.new_order = True
            st.session_state.order_items = []
            st.rerun()

    # ── KPIs ──
    pending_cnt  = sum(1 for o in s["active"] if o["status"] == "pendiente")
    in_prog_cnt  = sum(1 for o in s["active"] if o["status"] == "en_proceso")
    low_cnt      = len(s["low_stock"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Ingresos del mes",  fmt_short(s["month_rev"]),
              f"{len(m_orders)} órdenes completadas")
    c2.metric("📋 Pedidos activos",   str(len(s["active"])),
              f"{pending_cnt} pend · {in_prog_cnt} en proceso")
    c3.metric("📦 Alertas de stock",  str(low_cnt),
              "Reabastecer pronto" if low_cnt else "Inventario ok ✓",
              delta_color="inverse" if low_cnt else "normal")
    c4.metric("👥 Clientes",          str(len(d["clients"])), "Registrados")

    st.write("")

    col_chart, col_activity = st.columns([3, 2])

    # ── Revenue chart ──
    with col_chart:
        st.subheader("📊 Ingresos mensuales")
        if cd:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Cerraduras",
                x=[r["name"] for r in cd],
                y=[r["cerraduras"] for r in cd],
                marker_color="#3b82f6", marker_line_width=0,
            ))
            fig.add_trace(go.Bar(
                name="Servicios técnicos",
                x=[r["name"] for r in cd],
                y=[r["servicios"] for r in cd],
                marker_color="#8b5cf6", marker_line_width=0,
            ))
            fig.update_layout(
                barmode="group",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=250, margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", y=1.05, x=0),
                yaxis=dict(tickprefix="$", gridcolor="#f1f5f9"),
                xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                font=dict(size=11),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Completa órdenes para ver las estadísticas de ingresos")

    # ── Activity feed ──
    with col_activity:
        st.subheader("⚡ Actividad reciente")
        recent = sorted(d["orders"], key=lambda o: o["id"], reverse=True)[:6]
        for o in recent:
            cl = get_client(o["cid"])
            ot = ORDER_TYPES[o["type"]]
            status_cfg = STATUSES[o["status"]]
            c_ico, c_info, c_badge = st.columns([1, 4, 2])
            c_ico.write(ot["icon"])
            c_info.write(f"**{cl['name'] if cl else '—'}**  \n{fmt(o['total'])}")
            c_badge.write(status_cfg["badge"])

    if s["low_stock"]:
        st.warning("⚠️ **Stock bajo:** " + " · ".join(p["name"] for p in s["low_stock"]))
        if st.button("→ Gestionar inventario", key="dash_inv"):
            st.session_state.page = "inventory"
            st.rerun()

# ─── ORDERS VIEW ──────────────────────────────────────────────────────────────
def view_orders() -> None:
    d = st.session_state.data

    col_h, col_btn = st.columns([4, 1])
    with col_h:
        st.title("📋 Pedidos")
    with col_btn:
        st.write("")
        if st.button("＋ Nuevo pedido", type="primary", use_container_width=True, key="ord_new"):
            st.session_state.new_order = True
            st.session_state.order_items = []
            st.session_state.selected_order_id = None
            st.rerun()

    # ── New Order Form ─────────────────────────────────────────────────────────
    if st.session_state.new_order:
        st.subheader("✨ Crear nuevo pedido")
        st.write("")

        col_c, col_t = st.columns(2)

        with col_c:
            client_ids   = [c["id"] for c in d["clients"]]
            client_names = {c["id"]: f"{c['name']} · {c['phone']}" for c in d["clients"]}

            sel_cid = st.selectbox(
                "Cliente *",
                options=[None] + client_ids,
                format_func=lambda x: "Seleccionar cliente..." if x is None else client_names.get(x, "—"),
                key="no_cid",
            )

        with col_t:
            new_type = st.radio(
                "Tipo de servicio",
                ["cerradura", "tecnico"],
                format_func=lambda x: "🔐 Cerradura" if x == "cerradura" else "🖥️ Servicio técnico",
                horizontal=True,
                index=0 if st.session_state.order_type == "cerradura" else 1,
                key="no_type",
            )
            if new_type != st.session_state.order_type:
                st.session_state.order_type = new_type
                st.session_state.order_items = []
                st.rerun()

        otype = st.session_state.order_type
        prods = d["products"] if otype == "tecnico" else [p for p in d["products"] if p["cat"] == "cerradura"]
        svcs  = [s for s in d["services"] if s["cat"] == ("instalacion" if otype == "cerradura" else "tecnico")]

        col_p, col_s = st.columns(2)

        with col_p:
            prod_opts = {p["id"]: f"{p['name']} — {fmt(p['price'])} (Stock: {p['stock']})" for p in prods}
            sel_prod = st.selectbox(
                "Agregar producto",
                options=[None] + list(prod_opts.keys()),
                format_func=lambda x: "Seleccionar producto..." if x is None else prod_opts.get(x, "—"),
                key="no_prod",
            )
            if st.button("➕ Agregar producto", key="no_add_prod", use_container_width=True):
                if sel_prod is not None:
                    p = next(x for x in prods if x["id"] == sel_prod)
                    items = st.session_state.order_items
                    existing = next((i for i in items if i["k"] == "p" and i["id"] == p["id"]), None)
                    if existing:
                        existing["qty"] += 1
                    else:
                        items.append({"k":"p","id":p["id"],"name":p["name"],"qty":1,"price":p["price"]})
                    st.rerun()

        with col_s:
            svc_opts = {s["id"]: f"{s['name']} — {fmt(s['price'])}" for s in svcs}
            sel_svc = st.selectbox(
                "Agregar servicio",
                options=[None] + list(svc_opts.keys()),
                format_func=lambda x: "Seleccionar servicio..." if x is None else svc_opts.get(x, "—"),
                key="no_svc",
            )
            if st.button("➕ Agregar servicio", key="no_add_svc", use_container_width=True):
                if sel_svc is not None:
                    s = next(x for x in svcs if x["id"] == sel_svc)
                    items = st.session_state.order_items
                    existing = next((i for i in items if i["k"] == "s" and i["id"] == s["id"]), None)
                    if existing:
                        existing["qty"] += 1
                    else:
                        items.append({"k":"s","id":s["id"],"name":s["name"],"qty":1,"price":s["price"]})
                    st.rerun()

        items = st.session_state.order_items
        if items:
            st.write("**📋 Resumen del pedido:**")
            total = 0
            for i, item in enumerate(items):
                icon = "📦" if item["k"] == "p" else "⚙️"
                c1, c2, c3, c4, c5 = st.columns([4, 2, 1, 2, 1])
                c1.write(f"{icon} {item['name']}")
                c2.write(fmt(item["price"]))
                c3.write(f"×{item['qty']}")
                c4.write(f"**{fmt(item['price'] * item['qty'])}**")
                if c5.button("✕", key=f"rm_{i}"):
                    st.session_state.order_items.pop(i)
                    st.rerun()
                total += item["price"] * item["qty"]
            st.success(f"💰 **Total del pedido: {fmt(total)}**")

        col_n, col_pay = st.columns(2)
        with col_n:
            notes = st.text_area("Notas / descripción del equipo",
                                 placeholder="Ej: Laptop HP Pavilion i5, puerta principal...",
                                 key="no_notes", height=80)
        with col_pay:
            payment = st.selectbox("Método de pago", ["Por definir..."] + PAYMENT_METHODS, key="no_pay")

        total_items = sum(i["price"] * i["qty"] for i in items)
        can_create  = bool(items) and sel_cid is not None

        col_cancel, col_create = st.columns([1, 2])
        with col_cancel:
            if st.button("✕ Cancelar", use_container_width=True, key="no_cancel"):
                st.session_state.new_order  = False
                st.session_state.order_items = []
                st.rerun()
        with col_create:
            if st.button(f"✅ Crear pedido · {fmt(total_items)}", type="primary",
                         use_container_width=True, key="no_create", disabled=not can_create):
                new_order = {
                    "cid":   sel_cid,
                    "type":  st.session_state.order_type,
                    "status":"pendiente",
                    "date":  today(),
                    "done":  None,
                    "items": copy.deepcopy(items),
                    "total": total_items,
                    "pay":   "" if payment == "Por definir..." else payment,
                    "notes": notes,
                }
                op_add_order(new_order)
                st.session_state.new_order  = False
                st.session_state.order_items = []
                st.rerun()

        st.divider()

    # ── Order Detail ───────────────────────────────────────────────────────────
    if st.session_state.selected_order_id is not None:
        oid   = st.session_state.selected_order_id
        order = next((o for o in d["orders"] if o["id"] == oid), None)

        if order:
            cl       = get_client(order["cid"])
            ot       = ORDER_TYPES[order["type"]]
            st_cfg   = STATUSES[order["status"]]

            st.subheader(f"{ot['icon']} Pedido #{order['id']} — {st_cfg['badge']}")

            col_cl, col_tp = st.columns(2)
            with col_cl:
                st.markdown(
                    f"**👤 Cliente:** {cl['name'] if cl else '—'}  \n"
                    f"**📱 Teléfono:** {cl['phone'] if cl else '—'}  \n"
                    f"**📍 Dirección:** {cl.get('addr','') if cl else '—'}"
                )
            with col_tp:
                st.markdown(
                    f"**Tipo:** {ot['icon']} {ot['label']}  \n"
                    f"**Fecha:** {order['date']}  \n"
                    f"**Notas:** {order.get('notes','—')}"
                )

            st.write("**Ítems del pedido:**")
            total = 0
            for item in order["items"]:
                icon = "📦" if item["k"] == "p" else "⚙️"
                c1, c2, c3 = st.columns([4, 2, 2])
                c1.write(f"{icon} {item['name']}")
                c2.write(f"× {item['qty']} · {fmt(item['price'])}")
                c3.write(f"**{fmt(item['price'] * item['qty'])}**")
                total += item["price"] * item["qty"]
            st.success(f"💰 **Total: {fmt(total)}**")

            nexts = NEXT_STATUS.get(order["status"], [])
            if nexts:
                col_pay, col_act = st.columns([2, 3])
                with col_pay:
                    pay_idx = (PAYMENT_METHODS.index(order["pay"]) + 1
                               if order.get("pay") in PAYMENT_METHODS else 0)
                    new_pay = st.selectbox("Método de pago",
                                           ["Sin definir"] + PAYMENT_METHODS,
                                           index=pay_idx, key="od_pay")
                with col_act:
                    st.write("")
                    btn_cols = st.columns(len(nexts))
                    for i, ns in enumerate(nexts):
                        btn_type = "primary" if ns == "completado" else "secondary"
                        if btn_cols[i].button(STATUS_LABELS[ns], key=f"adv_{ns}",
                                              type=btn_type, use_container_width=True):
                            updated = dict(order)
                            updated["status"] = ns
                            updated["pay"]    = "" if new_pay == "Sin definir" else new_pay
                            if ns == "completado":
                                updated["done"] = today()
                            op_update_order(updated)
                            st.session_state.selected_order_id = None
                            st.rerun()

            elif order["status"] == "completado":
                st.success(
                    f"✅ **Completado el {order.get('done','—')}** "
                    f"· Pago: {order.get('pay','No registrado')}"
                )

            if st.button("← Cerrar detalle", key="od_close"):
                st.session_state.selected_order_id = None
                st.rerun()

            st.divider()

    # ── Orders list with tabs ──────────────────────────────────────────────────
    tab_labels = ["Todos","🟡 Pendientes","🔵 En proceso","🟢 Completados","🔴 Cancelados"]
    filter_map = ["all", "pendiente", "en_proceso", "completado", "cancelado"]

    for tab, fk in zip(st.tabs(tab_labels), filter_map):
        with tab:
            orders = (d["orders"] if fk == "all"
                      else [o for o in d["orders"] if o["status"] == fk])
            orders = sorted(orders, key=lambda o: o["id"], reverse=True)

            if not orders:
                st.info("Sin pedidos en esta categoría")
                continue

            for o in orders:
                cl     = get_client(o["cid"])
                ot     = ORDER_TYPES[o["type"]]
                st_cfg = STATUSES[o["status"]]

                col1, col2, col3 = st.columns([5, 2, 1])
                with col1:
                    items_str = " · ".join(
                        f"{'📦' if it['k']=='p' else '⚙️'} {it['name'][:22]}×{it['qty']}"
                        for it in o["items"]
                    )
                    st.write(
                        f"**#{o['id']}** {ot['icon']} **{cl['name'] if cl else '—'}** "
                        f"{st_cfg['badge']}"
                    )
                    st.caption(items_str)
                    if o.get("notes"):
                        st.caption(f"📝 {o['notes']}")
                with col2:
                    st.write(f"**{fmt(o['total'])}**")
                    st.caption(f"📅 {o['date']} · {o.get('pay') or '—'}")
                with col3:
                    if st.button("Ver", key=f"view_{fk}_{o['id']}", use_container_width=True):
                        st.session_state.selected_order_id = o["id"]
                        st.session_state.new_order = False
                        st.rerun()

                st.divider()

# ─── INVENTORY VIEW ───────────────────────────────────────────────────────────
def view_inventory() -> None:
    d = st.session_state.data

    col_h, col_btn = st.columns([4, 1])
    with col_h:
        st.title("📦 Inventario")
    with col_btn:
        st.write("")
        if st.button("＋ Agregar producto", type="primary", use_container_width=True, key="inv_add"):
            st.session_state.product_form = True
            st.session_state.edit_product = None
            st.session_state.stock_product = None
            st.rerun()

    # ── Product form ─────────────────────────────────────────────────────────
    if st.session_state.product_form:
        p = st.session_state.edit_product
        is_new = p is None

        st.subheader("🆕 Agregar producto" if is_new else "✏️ Editar producto")

        col_n, col_c = st.columns(2)
        with col_n:
            name = st.text_input("Nombre *", value=p["name"] if p else "", key="pf_name")
        with col_c:
            cat = st.selectbox(
                "Categoría",
                ["cerradura", "accesorio"],
                index=0 if not p or p["cat"] == "cerradura" else 1,
                format_func=lambda x: "🔐 Cerradura" if x == "cerradura" else "💻 Accesorio PC",
                key="pf_cat",
            )

        col_pr, col_co, col_st, col_mn = st.columns(4)
        with col_pr:
            price = st.number_input("Precio venta ($)", value=int(p["price"]) if p else 0,
                                    min_value=0, step=1000, key="pf_price")
        with col_co:
            cost = st.number_input("Costo ($)", value=int(p["cost"]) if p else 0,
                                   min_value=0, step=1000, key="pf_cost")
        with col_st:
            stock = st.number_input("Stock", value=int(p["stock"]) if p else 0,
                                    min_value=0, key="pf_stock")
        with col_mn:
            min_s = st.number_input("Stock mínimo", value=int(p["min"]) if p else 2,
                                    min_value=0, key="pf_min")

        if price > 0 and cost > 0:
            margin = round((price - cost) / price * 100)
            st.success(f"💵 Margen bruto: {fmt(price - cost)} ({margin}%)")

        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            if st.button("✕ Cancelar", key="pf_cancel", use_container_width=True):
                st.session_state.product_form = False
                st.session_state.edit_product = None
                st.rerun()
        with col_c2:
            label = "Agregar al inventario" if is_new else "Guardar cambios"
            if st.button(label, type="primary", key="pf_save",
                         use_container_width=True, disabled=not name or not price):
                prod = {"name": name, "cat": cat, "price": price,
                        "cost": cost, "stock": stock, "min": min_s}
                if not is_new:
                    prod["id"] = p["id"]
                    op_update_product(prod)
                else:
                    op_add_product(prod)
                st.session_state.product_form = False
                st.session_state.edit_product = None
                st.rerun()

        st.divider()

    # ── Stock entry form ──────────────────────────────────────────────────────
    if st.session_state.stock_product is not None:
        sp = st.session_state.stock_product

        st.subheader(f"📥 Entrada de inventario: {sp['name']}")
        st.caption(f"Stock actual: **{sp['stock']}** unidades · Mínimo: **{sp['min']}**")

        col_q, col_b, col_x = st.columns([2, 1, 1])
        with col_q:
            qty_in = st.number_input("Cantidad a ingresar", min_value=1,
                                     value=1, step=1, key="si_qty")
        with col_b:
            st.write("")
            if st.button(f"✅ Ingresar +{qty_in}", type="primary",
                         key="si_save", use_container_width=True):
                op_stock_in(sp["id"], int(qty_in))
                st.session_state.stock_product = None
                st.rerun()
        with col_x:
            st.write("")
            if st.button("✕ Cancelar", key="si_cancel", use_container_width=True):
                st.session_state.stock_product = None
                st.rerun()

        st.divider()

    # ── Product grid ─────────────────────────────────────────────────────────
    tab_labels  = ["Todos","🔐 Cerraduras","💻 Accesorios PC","⚠️ Stock bajo"]
    tab_keys    = ["all", "lock", "acc", "low"]
    tab_filters = [
        lambda p: True,
        lambda p: p["cat"] == "cerradura",
        lambda p: p["cat"] == "accesorio",
        lambda p: p["stock"] <= p["min"],
    ]

    for tab, tkey, filt in zip(st.tabs(tab_labels), tab_keys, tab_filters):
        with tab:
            prods = [p for p in d["products"] if filt(p)]

            if not prods:
                st.info("Sin productos en esta categoría")
                continue

            for i in range(0, len(prods), 3):
                cols = st.columns(3)
                for j, p in enumerate(prods[i:i+3]):
                    with cols[j]:
                        low    = p["stock"] <= p["min"]
                        margin = round((p["price"]-p["cost"])/p["price"]*100) if p["cost"] else 0

                        if low:
                            st.error(f"⚠️ **{p['name']}**")
                        else:
                            st.success(f"**{p['name']}**")

                        st.caption(f"{'🔐 Cerradura' if p['cat']=='cerradura' else '💻 Accesorio'}")

                        c_pr, c_st = st.columns(2)
                        c_pr.metric("Precio", fmt_short(p["price"]))
                        c_st.metric("Stock", str(p["stock"]),
                                    f"Mín: {p['min']}",
                                    delta_color="inverse" if low else "normal")

                        if margin:
                            st.caption(f"Margen: {margin}% · Costo: {fmt_short(p['cost'])}")

                        ce, cs = st.columns(2)
                        with ce:
                            if st.button("✏️ Editar", key=f"ed_p_{tkey}_{p['id']}", use_container_width=True):
                                st.session_state.edit_product  = p
                                st.session_state.product_form  = True
                                st.session_state.stock_product = None
                                st.rerun()
                        with cs:
                            if st.button("📥 Stock", key=f"si_p_{tkey}_{p['id']}",
                                         type="primary", use_container_width=True):
                                st.session_state.stock_product = p
                                st.session_state.product_form  = False
                                st.rerun()

# ─── CLIENTS VIEW ─────────────────────────────────────────────────────────────
def view_clients() -> None:
    d = st.session_state.data

    col_h, col_btn = st.columns([4, 1])
    with col_h:
        st.title("👥 Clientes")
    with col_btn:
        st.write("")
        if st.button("＋ Nuevo cliente", type="primary", use_container_width=True, key="cli_add"):
            st.session_state.client_form = True
            st.session_state.edit_client = None
            st.rerun()

    # ── Client form ──────────────────────────────────────────────────────────
    if st.session_state.client_form:
        c = st.session_state.edit_client
        is_new = c is None

        st.subheader("👤 Nuevo cliente" if is_new else "✏️ Editar cliente")

        col1, col2 = st.columns(2)
        with col1:
            name  = st.text_input("Nombre completo *", value=c["name"] if c else "", key="cf_name")
            addr  = st.text_input("Dirección", value=c.get("addr","") if c else "", key="cf_addr")
        with col2:
            phone = st.text_input("Teléfono *", value=c["phone"] if c else "", key="cf_phone")
            email = st.text_input("Email (opcional)", value=c.get("email","") if c else "", key="cf_email")

        cc, cs = st.columns([1, 2])
        with cc:
            if st.button("✕ Cancelar", key="cf_cancel", use_container_width=True):
                st.session_state.client_form = False
                st.session_state.edit_client = None
                st.rerun()
        with cs:
            label = "Agregar cliente" if is_new else "Guardar cambios"
            if st.button(label, type="primary", key="cf_save",
                         use_container_width=True, disabled=not name or not phone):
                client_data = {"name": name, "phone": phone, "addr": addr, "email": email}
                if not is_new:
                    client_data["id"]    = c["id"]
                    client_data["since"] = c["since"]
                    op_update_client(client_data)
                else:
                    op_add_client(client_data)
                st.session_state.client_form = False
                st.session_state.edit_client = None
                st.rerun()

        st.divider()

    # ── Search + list ─────────────────────────────────────────────────────────
    search = st.text_input("🔍 Buscar por nombre o teléfono",
                           placeholder="Ej: María, 3001234567...", key="cli_search")

    clients = d["clients"]
    if search:
        sq = search.lower()
        clients = [c for c in clients if sq in c["name"].lower() or sq in c["phone"]]

    if not clients:
        st.info("Sin clientes encontrados")
        return

    for i in range(0, len(clients), 2):
        cols = st.columns(2)
        for j, c in enumerate(clients[i:i+2]):
            with cols[j]:
                orders    = [o for o in d["orders"] if o["cid"] == c["id"]]
                rev       = sum(o["total"] for o in orders if o["status"] == "completado")
                lock_cnt  = sum(1 for o in orders if o["type"] == "cerradura")
                tech_cnt  = sum(1 for o in orders if o["type"] == "tecnico")
                last_ord  = sorted(orders, key=lambda o: o["id"], reverse=True)[0] if orders else None

                col_info, col_edit = st.columns([5, 1])
                with col_info:
                    st.markdown(f"### {c['name']}")
                    st.caption(f"📱 {c['phone']}")
                    if c.get("addr"):
                        st.caption(f"📍 {c['addr']}")
                with col_edit:
                    if st.button("✏️", key=f"ed_c_{c['id']}"):
                        st.session_state.edit_client  = c
                        st.session_state.client_form  = True
                        st.rerun()

                tags = []
                if lock_cnt: tags.append(f"🔐 {lock_cnt} cerradura{'s' if lock_cnt > 1 else ''}")
                if tech_cnt: tags.append(f"🖥️ {tech_cnt} servicio{'s' if tech_cnt > 1 else ''}")
                if tags:
                    st.write(" · ".join(tags))

                cm1, cm2, cm3 = st.columns(3)
                cm1.metric("Pedidos",  str(len(orders)))
                cm2.metric("Ingresos", fmt_short(rev))
                if last_ord:
                    st_cfg = STATUSES[last_ord["status"]]
                    cm3.metric("Último", st_cfg["emoji"])

                st.write("---")

# ─── REVENUE VIEW ─────────────────────────────────────────────────────────────
def view_revenue() -> None:
    s  = get_stats()
    cd = get_chart_data()

    st.title("💰 Ingresos")

    lock_orders = [o for o in s["done"] if o["type"] == "cerradura"]
    tech_orders = [o for o in s["done"] if o["type"] == "tecnico"]
    lock_rev    = sum(o["total"] for o in lock_orders)
    tech_rev    = sum(o["total"] for o in tech_orders)

    # ── Summary ──
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total acumulado",    fmt_short(s["total_rev"]),
              f"{len(s['done'])} órdenes completadas")
    c2.metric("🔐 Cerraduras",         fmt_short(lock_rev),
              f"{len(lock_orders)} instalaciones")
    c3.metric("🖥️ Servicios técnicos", fmt_short(tech_rev),
              f"{len(tech_orders)} servicios")

    if s["total_rev"] > 0:
        lock_pct = lock_rev / s["total_rev"]
        tech_pct = tech_rev / s["total_rev"]
        st.write("")
        st.write(f"🔐 Cerraduras — **{round(lock_pct*100)}%**")
        st.progress(lock_pct)
        st.write(f"🖥️ Servicios — **{round(tech_pct*100)}%**")
        st.progress(tech_pct)

    # ── Chart ──
    if cd:
        st.write("")
        st.subheader("📊 Evolución de ingresos")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Cerraduras",
            x=[r["name"] for r in cd], y=[r["cerraduras"] for r in cd],
            marker_color="#3b82f6", marker_line_width=0,
        ))
        fig.add_trace(go.Bar(
            name="Servicios",
            x=[r["name"] for r in cd], y=[r["servicios"] for r in cd],
            marker_color="#8b5cf6", marker_line_width=0,
        ))
        fig.update_layout(
            barmode="group",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=220, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", y=1.05, x=0),
            yaxis=dict(tickprefix="$", gridcolor="#f1f5f9"),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            font=dict(size=11),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── History table ──
    st.subheader("📋 Historial de pagos recibidos")
    sorted_done = sorted(s["done"], key=lambda o: o["id"], reverse=True)

    for o in sorted_done:
        cl     = get_client(o["cid"])
        ot     = ORDER_TYPES[o["type"]]
        c1,c2,c3,c4 = st.columns([3, 2, 2, 2])
        c1.write(f"{ot['icon']} **{cl['name'] if cl else '—'}**")
        c2.write(o.get("done") or o["date"])
        c3.write(f"**{fmt(o['total'])}**")
        c4.write(o.get("pay") or "—")
        st.divider()

    if not sorted_done:
        st.info("Sin ingresos registrados aún")

# ─── SERVICES VIEW ────────────────────────────────────────────────────────────
def view_services() -> None:
    d = st.session_state.data
    st.title("🛠️ Catálogo de servicios")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔐 Instalaciones de cerraduras")
        for s in [sv for sv in d["services"] if sv["cat"] == "instalacion"]:
            ca, cb = st.columns([3, 1])
            ca.write(f"🔧 **{s['name']}**")
            cb.write(f"**{fmt(s['price'])}**")
            st.divider()

    with col2:
        st.subheader("🖥️ Servicios técnicos")
        for s in [sv for sv in d["services"] if sv["cat"] == "tecnico"]:
            ca, cb = st.columns([3, 1])
            ca.write(f"⚙️ **{s['name']}**")
            cb.write(f"**{fmt(s['price'])}**")
            st.divider()

    st.info(
        "💡 Los datos se guardan en el archivo `techlock_data.json` junto a este script. "
        "Puedes editarlo directamente para modificar precios de servicios."
    )

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main() -> None:
    init_state()
    inject_css()
    render_sidebar()

    page = st.session_state.page

    if   page == "dashboard":  view_dashboard()
    elif page == "orders":     view_orders()
    elif page == "inventory":  view_inventory()
    elif page == "clients":    view_clients()
    elif page == "revenue":    view_revenue()
    elif page == "services":   view_services()

if __name__ == "__main__":
    main()
