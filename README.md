import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ==========================================
# CONFIGURACIÓN GLOBAL
# ==========================================
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "admin"
DB_NAME = 'vapehouse_datos.db'

conn = sqlite3.connect(DB_NAME)
conn.execute("PRAGMA journal_mode=WAL")

# ==========================================
# PALETA DE COLORES EMPRESARIAL
# ==========================================
C = {
    # Fondos
    "bg_dark":      "#0B1120",   # fondo principal ultra oscuro
    "bg_panel":     "#111827",   # paneles
    "bg_card":      "#1C2537",   # tarjetas
    "bg_card_h":    "#243045",   # tarjetas hover
    "bg_input":     "#1C2537",   # inputs
    "bg_table":     "#141E30",   # tabla fila par
    "bg_table_alt": "#0F1826",   # tabla fila impar

    # Textos
    "txt_white":    "#F0F4FF",
    "txt_muted":    "#7A8BA8",
    "txt_label":    "#A8B8D0",

    # Acentos principales
    "accent":       "#3B82F6",   # azul eléctrico
    "accent_hover": "#2563EB",
    "accent_glow":  "#60A5FA",

    # Colores semánticos
    "success":      "#10B981",
    "warning":      "#F59E0B",
    "danger":       "#EF4444",
    "purple":       "#8B5CF6",
    "cyan":         "#06B6D4",
    "gold":         "#F59E0B",

    # Bordes
    "border":       "#1E3050",
    "border_light": "#2D4A6E",

    # Separadores
    "divider":      "#1A2D48",
}

# ==========================================
# ESTILOS GLOBALES Y CONFIGURACIÓN TTK
# ==========================================

def apply_global_styles():
    style = ttk.Style()
    style.theme_use('default')

    # Notebook (pestañas)
    style.configure("Corp.TNotebook",
                    background=C["bg_panel"],
                    borderwidth=0,
                    tabmargins=[0, 0, 0, 0])
    style.configure("Corp.TNotebook.Tab",
                    background=C["bg_card"],
                    foreground=C["txt_muted"],
                    padding=[18, 10],
                    font=("Segoe UI", 9, "bold"),
                    borderwidth=0)
    style.map("Corp.TNotebook.Tab",
              background=[("selected", C["accent"]), ("active", C["bg_card_h"])],
              foreground=[("selected", C["txt_white"]), ("active", C["txt_white"])])

    # Treeview principal
    style.configure("Corp.Treeview",
                    background=C["bg_table"],
                    fieldbackground=C["bg_table"],
                    foreground=C["txt_white"],
                    rowheight=30,
                    font=("Segoe UI", 9),
                    borderwidth=0,
                    relief="flat")
    style.configure("Corp.Treeview.Heading",
                    background=C["bg_card"],
                    foreground=C["accent_glow"],
                    font=("Segoe UI", 9, "bold"),
                    relief="flat",
                    borderwidth=0)
    style.map("Corp.Treeview",
              background=[("selected", C["accent"])],
              foreground=[("selected", C["txt_white"])])

    # Combobox
    style.configure("Corp.TCombobox",
                    fieldbackground=C["bg_input"],
                    background=C["bg_input"],
                    foreground=C["txt_white"],
                    arrowcolor=C["accent"],
                    borderwidth=1,
                    relief="flat",
                    padding=8)

    # Scrollbar
    style.configure("Corp.Vertical.TScrollbar",
                    background=C["bg_card"],
                    troughcolor=C["bg_dark"],
                    arrowcolor=C["txt_muted"],
                    borderwidth=0,
                    relief="flat")

    return style

# ==========================================
# UTILIDADES DE UI
# ==========================================

def make_window(title, width, height, parent=None):
    """Crea una ventana con estilo corporativo consistente."""
    if parent:
        w = tk.Toplevel(parent)
    else:
        w = tk.Toplevel()
    w.title(title)
    w.geometry(f"{width}x{height}")
    w.configure(bg=C["bg_dark"])
    w.grab_set()
    # Centrar ventana
    w.update_idletasks()
    x = (w.winfo_screenwidth() - width) // 2
    y = (w.winfo_screenheight() - height) // 2
    w.geometry(f"{width}x{height}+{x}+{y}")
    return w

def header_bar(parent, title, subtitle=None, icon=None):
    """Barra de encabezado profesional para ventanas."""
    bar = tk.Frame(parent, bg=C["bg_panel"], height=80)
    bar.pack(fill="x")
    bar.pack_propagate(False)

    inner = tk.Frame(bar, bg=C["bg_panel"])
    inner.pack(side="left", padx=28, pady=12)

    if icon:
        tk.Label(inner, text=icon, font=("Segoe UI Emoji", 22),
                 fg=C["accent"], bg=C["bg_panel"]).pack(side="left", padx=(0, 12))

    txt_frame = tk.Frame(inner, bg=C["bg_panel"])
    txt_frame.pack(side="left")
    tk.Label(txt_frame, text=title, font=("Segoe UI", 16, "bold"),
             fg=C["txt_white"], bg=C["bg_panel"]).pack(anchor="w")
    if subtitle:
        tk.Label(txt_frame, text=subtitle, font=("Segoe UI", 9),
                 fg=C["txt_muted"], bg=C["bg_panel"]).pack(anchor="w")

    # Línea separadora
    sep = tk.Frame(parent, bg=C["accent"], height=2)
    sep.pack(fill="x")
    return bar

def corp_button(parent, text, command, style="primary", width=None, height=None, icon=None):
    """Botón con estilo corporativo."""
    styles = {
        "primary":  (C["accent"],   C["txt_white"],  C["accent_hover"]),
        "success":  (C["success"],  C["txt_white"],  "#059669"),
        "danger":   (C["danger"],   C["txt_white"],  "#DC2626"),
        "warning":  (C["warning"],  "#0B1120",       "#D97706"),
        "ghost":    (C["bg_card"],  C["txt_label"],  C["bg_card_h"]),
        "dark":     ("#1E293B",     C["txt_muted"],  "#273449"),
    }
    bg, fg, bg_h = styles.get(style, styles["primary"])
    label = f"{icon}  {text}" if icon else text

    btn = tk.Button(
        parent, text=label, command=command,
        bg=bg, fg=fg, activebackground=bg_h, activeforeground=fg,
        font=("Segoe UI", 9, "bold"),
        relief="flat", bd=0, cursor="hand2",
        padx=16, pady=8
    )
    if width:  btn.config(width=width)
    if height: btn.config(height=height)

    def on_enter(e): btn.config(bg=bg_h)
    def on_leave(e): btn.config(bg=bg)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def corp_entry(parent, **kwargs):
    """Entry con estilo corporativo."""
    e = tk.Entry(parent,
                 bg=C["bg_input"], fg=C["txt_white"],
                 insertbackground=C["accent"],
                 relief="flat", bd=0,
                 font=("Segoe UI", 10),
                 highlightthickness=1,
                 highlightbackground=C["border"],
                 highlightcolor=C["accent"],
                 **kwargs)
    return e

def kpi_card(parent, title, value, subtitle, color, width=180):
    """Tarjeta KPI para dashboards."""
    card = tk.Frame(parent, bg=C["bg_card"], width=width,
                    highlightthickness=1, highlightbackground=color)
    card.pack_propagate(False)
    inner = tk.Frame(card, bg=C["bg_card"])
    inner.pack(expand=True, fill="both", padx=16, pady=12)

    # Barra de color superior
    accent_bar = tk.Frame(card, bg=color, height=3)
    accent_bar.place(x=0, y=0, relwidth=1)

    tk.Label(inner, text=title, font=("Segoe UI", 8, "bold"),
             fg=C["txt_muted"], bg=C["bg_card"]).pack(anchor="w")
    tk.Label(inner, text=value, font=("Segoe UI", 18, "bold"),
             fg=color, bg=C["bg_card"]).pack(anchor="w", pady=(4, 0))
    tk.Label(inner, text=subtitle, font=("Segoe UI", 8),
             fg=C["txt_muted"], bg=C["bg_card"]).pack(anchor="w")
    return card

def section_label(parent, text):
    """Etiqueta de sección con línea decorativa."""
    f = tk.Frame(parent, bg=C["bg_dark"])
    f.pack(fill="x", padx=20, pady=(12, 4))
    tk.Label(f, text=text.upper(), font=("Segoe UI", 8, "bold"),
             fg=C["txt_muted"], bg=C["bg_dark"]).pack(side="left")
    tk.Frame(f, bg=C["border"], height=1).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=6)

def card_frame(parent, title=None, padx=16, pady=12):
    """Frame con estilo de tarjeta."""
    outer = tk.Frame(parent, bg=C["bg_card"],
                     highlightthickness=1, highlightbackground=C["border"])
    outer.pack(fill="x", padx=20, pady=6)
    if title:
        tk.Label(outer, text=title, font=("Segoe UI", 9, "bold"),
                 fg=C["accent_glow"], bg=C["bg_card"]).pack(anchor="w", padx=padx, pady=(10, 4))
        tk.Frame(outer, bg=C["border"], height=1).pack(fill="x", padx=padx)
    inner = tk.Frame(outer, bg=C["bg_card"])
    inner.pack(fill="x", padx=padx, pady=pady)
    return inner

def make_treeview(parent, cols, widths, height=12):
    """Treeview con estilo corporativo y scrollbar."""
    frame = tk.Frame(parent, bg=C["bg_dark"],
                     highlightthickness=1, highlightbackground=C["border"])
    frame.pack(fill="both", expand=True, padx=20, pady=6)
    sb = ttk.Scrollbar(frame, orient="vertical", style="Corp.Vertical.TScrollbar")
    sb_h = ttk.Scrollbar(frame, orient="horizontal")
    t = ttk.Treeview(frame, columns=cols, show="headings", height=height,
                     style="Corp.Treeview",
                     yscrollcommand=sb.set, xscrollcommand=sb_h.set)
    sb.config(command=t.yview)
    sb_h.config(command=t.xview)
    for col, w in zip(cols, widths):
        t.heading(col, text=col)
        t.column(col, width=w, anchor="center", minwidth=60)
    t.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    t.tag_configure('alt', background=C["bg_table_alt"])
    t.tag_configure('row', background=C["bg_table"])
    t.tag_configure('alerta', foreground=C["danger"], font=("Segoe UI", 9, "bold"))
    return t

def bottom_bar(parent, buttons_config):
    """Barra inferior con botones de acción."""
    bar = tk.Frame(parent, bg=C["bg_panel"], height=60)
    bar.pack(fill="x", side="bottom")
    bar.pack_propagate(False)
    sep = tk.Frame(bar, bg=C["border"], height=1)
    sep.pack(fill="x")
    inner = tk.Frame(bar, bg=C["bg_panel"])
    inner.pack(expand=True)
    for text, cmd, style in buttons_config:
        corp_button(inner, text, cmd, style=style).pack(side="left", padx=6, pady=10)
    return bar

# ==========================================
# BASE DE DATOS
# ==========================================

def iniciar_db():
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        categoria TEXT, nombre TEXT, costo REAL, venta REAL, cantidad INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
                        id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT, producto TEXT, unidades INTEGER, ganancia REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS historial (
                        id_mov INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT, producto TEXT, tipo_mov TEXT, cantidad_mov INTEGER, detalle TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS gastos (
                        id_gasto INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT, concepto TEXT, monto REAL)''')
    conn.commit()

def registrar_movimiento(producto, tipo, cantidad, detalle):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    conn.execute("INSERT INTO historial (fecha, producto, tipo_mov, cantidad_mov, detalle) VALUES (?,?,?,?,?)",
                 (fecha, producto, tipo, cantidad, detalle))
    conn.commit()

def actualizar_tabla_inv(tabla, filtro=""):
    tabla.delete(*tabla.get_children())
    cursor = conn.cursor()
    if filtro:
        cursor.execute("SELECT * FROM productos WHERE LOWER(nombre) LIKE ? OR LOWER(categoria) LIKE ?",
                       (f'%{filtro.lower()}%', f'%{filtro.lower()}%'))
    else:
        cursor.execute("SELECT * FROM productos")
    for i, fila in enumerate(cursor.fetchall()):
        tag = 'alerta' if fila[5] <= 3 else ('row' if i % 2 == 0 else 'alt')
        tabla.insert('', tk.END, values=fila, tags=(tag,))

# ==========================================
# PDF (sin cambios funcionales)
# ==========================================

def exportar_pdf(titulo_reporte, columnas, filas):
    if not filas:
        messagebox.showwarning("Sin datos", "No hay datos para exportar.")
        return
    archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
        initialfile=f"Reporte_{titulo_reporte}_{datetime.now().strftime('%d_%m_%Y')}")
    if not archivo: return
    try:
        doc = SimpleDocTemplate(archivo, pagesize=letter)
        elementos = []; estilos = getSampleStyleSheet()
        elementos.append(Paragraph(f"VAPEHOUSE — REPORTE: {titulo_reporte}", estilos['Title']))
        elementos.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos['Normal']))
        elementos.append(Spacer(1, 12))
        datos_tabla = [columnas] + [list(f) for f in filas]
        t = Table(datos_tabla)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1'))
        ]))
        elementos.append(t)
        doc.build(elementos)
        messagebox.showinfo("PDF Generado", f"Archivo guardado:\n{archivo}")
    except Exception as e:
        messagebox.showerror("Error al generar PDF", str(e))

# ==========================================
# VENTANA: GASTO / GANANCIA
# ==========================================

def abrir_analisis():
    v = make_window("Gasto / Ganancia", 900, 900)
    header_bar(v, "Gasto / Ganancia", "Control financiero del negocio", "💰")

    # Tarjeta de registro
    reg_card = card_frame(v, "  ➕  Registrar Nuevo Gasto o Inversión")

    tk.Label(reg_card, text="Concepto", font=("Segoe UI", 9),
             fg=C["txt_label"], bg=C["bg_card"]).grid(row=0, column=0, sticky="w", pady=4)
    ent_con = corp_entry(reg_card, width=32)
    ent_con.grid(row=0, column=1, padx=12, pady=4, ipady=6)

    tk.Label(reg_card, text="Monto ($)", font=("Segoe UI", 9),
             fg=C["txt_label"], bg=C["bg_card"]).grid(row=1, column=0, sticky="w", pady=4)
    ent_mon = corp_entry(reg_card, width=32)
    ent_mon.grid(row=1, column=1, padx=12, pady=4, ipady=6)

    def guardar_gasto():
        try:
            con, mon = ent_con.get().strip(), float(ent_mon.get())
            if not con: raise ValueError
            conn.execute("INSERT INTO gastos (fecha, concepto, monto) VALUES (?,?,?)",
                         (datetime.now().strftime("%d/%m/%Y"), con, mon))
            conn.commit()
            messagebox.showinfo("Registrado", "Gasto registrado correctamente.")
            ent_con.delete(0, tk.END); ent_mon.delete(0, tk.END)
            actualizar_resumen("HOY")
        except:
            messagebox.showerror("Error", "Verifica los datos ingresados.")

    corp_button(reg_card, "Registrar Gasto", guardar_gasto, "warning").grid(row=2, column=1, sticky="e", pady=10)

    # KPIs de resumen
    kpi_frame = tk.Frame(v, bg=C["bg_dark"])
    kpi_frame.pack(fill="x", padx=20, pady=8)

    lbl_v = tk.Label(kpi_frame, text="Ganancia Bruta: $0.00",
                     font=("Segoe UI", 12, "bold"), fg=C["accent"], bg=C["bg_dark"])
    lbl_v.pack(side="left", expand=True)
    lbl_g = tk.Label(kpi_frame, text="Gastos: $0.00",
                     font=("Segoe UI", 12, "bold"), fg=C["danger"], bg=C["bg_dark"])
    lbl_g.pack(side="left", expand=True)
    lbl_u = tk.Label(kpi_frame, text="UTILIDAD: $0.00",
                     font=("Segoe UI", 16, "bold"), fg=C["success"], bg=C["bg_dark"])
    lbl_u.pack(side="left", expand=True)

    section_label(v, "Detalle de gastos del periodo")
    cols = ("ID", "FECHA", "CONCEPTO", "MONTO")
    tabla_gastos = make_treeview(v, cols, [60, 120, 280, 120], height=8)

    datos_pdf = {"modo": "HOY", "filas": [], "v": 0, "g": 0}

    def actualizar_resumen(modo, resetear=False):
        cursor = conn.cursor(); hoy = datetime.now()
        tabla_gastos.delete(*tabla_gastos.get_children())
        datos_pdf["modo"] = modo

        if modo == "HOY":
            f_v = f"{hoy.strftime('%d/%m/%Y')}%"; f_g = hoy.strftime('%d/%m/%Y')
            q_v = "SELECT SUM(ganancia) FROM ventas WHERE fecha LIKE ?"
            q_g_sum = "SELECT SUM(monto) FROM gastos WHERE fecha = ?"
            q_g_all = "SELECT * FROM gastos WHERE fecha = ?"
            q_reset = "DELETE FROM gastos WHERE fecha = ?"
            params_v, params_g = (f_v,), (f_g,)
        elif modo == "SEMANAL":
            h_s = (hoy - timedelta(days=7)).strftime('%Y%m%d')
            cond = "(substr(fecha,7,4)||substr(fecha,4,2)||substr(fecha,1,2)) >= ?"
            q_v = f"SELECT SUM(ganancia) FROM ventas WHERE {cond}"
            q_g_sum = f"SELECT SUM(monto) FROM gastos WHERE {cond}"
            q_g_all = f"SELECT * FROM gastos WHERE {cond}"
            q_reset = f"DELETE FROM gastos WHERE {cond}"
            params_v, params_g = (h_s,), (h_s,)
        elif modo == "MENSUAL":
            f_mes = f"%/{hoy.strftime('%m/%Y')}%"
            q_v = "SELECT SUM(ganancia) FROM ventas WHERE fecha LIKE ?"
            q_g_sum = "SELECT SUM(monto) FROM gastos WHERE fecha LIKE ?"
            q_g_all = "SELECT * FROM gastos WHERE fecha LIKE ?"
            q_reset = "DELETE FROM gastos WHERE fecha LIKE ?"
            params_v, params_g = (f_mes,), (f_mes,)
        elif modo == "ANUAL":
            f_anio = f"%/%/{hoy.strftime('%Y')}%"
            q_v = "SELECT SUM(ganancia) FROM ventas WHERE fecha LIKE ?"
            q_g_sum = "SELECT SUM(monto) FROM gastos WHERE fecha LIKE ?"
            q_g_all = "SELECT * FROM gastos WHERE fecha LIKE ?"
            q_reset = "DELETE FROM gastos WHERE fecha LIKE ?"
            params_v, params_g = (f_anio,), (f_anio,)
        else:
            q_v = "SELECT SUM(ganancia) FROM ventas"
            q_g_sum = "SELECT SUM(monto) FROM gastos"
            q_g_all = "SELECT * FROM gastos"
            q_reset = "DELETE FROM gastos"
            params_v, params_g = (), ()

        if resetear:
            if messagebox.askyesno("Confirmar Reset", f"¿Limpiar gastos del periodo: {modo}?"):
                conn.execute(q_reset, params_g); conn.commit()

        cursor.execute(q_v, params_v); val = cursor.fetchone()[0] or 0
        cursor.execute(q_g_sum, params_g); g = cursor.fetchone()[0] or 0
        cursor.execute(q_g_all, params_g); filas = cursor.fetchall()

        datos_pdf.update({"filas": filas, "v": val, "g": g})
        for i, fila in enumerate(filas):
            tabla_gastos.insert('', tk.END, values=fila, tags=('row' if i % 2 == 0 else 'alt',))

        lbl_v.config(text=f"Ganancia Bruta ({modo}): ${val:,.2f}")
        lbl_g.config(text=f"Gastos ({modo}): ${g:,.2f}")
        lbl_u.config(text=f"UTILIDAD REAL: ${val - g:,.2f}",
                     fg=C["success"] if val - g >= 0 else C["danger"])

    # Botones de periodo
    section_label(v, "Filtrar por periodo")
    f_btns = tk.Frame(v, bg=C["bg_dark"]); f_btns.pack(pady=4, padx=20, fill="x")
    periodos = [("HOY", "primary"), ("SEMANAL", "ghost"), ("MENSUAL", "ghost"),
                ("ANUAL", "ghost"), ("TOTAL", "ghost")]
    for m, sty in periodos:
        col = tk.Frame(f_btns, bg=C["bg_dark"]); col.pack(side="left", padx=4)
        corp_button(col, m, lambda modo=m: actualizar_resumen(modo), sty).pack()
        corp_button(col, "⟳ Reset", lambda modo=m: actualizar_resumen(modo, True), "danger").pack(pady=3)

    def imprimir_balance_pdf():
        d = datos_pdf
        archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Balance_{d['modo']}_{datetime.now().strftime('%d_%m_%Y')}")
        if not archivo: return
        try:
            doc = SimpleDocTemplate(archivo, pagesize=letter)
            elementos = []; estilos = getSampleStyleSheet()
            elementos.append(Paragraph(f"VAPEHOUSE — BALANCE ({d['modo']})", estilos['Title']))
            elementos.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos['Normal']))
            elementos.append(Spacer(1, 20))
            resumen = [
                ["GANANCIA BRUTA:", f"${d['v']:,.2f}"],
                ["GASTOS / INVERSIÓN:", f"${d['g']:,.2f}"],
                ["UTILIDAD NETA:", f"${d['v'] - d['g']:,.2f}"]
            ]
            rt = Table(resumen, colWidths=[200, 120])
            rt.setStyle(TableStyle([
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 2), (-1, 2), 13),
                ('TEXTCOLOR', (0, 2), (1, 2), colors.HexColor('#10B981')),
                ('ALIGN', (1, 0), (1, 2), 'RIGHT'),
            ]))
            elementos.append(rt)
            if d['filas']:
                elementos.append(Spacer(1, 20))
                elementos.append(Paragraph("DETALLE DE GASTOS:", estilos['Heading3']))
                datos_tabla = [("ID", "FECHA", "CONCEPTO", "MONTO")] + [list(f) for f in d['filas']]
                t = Table(datos_tabla)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1'))
                ]))
                elementos.append(t)
            doc.build(elementos)
            messagebox.showinfo("PDF Generado", "Balance exportado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    bottom_bar(v, [
        ("📄  Imprimir Balance PDF", imprimir_balance_pdf, "primary"),
        ("← Volver", v.destroy, "dark"),
    ])
    actualizar_resumen("HOY")

# ==========================================
# VENTANA: CONTABILIDAD
# ==========================================

def abrir_contabilidad():
    v = make_window("Contabilidad — Reportes de Ventas", 1050, 860)
    header_bar(v, "Reportes de Ventas", "Historial completo de transacciones", "📊")

    nb = ttk.Notebook(v, style="Corp.TNotebook")
    nb.pack(pady=8, padx=20, fill="both", expand=True)

    def filtrar_y_obtener(modo):
        cursor = conn.cursor(); hoy = datetime.now()
        if modo == "HOY":
            cursor.execute("SELECT * FROM ventas WHERE fecha LIKE ?", (f"{hoy.strftime('%d/%m/%Y')}%",))
        elif modo == "SEMANAL":
            h_s = (hoy - timedelta(days=7)).strftime('%Y%m%d')
            cursor.execute("SELECT * FROM ventas WHERE (substr(fecha,7,4)||substr(fecha,4,2)||substr(fecha,1,2)) >= ?", (h_s,))
        elif modo == "MES ACTUAL":
            cursor.execute("SELECT * FROM ventas WHERE fecha LIKE ?", (f"%/{hoy.strftime('%m/%Y')}%",))
        elif modo == "AÑO ACTUAL":
            cursor.execute("SELECT * FROM ventas WHERE fecha LIKE ?", (f"%/%/{hoy.strftime('%Y')}%",))
        else:
            cursor.execute("SELECT * FROM ventas")
        return cursor.fetchall()

    def crear_pestana(nombre, modo_filtro):
        frame = tk.Frame(nb, bg=C["bg_dark"]); nb.add(frame, text=f"  {nombre}  ")
        cols = ("ID", "FECHA / HORA", "PRODUCTO", "UNIDADES", "GANANCIA")
        t = make_treeview(frame, cols, [60, 160, 280, 90, 120], height=16)
        lbl_sum = tk.Label(frame, text="Total: $0.00",
                           font=("Segoe UI", 18, "bold"), fg=C["success"], bg=C["bg_dark"])
        lbl_sum.pack(pady=6)

        def refresh():
            t.delete(*t.get_children())
            filas = filtrar_y_obtener(modo_filtro); total = 0
            for i, f in enumerate(filas):
                t.insert('', tk.END, values=f, tags=('row' if i % 2 == 0 else 'alt',))
                total += f[4]
            lbl_sum.config(text=f"Total {nombre}: ${total:,.2f}")
            return filas

        btn_frame = tk.Frame(frame, bg=C["bg_dark"]); btn_frame.pack(pady=6)
        corp_button(btn_frame, "📄  Exportar PDF",
                    lambda: exportar_pdf(f"VENTAS_{modo_filtro}", cols, filtrar_y_obtener(modo_filtro)),
                    "primary").pack(side="left", padx=6)
        corp_button(btn_frame, "🗑  Resetear Ventas",
                    lambda: [conn.execute("DELETE FROM ventas" if modo_filtro == "REPORTE GENERAL"
                                          else "DELETE FROM ventas WHERE fecha LIKE ?",
                                         () if modo_filtro == "REPORTE GENERAL"
                                         else (f"{datetime.now().strftime('%d/%m/%Y')}%",)),
                             conn.commit(), refresh()],
                    "danger").pack(side="left", padx=6)
        refresh()

    for n, m in [("Hoy", "HOY"), ("Semanal", "SEMANAL"), ("Mes Actual", "MES ACTUAL"),
                 ("Año Actual", "AÑO ACTUAL"), ("General", "REPORTE GENERAL")]:
        crear_pestana(n, m)

    bottom_bar(v, [("← Volver", v.destroy, "dark")])

# ==========================================
# VENTANA: HISTORIAL
# ==========================================

def abrir_historial():
    v = make_window("Historial de Movimientos", 1000, 720)
    header_bar(v, "Historial de Movimientos", "Registro completo de operaciones", "📋")

    cols = ("FECHA / HORA", "PRODUCTO", "TIPO", "CANT.", "DETALLE")
    tabla_h = make_treeview(v, cols, [160, 200, 120, 70, 300], height=18)
    tabla_h.tag_configure('VENTA',      foreground=C["success"])
    tabla_h.tag_configure('ENTRADA',    foreground=C["accent"])
    tabla_h.tag_configure('INGRESO',    foreground=C["purple"])
    tabla_h.tag_configure('ELIMINACION',foreground=C["danger"])

    def cargar_historial():
        tabla_h.delete(*tabla_h.get_children())
        cursor = conn.cursor()
        cursor.execute("SELECT fecha, producto, tipo_mov, cantidad_mov, detalle FROM historial ORDER BY id_mov DESC")
        for f in cursor.fetchall():
            tipo = f[2]
            tag = ('VENTA' if 'VENTA' in tipo else
                   'INGRESO' if 'INGRESO' in tipo else
                   'ENTRADA' if 'ENTRADA' in tipo else
                   'ELIMINACION' if 'ELIMINACION' in tipo.upper() else 'row')
            tabla_h.insert('', tk.END, values=f, tags=(tag,))

    def reset_historial():
        if messagebox.askyesno("Confirmar", "¿Desea limpiar todo el historial de movimientos?"):
            conn.execute("DELETE FROM historial"); conn.commit(); cargar_historial()

    bottom_bar(v, [
        ("🗑  Limpiar Historial", reset_historial, "danger"),
        ("← Volver", v.destroy, "dark"),
    ])
    cargar_historial()

# ==========================================
# VENTANA: FACTURAS
# ==========================================

def abrir_facturas():
    v = make_window("Control de Facturas", 950, 720)
    header_bar(v, "Control de Facturas", "Registro y exportación de transacciones", "🧾")

    cols = ("ID", "FECHA / HORA", "PRODUCTO", "UNIDADES", "TOTAL VENTA")
    tabla_f = make_treeview(v, cols, [60, 160, 280, 90, 120], height=16)

    def cargar_f():
        tabla_f.delete(*tabla_f.get_children())
        cursor = conn.cursor()
        cursor.execute("SELECT id_venta, fecha, producto, unidades, ganancia FROM ventas ORDER BY id_venta DESC")
        for i, f in enumerate(cursor.fetchall()):
            tabla_f.insert('', tk.END, values=f, tags=('row' if i % 2 == 0 else 'alt',))

    def reset_f():
        if messagebox.askyesno("Confirmar", "¿Eliminar todas las facturas registradas?"):
            conn.execute("DELETE FROM ventas"); conn.commit(); cargar_f()

    def imprimir_f():
        cursor = conn.cursor(); cursor.execute("SELECT * FROM ventas")
        exportar_pdf("FACTURAS", cols, cursor.fetchall())

    bottom_bar(v, [
        ("📄  Exportar PDF", imprimir_f, "primary"),
        ("🗑  Reset Facturas", reset_f, "danger"),
        ("← Volver", v.destroy, "dark"),
    ])
    cargar_f()

# ==========================================
# FACTURA PDF CON DATOS CLIENTE
# ==========================================

def generar_factura_cliente(datos_cliente, producto, cantidad, precio_unit, total_venta, id_venta):
    archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
        initialfile=f"Factura_{id_venta:05d}_{datos_cliente['cedula']}_{datetime.now().strftime('%d_%m_%Y')}")
    if not archivo: return
    try:
        doc = SimpleDocTemplate(archivo, pagesize=letter,
                                topMargin=40, bottomMargin=40, leftMargin=50, rightMargin=50)
        elementos = []; estilos = getSampleStyleSheet()
        elementos.append(Paragraph("VAPEHOUSE", estilos['Title']))
        elementos.append(Paragraph("FACTURA DE VENTA", estilos['Heading2']))
        elementos.append(Spacer(1, 6))
        elementos.append(Paragraph(
            f"No. Factura: <b>{id_venta:05d}</b>  |  Fecha: <b>{datetime.now().strftime('%d/%m/%Y %H:%M')}</b>",
            estilos['Normal']))
        elementos.append(Spacer(1, 16))
        elementos.append(Paragraph("DATOS DEL CLIENTE", estilos['Heading3']))
        datos_cli_tabla = [
            ["Nombre completo:", f"{datos_cliente['nombre']} {datos_cliente['apellido']}"],
            ["Cédula / ID:", datos_cliente['cedula']],
            ["Teléfono:", datos_cliente['telefono']],
            ["Correo electrónico:", datos_cliente['correo']],
        ]
        t_cli = Table(datos_cli_tabla, colWidths=[150, 300])
        t_cli.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_cli)
        elementos.append(Spacer(1, 16))
        elementos.append(Paragraph("DETALLE DE LA VENTA", estilos['Heading3']))
        t_prod = Table(
            [["PRODUCTO", "CANT.", "PRECIO UNIT.", "TOTAL"],
             [producto, str(cantidad), f"${precio_unit:,.2f}", f"${total_venta:,.2f}"]],
            colWidths=[220, 70, 110, 110])
        t_prod.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_prod)
        elementos.append(Spacer(1, 12))
        t_total = Table([["TOTAL A PAGAR:", f"${total_venta:,.2f}"]], colWidths=[300, 210])
        t_total.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#10B981')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_total)
        elementos.append(Spacer(1, 30))
        elementos.append(Paragraph("¡Gracias por su compra! — VAPEHOUSE", estilos['Normal']))
        doc.build(elementos)
        messagebox.showinfo("Factura Generada", f"Factura guardada:\n{archivo}")
    except Exception as e:
        messagebox.showerror("Error al generar factura", str(e))

# ==========================================
# FORMULARIO DATOS CLIENTE
# ==========================================

def formulario_datos_cliente(parent, producto_nombre, cantidad, precio_unit, total_venta, callback_confirmar):
    v_cli = make_window("Datos del Cliente", 460, 540)
    header_bar(v_cli, "Datos del Cliente", f"{producto_nombre} — Cant: {cantidad} — Total: ${total_venta:,.2f}", "👤")

    campos = [("Nombre", "nombre"), ("Apellido", "apellido"), ("Cédula / ID", "cedula"),
              ("Teléfono", "telefono"), ("Correo electrónico", "correo")]
    entradas = {}

    f_form = tk.Frame(v_cli, bg=C["bg_dark"]); f_form.pack(fill="x", padx=30, pady=16)
    for i, (label_txt, key) in enumerate(campos):
        tk.Label(f_form, text=label_txt, font=("Segoe UI", 9),
                 fg=C["txt_label"], bg=C["bg_dark"]).grid(row=i, column=0, sticky="w", pady=8, padx=(0, 16))
        ent = corp_entry(f_form, width=24)
        ent.grid(row=i, column=1, pady=8, ipady=7, sticky="ew")
        entradas[key] = ent
    f_form.columnconfigure(1, weight=1)

    # Nota de campos obligatorios
    tk.Label(v_cli, text="* Nombre, apellido y cédula son obligatorios",
             font=("Segoe UI", 8), fg=C["txt_muted"], bg=C["bg_dark"]).pack()

    def confirmar():
        datos = {k: v.get().strip() for k, v in entradas.items()}
        if not datos['nombre'] or not datos['apellido'] or not datos['cedula']:
            messagebox.showerror("Campos requeridos", "Nombre, apellido y cédula son obligatorios.", parent=v_cli)
            return
        v_cli.destroy()
        callback_confirmar(datos)

    bottom_bar(v_cli, [
        ("✅  Confirmar Venta", confirmar, "success"),
        ("✖  Cancelar", v_cli.destroy, "danger"),
    ])

# ==========================================
# VENTANA: INVENTARIO
# ==========================================

def abrir_inventario():
    v = make_window("Gestión de Inventario", 1000, 920)
    header_bar(v, "Gestión de Inventario", "Control de stock en tiempo real", "📦")

    # Barra de búsqueda
    f_search = tk.Frame(v, bg=C["bg_dark"]); f_search.pack(fill="x", padx=20, pady=8)
    tk.Label(f_search, text="🔍", font=("Segoe UI", 12), fg=C["accent"], bg=C["bg_dark"]).pack(side="left", padx=(0, 8))
    sv = tk.StringVar()
    ent_b = corp_entry(f_search, textvariable=sv, width=40)
    ent_b.pack(side="left", fill="x", expand=True, ipady=7)
    tk.Label(f_search, text="Buscar por nombre o categoría",
             font=("Segoe UI", 8), fg=C["txt_muted"], bg=C["bg_dark"]).pack(side="left", padx=10)

    # Tarjeta de formulario
    f_card = card_frame(v, "  ➕  Agregar / Actualizar Producto")

    categorias = ["Vapers", "Esencias", "Destilados", "Relojes", "Perfumes", "Gorras", "Camisetas"]
    cb_cat = ttk.Combobox(f_card, values=categorias, state="readonly",
                          style="Corp.TCombobox", width=20, font=("Segoe UI", 10))
    ent_n = corp_entry(f_card, width=22)
    ent_c = corp_entry(f_card, width=16)
    ent_v = corp_entry(f_card, width=16)
    ent_s = corp_entry(f_card, width=12)

    for i, (lbl, widget, r, c) in enumerate([
        ("Categoría", cb_cat, 0, 0), ("Nombre del producto", ent_n, 0, 2),
        ("Costo ($)", ent_c, 1, 0), ("Precio de venta ($)", ent_v, 1, 2), ("Unidades en stock", ent_s, 2, 0)
    ]):
        tk.Label(f_card, text=lbl, font=("Segoe UI", 9),
                 fg=C["txt_label"], bg=C["bg_card"]).grid(row=r, column=c, sticky="w", padx=(0, 8), pady=6)
        widget.grid(row=r, column=c + 1, padx=(0, 20), pady=6, ipady=6, sticky="ew")

    def guardar():
        try:
            cat, nom = cb_cat.get(), ent_n.get().strip()
            c_val, v_val, s_val = float(ent_c.get()), float(ent_v.get()), int(ent_s.get())
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM productos WHERE LOWER(nombre) = LOWER(?)", (nom,))
            ex = cursor.fetchone()
            if ex:
                if messagebox.askyesno("Producto existente", f"¿Sumar {s_val} unidades a '{nom}'?"):
                    conn.execute("UPDATE productos SET categoria=?, costo=?, venta=?, cantidad=cantidad+? WHERE id=?",
                                 (cat, c_val, v_val, s_val, ex[0]))
                    registrar_movimiento(nom, "ENTRADA", s_val, f"Reposición de stock")
            else:
                conn.execute("INSERT INTO productos (categoria, nombre, costo, venta, cantidad) VALUES (?,?,?,?,?)",
                             (cat, nom, c_val, v_val, s_val))
                registrar_movimiento(nom, "INGRESO", s_val, "Nuevo producto registrado")
            conn.commit(); actualizar_tabla_inv(tabla_inv)
            for e in [ent_n, ent_c, ent_v, ent_s]: e.delete(0, tk.END)
        except:
            messagebox.showerror("Error", "Verifica que los valores numéricos sean correctos.")

    corp_button(f_card, "Guardar Producto", guardar, "success").grid(row=2, column=2, columnspan=2, sticky="e", pady=10)

    sv.trace_add("write", lambda *args: actualizar_tabla_inv(tabla_inv, sv.get()))

    # Alerta de stock bajo
    tk.Label(v, text="⚠  Productos con 3 o menos unidades aparecen resaltados en rojo",
             font=("Segoe UI", 8), fg=C["warning"], bg=C["bg_dark"]).pack(padx=20, anchor="w")

    section_label(v, "Productos en inventario")
    cols = ("ID", "CATEGORÍA", "NOMBRE", "COSTO", "PRECIO VENTA", "STOCK")
    tabla_inv = make_treeview(v, cols, [50, 110, 240, 90, 110, 80], height=14)

    def vender_local():
        sel = tabla_inv.selection()
        if not sel: return
        cant = simpledialog.askinteger("Registrar Venta", "¿Cuántas unidades deseas vender?", minvalue=1)
        if not cant: return
        for item in sel:
            d = tabla_inv.item(item)['values']
            if int(d[5]) >= cant:
                precio_unit = float(d[4]); total_venta = precio_unit * cant
                gan = (precio_unit - float(d[3])) * cant
                prod_nombre = d[2]; prod_id = d[0]

                def procesar_venta(datos_cliente, _cant=cant, _gan=gan, _prod_nombre=prod_nombre,
                                   _prod_id=prod_id, _precio_unit=precio_unit, _total_venta=total_venta):
                    conn.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id = ?", (_cant, _prod_id))
                    conn.execute("INSERT INTO ventas (fecha, producto, unidades, ganancia) VALUES (?,?,?,?)",
                                 (datetime.now().strftime("%d/%m/%Y %H:%M"), _prod_nombre, _cant, _gan))
                    id_venta = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                    registrar_movimiento(_prod_nombre, "VENTA", _cant, "Venta realizada")
                    conn.commit(); actualizar_tabla_inv(tabla_inv)
                    generar_factura_cliente(datos_cliente, _prod_nombre, _cant, _precio_unit, _total_venta, id_venta)

                formulario_datos_cliente(v, prod_nombre, cant, precio_unit, total_venta, procesar_venta)
            else:
                messagebox.showwarning("Stock insuficiente", f"No hay suficiente stock de '{d[2]}'.")

    def eliminar_local():
        sel = tabla_inv.selection()
        if not sel or not messagebox.askyesno("Eliminar producto", "¿Borrar los productos seleccionados?"): return
        for item in sel:
            d = tabla_inv.item(item)['values']
            conn.execute("DELETE FROM productos WHERE id = ?", (d[0],))
            registrar_movimiento(d[2], "ELIMINACIÓN", 0, "Producto eliminado del sistema")
        conn.commit(); actualizar_tabla_inv(tabla_inv)

    bottom_bar(v, [
        ("💰  Vender", vender_local, "success"),
        ("📋  Historial", abrir_historial, "ghost"),
        ("🧾  Facturas", abrir_facturas, "primary"),
        ("🗑  Eliminar", eliminar_local, "danger"),
        ("← Volver", v.destroy, "dark"),
    ])
    actualizar_tabla_inv(tabla_inv)

# ==========================================
# VENTANA: ANÁLISIS BI
# ==========================================

def abrir_analisis_bi():
    v = make_window("Inteligencia de Negocios", 1150, 860)
    header_bar(v, "Inteligencia de Negocios", "Análisis estratégico y recomendaciones automáticas", "📊")

    nb_bi = ttk.Notebook(v, style="Corp.TNotebook")
    nb_bi.pack(pady=8, padx=20, fill="both", expand=True)

    # ── PESTAÑA 1: RENDIMIENTO ──
    tab1 = tk.Frame(nb_bi, bg=C["bg_dark"]); nb_bi.add(tab1, text="  📈  Rendimiento  ")

    # KPI cards
    f_kpi = tk.Frame(tab1, bg=C["bg_dark"]); f_kpi.pack(fill="x", padx=16, pady=10)
    kpi_vars = {}
    kpi_defs = [("HOY", C["success"]), ("ESTE MES", C["accent"]), ("ESTE AÑO", C["purple"]), ("TOTAL", C["warning"])]
    for titulo, color in kpi_defs:
        card = kpi_card(f_kpi, titulo, "$0.00", "0 ventas", color, width=230)
        card.pack(side="left", expand=True, fill="x", padx=5)
        kpi_vars[titulo] = (card.winfo_children()[0].winfo_children()[1],
                            card.winfo_children()[0].winfo_children()[2])

    tk.Label(tab1, text="Detalle diario — últimos 30 días",
             font=("Segoe UI", 9, "italic"), fg=C["txt_muted"], bg=C["bg_dark"]).pack(anchor="w", padx=20)
    cols_r = ("FECHA", "# VENTAS", "UNIDADES", "GANANCIA TOTAL", "TICKET PROMEDIO")
    t_rend = make_treeview(tab1, cols_r, [130, 100, 100, 150, 150], height=12)

    def cargar_rendimiento():
        cursor = conn.cursor(); hoy = datetime.now()
        periodos_bi = {
            "HOY": f"WHERE fecha LIKE '{hoy.strftime('%d/%m/%Y')}%'",
            "ESTE MES": f"WHERE fecha LIKE '%/{hoy.strftime('%m/%Y')}%'",
            "ESTE AÑO": f"WHERE fecha LIKE '%/%/{hoy.strftime('%Y')}%'",
            "TOTAL": ""
        }
        for titulo, cond in periodos_bi.items():
            cursor.execute(f"SELECT SUM(ganancia), COUNT(*) FROM ventas {cond}")
            row = cursor.fetchone(); gan = row[0] or 0; cnt = row[1] or 0
            kpi_vars[titulo][0].config(text=f"${gan:,.2f}")
            kpi_vars[titulo][1].config(text=f"{cnt} venta{'s' if cnt != 1 else ''}")
        t_rend.delete(*t_rend.get_children())
        for i in range(29, -1, -1):
            dia = (hoy - timedelta(days=i)).strftime('%d/%m/%Y')
            cursor.execute("SELECT COUNT(*), SUM(unidades), SUM(ganancia) FROM ventas WHERE fecha LIKE ?", (f"{dia}%",))
            r = cursor.fetchone(); cnt_v, unds, gan = r[0] or 0, r[1] or 0, r[2] or 0
            ticket = (gan / cnt_v) if cnt_v > 0 else 0
            tag = 'row' if i % 2 == 0 else 'alt'
            t_rend.insert('', tk.END, values=(dia, cnt_v, unds, f"${gan:,.2f}", f"${ticket:,.2f}"), tags=(tag,))

    corp_button(tab1, "🔄  Actualizar Datos", cargar_rendimiento, "primary").pack(pady=6)

    # ── PESTAÑA 2: PRODUCTOS ESTRELLA ──
    tab2 = tk.Frame(nb_bi, bg=C["bg_dark"]); nb_bi.add(tab2, text="  ⭐  Productos Estrella  ")
    tk.Label(tab2, text="Ranking de productos por rendimiento",
             font=("Segoe UI", 11, "bold"), fg=C["txt_white"], bg=C["bg_dark"]).pack(pady=8)
    f_filtro = tk.Frame(tab2, bg=C["bg_dark"]); f_filtro.pack(pady=4)
    tk.Label(f_filtro, text="Periodo:", fg=C["txt_label"], bg=C["bg_dark"],
             font=("Segoe UI", 9)).pack(side="left", padx=6)
    cb_periodo = ttk.Combobox(f_filtro, values=["HOY", "ESTE MES", "ESTE AÑO", "TOTAL"],
                              state="readonly", style="Corp.TCombobox", width=14)
    cb_periodo.set("ESTE MES"); cb_periodo.pack(side="left", padx=5)

    cols_e = ("RANK", "PRODUCTO", "UNIDADES VENDIDAS", "GANANCIA TOTAL", "# TRANSACCIONES", "MARGEN %")
    t_estrella = make_treeview(tab2, cols_e, [60, 220, 140, 140, 140, 110], height=14)
    t_estrella.tag_configure('oro',    foreground=C["gold"],    font=("Segoe UI", 9, "bold"))
    t_estrella.tag_configure('plata',  foreground="#C0C0C0")
    t_estrella.tag_configure('bronce', foreground="#CD7F32")

    def cargar_estrella():
        t_estrella.delete(*t_estrella.get_children())
        cursor = conn.cursor(); hoy = datetime.now()
        periodo = cb_periodo.get()
        cond = {"HOY": f"WHERE v.fecha LIKE '{hoy.strftime('%d/%m/%Y')}%'",
                "ESTE MES": f"WHERE v.fecha LIKE '%/{hoy.strftime('%m/%Y')}%'",
                "ESTE AÑO": f"WHERE v.fecha LIKE '%/%/{hoy.strftime('%Y')}%'",
                "TOTAL": ""}.get(periodo, "")
        cursor.execute(f"""
            SELECT v.producto, SUM(v.unidades), SUM(v.ganancia), COUNT(*), p.costo, p.venta
            FROM ventas v LEFT JOIN productos p ON LOWER(v.producto) = LOWER(p.nombre)
            {cond} GROUP BY v.producto ORDER BY SUM(v.unidades) DESC""")
        for i, f in enumerate(cursor.fetchall(), 1):
            prod, unds, gan, trans, costo, venta = f
            margen = ((venta - costo) / venta * 100) if venta and costo and venta > 0 else 0
            tag = 'oro' if i == 1 else 'plata' if i == 2 else 'bronce' if i == 3 else 'row'
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else str(i)
            t_estrella.insert('', tk.END,
                              values=(medal, prod, unds or 0, f"${gan or 0:,.2f}", trans, f"{margen:.1f}%"),
                              tags=(tag,))

    corp_button(tab2, "🔄  Actualizar Ranking", cargar_estrella, "warning").pack(pady=6)
    cb_periodo.bind("<<ComboboxSelected>>", lambda e: cargar_estrella())

    # ── PESTAÑA 3: RECOMENDACIONES BI ──
    tab3 = tk.Frame(nb_bi, bg=C["bg_dark"]); nb_bi.add(tab3, text="  🤖  Recomendaciones  ")
    tk.Label(tab3, text="Motor de Recomendaciones Estratégicas",
             font=("Segoe UI", 11, "bold"), fg=C["txt_white"], bg=C["bg_dark"]).pack(pady=8)

    f_alertas = tk.LabelFrame(tab3, text="  🚨  Alertas Críticas",
                               bg=C["bg_card"], fg=C["danger"],
                               font=("Segoe UI", 9, "bold"),
                               highlightthickness=1, highlightbackground=C["danger"],
                               padx=10, pady=8)
    f_alertas.pack(fill="x", padx=20, pady=5)
    txt_alertas = tk.Text(f_alertas, height=4, bg="#1a0000", fg="#FF6B6B",
                          font=("Consolas", 9), relief="flat", state="disabled", wrap="word")
    txt_alertas.pack(fill="x")

    f_opor = tk.LabelFrame(tab3, text="  💡  Oportunidades de Inversión",
                            bg=C["bg_card"], fg=C["success"],
                            font=("Segoe UI", 9, "bold"),
                            highlightthickness=1, highlightbackground=C["success"],
                            padx=10, pady=8)
    f_opor.pack(fill="x", padx=20, pady=5)
    txt_opor = tk.Text(f_opor, height=4, bg="#001a0a", fg=C["success"],
                       font=("Consolas", 9), relief="flat", state="disabled", wrap="word")
    txt_opor.pack(fill="x")

    tk.Label(tab3, text="Análisis cruzado: Margen × Stock × Rotación",
             font=("Segoe UI", 9, "italic"), fg=C["txt_muted"], bg=C["bg_dark"]).pack(pady=4)
    cols_bi = ("PRODUCTO", "STOCK", "MARGEN %", "VENTAS 30d", "DÍAS STOCK", "ESTADO", "ACCIÓN SUGERIDA")
    t_bi = make_treeview(tab3, cols_bi, [170, 65, 85, 85, 90, 110, 210], height=8)
    t_bi.tag_configure('critico',  foreground=C["danger"],  font=("Segoe UI", 9, "bold"))
    t_bi.tag_configure('invertir', foreground=C["success"], font=("Segoe UI", 9, "bold"))
    t_bi.tag_configure('revisar',  foreground=C["warning"])

    def cargar_recomendaciones():
        cursor = conn.cursor(); hoy = datetime.now()
        cursor.execute("SELECT id, nombre, costo, venta, cantidad FROM productos")
        productos_list = cursor.fetchall()
        alertas = []; oportunidades = []; t_bi.delete(*t_bi.get_children())
        for p in productos_list:
            pid, nombre, costo, precio_venta, stock = p
            margen = ((precio_venta - costo) / precio_venta * 100) if precio_venta > 0 else 0
            hace_30 = (hoy - timedelta(days=30)).strftime('%Y%m%d')
            cursor.execute("""SELECT SUM(unidades) FROM ventas WHERE LOWER(producto) = LOWER(?)
                              AND (substr(fecha,7,4)||substr(fecha,4,2)||substr(fecha,1,2)) >= ?""",
                           (nombre, hace_30))
            ventas_30 = cursor.fetchone()[0] or 0
            rotacion = ventas_30 / 30 if ventas_30 > 0 else 0
            dias_stock = int(stock / rotacion) if rotacion > 0 else 999
            if stock <= 3 and ventas_30 > 0:
                estado = "⚠️ CRÍTICO"; accion = "REPOSICIÓN URGENTE — alta demanda"; tag = 'critico'
                alertas.append(f"  ⚠  {nombre}: solo {stock} uds, {ventas_30} vendidas en 30d → REPONER")
            elif stock <= 3 and ventas_30 == 0:
                estado = "📦 SIN MOVIM."; accion = "Evaluar descontinuar o promocionar"; tag = 'revisar'
            elif margen >= 40 and ventas_30 >= 5:
                estado = "🌟 ESTRELLA"; accion = f"INVERTIR MÁS — margen {margen:.0f}%"; tag = 'invertir'
                oportunidades.append(f"  💰  {nombre}: margen {margen:.0f}%, {ventas_30} uds/30d → Ampliar stock")
            elif margen >= 40 and ventas_30 < 5:
                estado = "💎 ALTO MARGEN"; accion = "Promover — buen margen, baja rotación"; tag = 'revisar'
                oportunidades.append(f"  📢  {nombre}: margen {margen:.0f}% — necesita visibilidad")
            elif dias_stock < 7 and ventas_30 > 0:
                estado = "🔴 POR AGOTAR"; accion = f"Reponer — ~{dias_stock}d de stock"; tag = 'critico'
                alertas.append(f"  🔴  {nombre}: stock para ~{dias_stock} días → PLANIFICAR COMPRA")
            elif ventas_30 == 0 and stock > 10:
                estado = "❄️ ESTANCADO"; accion = "Sin ventas 30d — considerar descuento"; tag = 'revisar'
            else:
                estado = "✅ NORMAL"; accion = "Mantener operación actual"; tag = 'row'
            dias_txt = f"~{dias_stock}d" if dias_stock < 999 else "∞"
            t_bi.insert('', tk.END,
                        values=(nombre, stock, f"{margen:.1f}%", ventas_30, dias_txt, estado, accion),
                        tags=(tag,))
        for txt_w, lineas, default in [
            (txt_alertas, alertas, "  ✅  Sin alertas críticas."),
            (txt_opor, oportunidades, "  ℹ️  Sin oportunidades destacadas.")
        ]:
            txt_w.config(state="normal"); txt_w.delete(1.0, tk.END)
            txt_w.insert(tk.END, "\n".join(lineas) if lineas else default)
            txt_w.config(state="disabled")

    corp_button(tab3, "🤖  Generar Análisis Completo", cargar_recomendaciones, "cyan" if False else "primary").pack(pady=8)

    cargar_rendimiento(); cargar_estrella(); cargar_recomendaciones()
    bottom_bar(v, [("← Volver", v.destroy, "dark")])

# ==========================================
# MENÚ PRINCIPAL — DISEÑO CON TILES GRANDES
# ==========================================

def mostrar_menu_principal():
    menu = tk.Toplevel()
    menu.title("VapeHouse — Panel de Control")
    menu.geometry("560x780")
    menu.configure(bg=C["bg_dark"])
    menu.protocol("WM_DELETE_WINDOW", lambda: root.destroy())

    # Centrar
    menu.update_idletasks()
    x = (menu.winfo_screenwidth() - 560) // 2
    y = (menu.winfo_screenheight() - 780) // 2
    menu.geometry(f"560x780+{x}+{y}")

    # Encabezado branding
    top = tk.Frame(menu, bg=C["bg_panel"], height=130)
    top.pack(fill="x"); top.pack_propagate(False)

    # Línea decorativa de color
    tk.Frame(top, bg=C["accent"], height=4).pack(fill="x")

    brand = tk.Frame(top, bg=C["bg_panel"])
    brand.pack(expand=True)
    tk.Label(brand, text="VAPEHOUSE", font=("Segoe UI", 34, "bold"),
             fg=C["txt_white"], bg=C["bg_panel"]).pack()
    tk.Label(brand, text="SISTEMA DE GESTIÓN EMPRESARIAL",
             font=("Segoe UI", 9), fg=C["txt_muted"], bg=C["bg_panel"]).pack()

    tk.Frame(menu, bg=C["border"], height=1).pack(fill="x")

    # Fecha/hora
    hoy_str = datetime.now().strftime("%A, %d de %B de %Y").capitalize()
    tk.Label(menu, text=hoy_str, font=("Segoe UI", 9),
             fg=C["txt_muted"], bg=C["bg_dark"]).pack(pady=10)

    # Grid de módulos — 2 columnas
    grid = tk.Frame(menu, bg=C["bg_dark"])
    grid.pack(padx=24, pady=6, fill="both", expand=True)
    grid.columnconfigure(0, weight=1)
    grid.columnconfigure(1, weight=1)

    modules = [
        ("📦", "Inventario",         "Stock y productos",      abrir_inventario,    C["success"],  0, 0),
        ("📊", "Contabilidad",       "Reportes de ventas",     abrir_contabilidad,  C["accent"],   0, 1),
        ("💰", "Gasto / Ganancia",   "Control financiero",     abrir_analisis,      C["warning"],  1, 0),
        ("🧠", "Análisis BI",        "Inteligencia de negocios", abrir_analisis_bi, C["purple"],   1, 1),
    ]

    for icon, title, subtitle, cmd, color, row, col in modules:
        card = tk.Frame(grid, bg=C["bg_card"], cursor="hand2",
                        highlightthickness=1, highlightbackground=C["border"])
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew", ipady=10)
        grid.rowconfigure(row, weight=1)

        # Barra de color superior de la card
        bar = tk.Frame(card, bg=color, height=4)
        bar.pack(fill="x")

        inner = tk.Frame(card, bg=C["bg_card"]); inner.pack(expand=True, pady=16)
        tk.Label(inner, text=icon, font=("Segoe UI Emoji", 36),
                 fg=color, bg=C["bg_card"]).pack()
        tk.Label(inner, text=title, font=("Segoe UI", 13, "bold"),
                 fg=C["txt_white"], bg=C["bg_card"]).pack(pady=(6, 2))
        tk.Label(inner, text=subtitle, font=("Segoe UI", 9),
                 fg=C["txt_muted"], bg=C["bg_card"]).pack()

        btn = corp_button(inner, "Abrir →", cmd, "ghost")
        btn.pack(pady=(12, 4))

        def on_enter(e, c=card, color=color):
            c.config(highlightbackground=color)
        def on_leave(e, c=card):
            c.config(highlightbackground=C["border"])

        card.bind("<Enter>", on_enter); card.bind("<Leave>", on_leave)
        for child in card.winfo_children():
            child.bind("<Enter>", on_enter); child.bind("<Leave>", on_leave)

    # Footer
    footer = tk.Frame(menu, bg=C["bg_panel"])
    footer.pack(fill="x", side="bottom")
    tk.Frame(footer, bg=C["border"], height=1).pack(fill="x")
    f_inner = tk.Frame(footer, bg=C["bg_panel"]); f_inner.pack(fill="x", padx=20, pady=10)

    tk.Label(f_inner, text="VapeHouse v2.0 — Sistema Empresarial",
             font=("Segoe UI", 8), fg=C["txt_muted"], bg=C["bg_panel"]).pack(side="left")

    corp_button(f_inner, "Cerrar Sesión",
                lambda: (menu.destroy(), root.deiconify()),
                "danger").pack(side="right")

# ==========================================
# LOGIN
# ==========================================

def login():
    l = make_window("Acceso — VapeHouse", 420, 500)
    l.grab_set()

    # Logo
    logo_frame = tk.Frame(l, bg=C["bg_dark"]); logo_frame.pack(pady=40)
    tk.Label(logo_frame, text="VAPEHOUSE", font=("Segoe UI", 28, "bold"),
             fg=C["txt_white"], bg=C["bg_dark"]).pack()
    tk.Label(logo_frame, text="S I S T E M A   E M P R E S A R I A L",
             font=("Segoe UI", 9), fg=C["txt_muted"], bg=C["bg_dark"]).pack(pady=4)

    tk.Frame(l, bg=C["accent"], height=2).pack(fill="x", padx=40)

    # Formulario
    f_form = tk.Frame(l, bg=C["bg_dark"]); f_form.pack(pady=30, padx=50, fill="x")

    tk.Label(f_form, text="Usuario", font=("Segoe UI", 9),
             fg=C["txt_muted"], bg=C["bg_dark"]).pack(anchor="w")
    u = corp_entry(f_form)
    u.pack(fill="x", ipady=10, pady=(4, 14))

    tk.Label(f_form, text="Contraseña", font=("Segoe UI", 9),
             fg=C["txt_muted"], bg=C["bg_dark"]).pack(anchor="w")
    p = corp_entry(f_form, show="•")
    p.pack(fill="x", ipady=10, pady=(4, 24))

    def auth():
        if u.get() == USUARIO_CORRECTO and p.get() == CLAVE_CORRECTA:
            l.destroy(); root.withdraw(); mostrar_menu_principal()
        else:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")

    btn_login = corp_button(f_form, "INGRESAR AL SISTEMA", auth, "primary")
    btn_login.pack(fill="x", ipady=8)
    l.bind("<Return>", lambda e: auth())

    # Footer
    tk.Label(l, text="© 2024 VapeHouse — Acceso restringido",
             font=("Segoe UI", 8), fg=C["txt_muted"], bg=C["bg_dark"]).pack(side="bottom", pady=16)

# ==========================================
# SPLASH SCREEN / INICIO
# ==========================================

iniciar_db()
apply_global_styles()

root = tk.Tk()
root.title("VapeHouse")
root.geometry("560x420")
root.configure(bg=C["bg_dark"])

# Centrar
root.update_idletasks()
x = (root.winfo_screenwidth() - 560) // 2
y = (root.winfo_screenheight() - 420) // 2
root.geometry(f"560x420+{x}+{y}")

# Pantalla de inicio
tk.Frame(root, bg=C["accent"], height=4).pack(fill="x")
main_frame = tk.Frame(root, bg=C["bg_dark"])
main_frame.pack(expand=True)

tk.Label(main_frame, text="VAPEHOUSE", font=("Segoe UI", 48, "bold"),
         fg=C["txt_white"], bg=C["bg_dark"]).pack()
tk.Label(main_frame, text="S I S T E M A   D E   G E S T I Ó N   E M P R E S A R I A L",
         font=("Segoe UI", 9), fg=C["txt_muted"], bg=C["bg_dark"]).pack(pady=6)

tk.Frame(main_frame, bg=C["border"], height=1, width=280).pack(pady=20)

corp_button(main_frame, "ENTRAR AL SISTEMA", login, "primary").pack(ipady=12, ipadx=30)

tk.Label(root, text="© 2024 VapeHouse — Todos los derechos reservados",
         font=("Segoe UI", 8), fg=C["txt_muted"], bg=C["bg_dark"]).pack(side="bottom", pady=12)

root.mainloop()
