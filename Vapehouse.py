import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from datetime import datetime, timedelta
# Librerías para PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ==========================================
# CONFIGURACIÓN Y CONEXIÓN GLOBAL
# ==========================================
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "admin"
DB_NAME = 'vapehouse_datos.db'

conn = sqlite3.connect(DB_NAME)
conn.execute("PRAGMA journal_mode=WAL") 

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

# ==========================================
# FUNCIÓN GENÉRICA PARA IMPRIMIR PDF
# ==========================================

def exportar_pdf(titulo_reporte, columnas, filas):
    if not filas:
        messagebox.showwarning("Atención", "No hay datos para exportar.")
        return

    archivo = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                           filetypes=[("PDF files", "*.pdf")],
                                           initialfile=f"Reporte_{titulo_reporte}_{datetime.now().strftime('%d_%m_%Y')}")
    if not archivo:
        return

    try:
        doc = SimpleDocTemplate(archivo, pagesize=letter)
        elementos = []
        estilos = getSampleStyleSheet()

        # Título
        elementos.append(Paragraph(f"VAPEHOUSE - REPORTE DE {titulo_reporte}", estilos['Title']))
        elementos.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos['Normal']))
        elementos.append(Spacer(1, 12))

        # Preparar datos (Encabezados + Filas)
        datos_tabla = [columnas] + [list(f) for f in filas]

        # Crear tabla PDF
        t = Table(datos_tabla)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elementos.append(t)
        doc.build(elementos)
        messagebox.showinfo("Éxito", f"PDF guardado correctamente en:\n{archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")

# ==========================================
# LÓGICA DE NEGOCIO
# ==========================================

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
    for fila in cursor.fetchall():
        tag = 'alerta' if fila[5] <= 3 else 'normal'
        tabla.insert('', tk.END, values=fila, tags=(tag,))

# ==========================================
# VENTANA: GASTO / GANANCIA
# ==========================================

def abrir_analisis():
    v_an = tk.Toplevel()
    v_an.title("Gasto / Ganancia")
    v_an.geometry("850x950") 
    v_an.configure(bg="#121212")
    v_an.grab_set()

    tk.Label(v_an, text="GASTO / GANANCIA", font=("Arial", 24, "bold"), fg="#bb86fc", bg="#121212").pack(pady=10)

    # --- Sección Registro ---
    f_gasto = tk.LabelFrame(v_an, text=" Registrar Gasto / Inversión ", bg="#1a1a1a", fg="#bb86fc", padx=15, pady=15)
    f_gasto.pack(pady=10, padx=20, fill="x")

    tk.Label(f_gasto, text="Concepto:", fg="white", bg="#1a1a1a").grid(row=0, column=0, sticky="w")
    ent_con = tk.Entry(f_gasto, font=("Arial", 11)); ent_con.grid(row=0, column=1, padx=10, pady=5)
    tk.Label(f_gasto, text="Monto $:", fg="white", bg="#1a1a1a").grid(row=1, column=0, sticky="w")
    ent_mon = tk.Entry(f_gasto, font=("Arial", 11)); ent_mon.grid(row=1, column=1, padx=10, pady=5)

    def guardar_gasto():
        try:
            con, mon = ent_con.get().strip(), float(ent_mon.get())
            if not con: raise ValueError
            conn.execute("INSERT INTO gastos (fecha, concepto, monto) VALUES (?,?,?)", 
                         (datetime.now().strftime("%d/%m/%Y"), con, mon))
            conn.commit()
            messagebox.showinfo("Éxito", "Gasto registrado")
            ent_con.delete(0, tk.END); ent_mon.delete(0, tk.END)
            actualizar_resumen("HOY")
        except: messagebox.showerror("Error", "Datos de gasto inválidos")

    tk.Button(f_gasto, text="REGISTRAR GASTO", bg="#bb86fc", font=("Arial", 9, "bold"), command=guardar_gasto).grid(row=2, column=1, pady=10)

    # --- Sección Totales ---
    f_res = tk.Frame(v_an, bg="#121212")
    f_res.pack(pady=10, padx=20, fill="x")
    
    lbl_v = tk.Label(f_res, text="Ganancia Bruta: $0", font=("Arial", 12), fg="#3498db", bg="#121212")
    lbl_v.pack()
    lbl_g = tk.Label(f_res, text="Gastos/Inversión: $0", font=("Arial", 12), fg="#e74c3c", bg="#121212")
    lbl_g.pack()
    lbl_u = tk.Label(f_res, text="UTILIDAD REAL: $0", font=("Arial", 18, "bold"), fg="#00FF7F", bg="#121212")
    lbl_u.pack(pady=5)

    tk.Label(v_an, text="Detalle de Gastos en el periodo:", fg="#bb86fc", bg="#121212", font=("Arial", 10, "italic")).pack()
    cols = ("ID", "FECHA", "CONCEPTO", "MONTO")
    tabla_gastos = ttk.Treeview(v_an, columns=cols, show="headings", height=8)
    for c in cols: 
        tabla_gastos.heading(c, text=c)
        tabla_gastos.column(c, width=150, anchor="center")
    tabla_gastos.pack(pady=10, padx=20, fill="x")

    datos_actuales_pdf = {"modo": "HOY", "filas": [], "v": 0, "g": 0}

    def actualizar_resumen(modo, resetear=False):
        cursor = conn.cursor()
        hoy = datetime.now()
        tabla_gastos.delete(*tabla_gastos.get_children())
        datos_actuales_pdf["modo"] = modo
        
        if modo == "HOY":
            f_v, f_g = f"{hoy.strftime('%d/%m/%Y')}%", hoy.strftime('%d/%m/%Y')
            q_v, q_g_sum, q_g_all, q_reset = "SELECT SUM(ganancia) FROM ventas WHERE fecha LIKE ?", "SELECT SUM(monto) FROM gastos WHERE fecha = ?", "SELECT * FROM gastos WHERE fecha = ?", "DELETE FROM gastos WHERE fecha = ?"
            params_v, params_g = (f_v,), (f_g,)
        elif modo == "SEMANAL":
            h_s = (hoy - timedelta(days=7)).strftime('%Y%m%d')
            cond = "(substr(fecha,7,4)||substr(fecha,4,2)||substr(fecha,1,2)) >= ?"
            q_v, q_g_sum, q_g_all, q_reset = f"SELECT SUM(ganancia) FROM ventas WHERE {cond}", f"SELECT SUM(monto) FROM gastos WHERE {cond}", f"SELECT * FROM gastos WHERE {cond}", f"DELETE FROM gastos WHERE {cond}"
            params_v, params_g = (h_s,), (h_s,)
        elif modo == "MENSUAL":
            f_mes = f"%/{hoy.strftime('%m/%Y')}%"
            q_v, q_g_sum, q_g_all, q_reset = "SELECT SUM(ganancia) FROM ventas WHERE fecha LIKE ?", "SELECT SUM(monto) FROM gastos WHERE fecha LIKE ?", "SELECT * FROM gastos WHERE LIKE ?", "DELETE FROM gastos WHERE fecha LIKE ?"
            params_v, params_g = (f_mes,), (f_mes,)
        elif modo == "ANUAL":
            f_anio = f"%/%/{hoy.strftime('%Y')}%"
            q_v, q_g_sum, q_g_all, q_reset = "SELECT SUM(ganancia) FROM ventas WHERE fecha LIKE ?", "SELECT SUM(monto) FROM gastos WHERE fecha LIKE ?", "SELECT * FROM gastos WHERE LIKE ?", "DELETE FROM gastos WHERE fecha LIKE ?"
            params_v, params_g = (f_anio,), (f_anio,)
        else: # TOTAL
            q_v, q_g_sum, q_g_all, q_reset = "SELECT SUM(ganancia) FROM ventas", "SELECT SUM(monto) FROM gastos", "SELECT * FROM gastos", "DELETE FROM gastos"
            params_v, params_g = (), ()

        if resetear:
            if messagebox.askyesno("Resetear", f"¿Limpiar gastos de {modo}?"):
                conn.execute(q_reset, params_g); conn.commit()

        cursor.execute(q_v, params_v); v = cursor.fetchone()[0] or 0
        cursor.execute(q_g_sum, params_g); g = cursor.fetchone()[0] or 0
        cursor.execute(q_g_all, params_g); filas = cursor.fetchall()
        
        datos_actuales_pdf["filas"] = filas
        datos_actuales_pdf["v"] = v
        datos_actuales_pdf["g"] = g
        
        for fila in filas: tabla_gastos.insert('', tk.END, values=fila)
        
        lbl_v.config(text=f"Ganancia Bruta ({modo}): ${v:,.2f}")
        lbl_g.config(text=f"Gastos ({modo}): ${g:,.2f}")
        lbl_u.config(text=f"UTILIDAD REAL: ${v-g:,.2f}")

    def imprimir_balance_pdf():
        d = datos_actuales_pdf
        archivo = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                               filetypes=[("PDF files", "*.pdf")],
                                               initialfile=f"Balance_{d['modo']}_{datetime.now().strftime('%d_%m_%Y')}")
        if not archivo: return

        try:
            doc = SimpleDocTemplate(archivo, pagesize=letter)
            elementos = []; estilos = getSampleStyleSheet()
            elementos.append(Paragraph(f"VAPEHOUSE - BALANCE ({d['modo']})", estilos['Title']))
            elementos.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos['Normal']))
            elementos.append(Spacer(1, 20))

            resumen = [
                [f"GANANCIA BRUTA (Ventas):", f"${d['v']:,.2f}"],
                [f"GASTOS / INVERSIÓN:", f"${d['g']:,.2f}"],
                [f"UTILIDAD NETA REAL:", f"${d['v']-d['g']:,.2f}"]
            ]
            rt = Table(resumen, colWidths=[200, 100])
            rt.setStyle(TableStyle([
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('SIZE', (0, 2), (-1, 2), 14),
                ('TEXTCOLOR', (0, 2), (1, 2), colors.green),
                ('ALIGN', (1, 0), (1, 2), 'RIGHT'),
            ]))
            elementos.append(rt)
            elementos.append(Spacer(1, 20))
            elementos.append(Paragraph("DETALLE DE GASTOS:", estilos['Heading3']))

            if d['filas']:
                datos_tabla = [cols] + [list(f) for f in d['filas']]
                t = Table(datos_tabla)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.blueviolet),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elementos.append(t)
            
            doc.build(elementos)
            messagebox.showinfo("Éxito", "Balance PDF generado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")

    f_btns = tk.Frame(v_an, bg="#121212")
    f_btns.pack(pady=10)
    for m in ["HOY", "SEMANAL", "MENSUAL", "ANUAL", "TOTAL"]:
        col = tk.Frame(f_btns, bg="#121212")
        col.pack(side="left", padx=5)
        tk.Button(col, text=m, width=10, command=lambda modo=m: actualizar_resumen(modo)).pack()
        tk.Button(col, text="RESET", width=10, bg="#e74c3c", fg="white", font=("Arial", 7, "bold"), command=lambda modo=m: actualizar_resumen(modo, True)).pack(pady=2)

    tk.Button(v_an, text="📄 IMPRIMIR BALANCE COMPLETO PDF", bg="#bb86fc", fg="black", font=("Arial", 10, "bold"), width=35, 
              command=imprimir_balance_pdf).pack(pady=5)

    actualizar_resumen("HOY")
    tk.Button(v_an, text="VOLVER", bg="#444", fg="white", width=20, command=v_an.destroy).pack(pady=20)

# ==========================================
# VENTANA: CONTABILIDAD
# ==========================================

def abrir_contabilidad():
    v_cont = tk.Toplevel(); v_cont.title("Contabilidad"); v_cont.geometry("1000x850"); v_cont.configure(bg="#121212"); v_cont.grab_set()
    tk.Label(v_cont, text="REPORTES DE VENTAS", font=("Arial", 28, "bold"), fg="#3498db", bg="#121212").pack(pady=20)
    nb = ttk.Notebook(v_cont); nb.pack(pady=10, padx=20, fill="both", expand=True)

    def filtrar_y_obtener(modo):
        cursor = conn.cursor(); hoy = datetime.now()
        if modo == "HOY": cursor.execute("SELECT * FROM ventas WHERE fecha LIKE ?", (f"{hoy.strftime('%d/%m/%Y')}%",))
        elif modo == "SEMANAL":
            h_s = (hoy - timedelta(days=7)).strftime('%Y%m%d')
            cursor.execute("SELECT * FROM ventas WHERE (substr(fecha,7,4)||substr(fecha,4,2)||substr(fecha,1,2)) >= ?", (h_s,))
        elif modo == "MES ACTUAL": cursor.execute("SELECT * FROM ventas WHERE fecha LIKE ?", (f"%/{(hoy.strftime('%m/%Y'))}%",))
        elif modo == "AÑO ACTUAL": cursor.execute("SELECT * FROM ventas WHERE fecha LIKE ?", (f"%/%/{hoy.strftime('%Y')}%",))
        else: cursor.execute("SELECT * FROM ventas")
        return cursor.fetchall()

    def crear_pestana(nombre, modo_filtro):
        frame = tk.Frame(nb, bg="#1a1a1a"); nb.add(frame, text=f"  {nombre}  ")
        cols = ("ID", "FECHA/HORA", "PRODUCTO", "UNDS", "GANANCIA")
        tabla = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        for c in cols: tabla.heading(c, text=c); tabla.column(c, width=150, anchor="center")
        tabla.pack(pady=15, padx=15, fill="both", expand=True)
        lbl_sum = tk.Label(frame, text="Total: $0.00", font=("Arial", 22, "bold"), fg="#00FF7F", bg="#1a1a1a"); lbl_sum.pack(pady=5)
        
        def refresh():
            tabla.delete(*tabla.get_children())
            filas = filtrar_y_obtener(modo_filtro); total = 0
            for f in filas: tabla.insert('', tk.END, values=f); total += f[4]
            lbl_sum.config(text=f"Total {nombre}: ${total:,.2f}")
            return filas

        f_btns_c = tk.Frame(frame, bg="#1a1a1a")
        f_btns_c.pack(pady=10)

        tk.Button(f_btns_c, text="📄 IMPRIMIR PDF", bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=15,
                  command=lambda: exportar_pdf(f"VENTAS_{modo_filtro}", cols, filtrar_y_obtener(modo_filtro))).pack(side="left", padx=10)
        
        tk.Button(f_btns_c, text="RESETEAR VENTAS", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=15,
                  command=lambda: [conn.execute("DELETE FROM ventas" if modo_filtro=="REPORTE GENERAL" else "DELETE FROM ventas WHERE fecha LIKE ?", (f"{datetime.now().strftime('%d/%m/%Y')}%",) if modo_filtro=="HOY" else ""), conn.commit(), refresh()]).pack(side="left", padx=10)
        
        refresh()

    crear_pestana("HOY", "HOY"); crear_pestana("SEMANAL", "SEMANAL"); crear_pestana("MES ACTUAL", "MES ACTUAL")
    crear_pestana("AÑO ACTUAL", "AÑO ACTUAL"); crear_pestana("REPORTE GENERAL", "REPORTE GENERAL")
    tk.Button(v_cont, text="VOLVER", bg="#444", fg="white", font=("Arial", 12, "bold"), width=20, command=v_cont.destroy).pack(pady=20)

# ==========================================
# VENTANA: HISTORIAL (CON BOTÓN RESET)
# ==========================================

def abrir_historial():
    v = tk.Toplevel(); v.title("Historial"); v.geometry("950x700"); v.configure(bg="#1a1a1a"); v.grab_set()
    tk.Label(v, text="REGISTRO DE MOVIMIENTOS", font=("Arial", 22, "bold"), fg="#FFD700", bg="#1a1a1a").pack(pady=20)
    cols = ("FECHA", "PRODUCTO", "TIPO", "CANT", "DETALLE")
    tabla_h = ttk.Treeview(v, columns=cols, show="headings", height=18)
    for col in cols: tabla_h.heading(col, text=col); tabla_h.column(col, width=160, anchor="center")
    tabla_h.tag_configure('VENTA', foreground="#2ecc71"); tabla_h.tag_configure('ENTRADA', foreground="#3498db")
    tabla_h.tag_configure('INGRESO', foreground="#bb86fc"); tabla_h.tag_configure('ELIMINACION', foreground="#e74c3c")
    tabla_h.pack(pady=10, padx=30, fill="both", expand=True)

    def cargar_historial():
        tabla_h.delete(*tabla_h.get_children())
        cursor = conn.cursor(); cursor.execute("SELECT fecha, producto, tipo_mov, cantidad_mov, detalle FROM historial ORDER BY id_mov DESC")
        for f in cursor.fetchall(): 
            tipo = f[2]; t_tag = 'VENTA' if 'VENTA' in tipo else 'INGRESO' if 'INGRESO' in tipo else 'ENTRADA' if 'ENTRADA' in tipo else 'ELIMINACION' if 'ELIMINACION' in tipo.upper() else 'normal'
            tabla_h.insert('', tk.END, values=f, tags=(t_tag,))

    def reset_historial():
        if messagebox.askyesno("Confirmar", "¿Desea limpiar todo el historial de movimientos?"):
            conn.execute("DELETE FROM historial"); conn.commit()
            cargar_historial()

    f_btns = tk.Frame(v, bg="#1a1a1a")
    f_btns.pack(pady=10)
    tk.Button(f_btns, text="LIMPIAR HISTORIAL", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=20, command=reset_historial).pack(side="left", padx=10)
    tk.Button(f_btns, text="← VOLVER", bg="#444", fg="white", font=("Arial", 10, "bold"), width=15, command=v.destroy).pack(side="left", padx=10)
    
    cargar_historial()

# ==========================================
# VENTANA: FACTURAS GENERADAS (NUEVO)
# ==========================================

def abrir_facturas():
    v = tk.Toplevel(); v.title("Facturas Generadas"); v.geometry("900x700"); v.configure(bg="#1a1a1a"); v.grab_set()
    tk.Label(v, text="CONTROL DE FACTURAS", font=("Arial", 22, "bold"), fg="#3498db", bg="#1a1a1a").pack(pady=20)
    
    cols = ("ID", "FECHA", "PRODUCTO", "UNDS", "TOTAL VENTA")
    tabla_f = ttk.Treeview(v, columns=cols, show="headings", height=15)
    for col in cols: tabla_f.heading(col, text=col); tabla_f.column(col, width=150, anchor="center")
    tabla_f.pack(pady=10, padx=30, fill="both", expand=True)

    def cargar_f():
        tabla_f.delete(*tabla_f.get_children())
        cursor = conn.cursor()
        cursor.execute("SELECT id_venta, fecha, producto, unidades, (ganancia) FROM ventas ORDER BY id_venta DESC")
        for f in cursor.fetchall(): tabla_f.insert('', tk.END, values=f)

    def reset_f():
        if messagebox.askyesno("Reset", "¿Eliminar todas las facturas registradas?"):
            conn.execute("DELETE FROM ventas"); conn.commit(); cargar_f()

    def imprimir_f():
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ventas")
        exportar_pdf("FACTURAS", cols, cursor.fetchall())

    f_btns = tk.Frame(v, bg="#1a1a1a")
    f_btns.pack(pady=20)
    tk.Button(f_btns, text="📄 EXPORTAR PDF", bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=15, command=imprimir_f).pack(side="left", padx=10)
    tk.Button(f_btns, text="RESET FACTURAS", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=15, command=reset_f).pack(side="left", padx=10)
    tk.Button(f_btns, text="VOLVER", bg="#555", fg="white", font=("Arial", 10, "bold"), width=15, command=v.destroy).pack(side="left", padx=10)
    
    cargar_f()

# ==========================================
# FUNCIÓN: GENERAR FACTURA PDF CON DATOS CLIENTE
# ==========================================

def generar_factura_cliente(datos_cliente, producto, cantidad, precio_unit, total_venta, id_venta):
    """Genera una factura PDF con los datos del cliente y la venta."""
    archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=f"Factura_{id_venta}_{datos_cliente['cedula']}_{datetime.now().strftime('%d_%m_%Y')}"
    )
    if not archivo:
        return

    try:
        doc = SimpleDocTemplate(archivo, pagesize=letter,
                                topMargin=40, bottomMargin=40, leftMargin=50, rightMargin=50)
        elementos = []
        estilos = getSampleStyleSheet()

        # Encabezado
        elementos.append(Paragraph("VAPEHOUSE", estilos['Title']))
        elementos.append(Paragraph("FACTURA DE VENTA", estilos['Heading2']))
        elementos.append(Spacer(1, 6))
        elementos.append(Paragraph(f"No. Factura: <b>{id_venta:05d}</b>  |  Fecha: <b>{datetime.now().strftime('%d/%m/%Y %H:%M')}</b>", estilos['Normal']))
        elementos.append(Spacer(1, 16))

        # Datos del cliente
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
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.whitesmoke, colors.white]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_cli)
        elementos.append(Spacer(1, 16))

        # Detalle del producto
        elementos.append(Paragraph("DETALLE DE LA VENTA", estilos['Heading3']))
        encabezado_prod = [["PRODUCTO", "CANT.", "PRECIO UNIT.", "TOTAL"]]
        fila_prod = [[producto, str(cantidad), f"${precio_unit:,.2f}", f"${total_venta:,.2f}"]]
        t_prod = Table(encabezado_prod + fila_prod, colWidths=[220, 70, 110, 110])
        t_prod.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_prod)
        elementos.append(Spacer(1, 12))

        # Total destacado
        t_total = Table([["TOTAL A PAGAR:", f"${total_venta:,.2f}"]], colWidths=[300, 210])
        t_total.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#27ae60')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_total)
        elementos.append(Spacer(1, 30))
        elementos.append(Paragraph("¡Gracias por su compra! - VAPEHOUSE", estilos['Normal']))

        doc.build(elementos)
        messagebox.showinfo("Factura generada", f"Factura PDF guardada correctamente:\n{archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la factura PDF: {e}")


# ==========================================
# VENTANA: FORMULARIO DATOS CLIENTE PARA VENTA
# ==========================================

def formulario_datos_cliente(parent, producto_nombre, cantidad, precio_unit, total_venta, callback_confirmar):
    """Abre ventana para ingresar datos del cliente antes de confirmar la venta."""
    v_cli = tk.Toplevel(parent)
    v_cli.title("Datos del Cliente")
    v_cli.geometry("420x480")
    v_cli.configure(bg="#1a1a1a")
    v_cli.grab_set()

    tk.Label(v_cli, text="DATOS DEL CLIENTE", font=("Arial", 16, "bold"), fg="#00FF7F", bg="#1a1a1a").pack(pady=15)
    tk.Label(v_cli, text=f"Producto: {producto_nombre}  |  Cant: {cantidad}  |  Total: ${total_venta:,.2f}",
             font=("Arial", 9), fg="#aaaaaa", bg="#1a1a1a").pack(pady=2)

    f_form = tk.Frame(v_cli, bg="#1a1a1a")
    f_form.pack(pady=15, padx=30, fill="x")

    campos = [("Nombre:", "nombre"), ("Apellido:", "apellido"), ("Cédula / ID:", "cedula"),
              ("Teléfono:", "telefono"), ("Correo:", "correo")]
    entradas = {}
    for i, (label_txt, key) in enumerate(campos):
        tk.Label(f_form, text=label_txt, fg="white", bg="#1a1a1a", font=("Arial", 10), anchor="w").grid(row=i, column=0, sticky="w", pady=6)
        ent = tk.Entry(f_form, font=("Arial", 11), bg="#333", fg="white", insertbackground="white", width=22)
        ent.grid(row=i, column=1, padx=10, pady=6)
        entradas[key] = ent

    def confirmar():
        datos = {k: v.get().strip() for k, v in entradas.items()}
        if not datos['nombre'] or not datos['apellido'] or not datos['cedula']:
            messagebox.showerror("Error", "Nombre, apellido y cédula son obligatorios.", parent=v_cli)
            return
        v_cli.destroy()
        callback_confirmar(datos)

    def cancelar():
        v_cli.destroy()

    f_bts = tk.Frame(v_cli, bg="#1a1a1a")
    f_bts.pack(pady=15)
    tk.Button(f_bts, text="✅ CONFIRMAR VENTA", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"),
              width=18, command=confirmar).pack(side="left", padx=8)
    tk.Button(f_bts, text="✖ CANCELAR", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
              width=12, command=cancelar).pack(side="left", padx=8)


# ==========================================
# VENTANA: INVENTARIO
# ==========================================

def abrir_inventario():
    v_inv = tk.Toplevel(); v_inv.title("Inventario"); v_inv.geometry("950x900"); v_inv.configure(bg="#1a1a1a"); v_inv.grab_set()
    tk.Label(v_inv, text="GESTIÓN DE STOCK", font=("Arial", 22, "bold"), fg="#00FF7F", bg="#1a1a1a").pack(pady=10)
    
    f_b = tk.Frame(v_inv, bg="#1a1a1a"); f_b.pack(pady=5, padx=20, fill="x")
    tk.Label(f_b, text="🔍 BUSCAR:", fg="white", bg="#1a1a1a").pack(side="left", padx=5)
    sv = tk.StringVar(); ent_b = tk.Entry(f_b, textvariable=sv, bg="#333", fg="white", font=("Arial", 12)); ent_b.pack(side="left", fill="x", expand=True)
    sv.trace_add("write", lambda *args: actualizar_tabla_inv(tabla_inv, sv.get()))
    
    f_datos = tk.LabelFrame(v_inv, text=" Datos del Producto ", bg="#1a1a1a", fg="#00FF7F", padx=10, pady=10); f_datos.pack(pady=10, padx=20, fill="x")
    cb_cat = ttk.Combobox(f_datos, values=["Vapers", "Esencias", "Destilados", "Relojes", "Perfumes", "Gorras", "Camisetas"], state="readonly")
    cb_cat.grid(row=0, column=1, padx=5, pady=5); ent_n = tk.Entry(f_datos); ent_n.grid(row=0, column=3, padx=5, pady=5)
    ent_c = tk.Entry(f_datos); ent_c.grid(row=1, column=1, padx=5, pady=5); ent_v = tk.Entry(f_datos); ent_v.grid(row=1, column=3, padx=5, pady=5)
    ent_s = tk.Entry(f_datos); ent_s.grid(row=2, column=1, padx=5, pady=5)
    labels = [("Categoría:",0,0), ("Nombre:",0,2), ("Costo $:",1,0), ("Venta $:",1,2), ("Stock:",2,0)]
    for text, r, c in labels: tk.Label(f_datos, text=text, bg="#1a1a1a", fg="white").grid(row=r, column=c, sticky="e")
    
    def guardar():
        try:
            cat, nom, c, v, s = cb_cat.get(), ent_n.get().strip(), float(ent_c.get()), float(ent_v.get()), int(ent_s.get())
            cursor = conn.cursor(); cursor.execute("SELECT id FROM productos WHERE LOWER(nombre) = LOWER(?)", (nom,))
            ex = cursor.fetchone()
            if ex:
                if messagebox.askyesno("Producto Existente", f"¿Sumar {s} unidades a {nom}?"):
                    conn.execute("UPDATE productos SET categoria=?, costo=?, venta=?, cantidad=cantidad+? WHERE id=?", (cat, c, v, s, ex[0]))
                    registrar_movimiento(nom, "ENTRADA", s, f"Reposición. Stock total: {s}")
            else:
                conn.execute("INSERT INTO productos (categoria, nombre, costo, venta, cantidad) VALUES (?,?,?,?,?)", (cat, nom, c, v, s))
                registrar_movimiento(nom, "INGRESO", s, "Nuevo producto en sistema")
            conn.commit(); actualizar_tabla_inv(tabla_inv)
            for e in [ent_n, ent_c, ent_v, ent_s]: e.delete(0, tk.END)
        except: messagebox.showerror("Error", "Datos numéricos inválidos")
    
    tk.Button(f_datos, text="GUARDAR", bg="#00FF7F", font=("Arial", 10, "bold"), width=12, command=guardar).grid(row=2, column=2, columnspan=2, pady=10)
    
    cols = ("ID", "CATEGORÍA", "NOMBRE", "COSTO", "VENTA", "STOCK")
    tabla_inv = ttk.Treeview(v_inv, columns=cols, show="headings")
    for col in cols: tabla_inv.heading(col, text=col); tabla_inv.column(col, width=100, anchor="center")
    tabla_inv.tag_configure('alerta', foreground="#ff4d4d", font=("Arial", 10, "bold")); tabla_inv.pack(pady=10, padx=20, fill="both", expand=True)
    
    btns = tk.Frame(v_inv, bg="#1a1a1a"); btns.pack(pady=10)
    
    def vender_local():
        sel = tabla_inv.selection()
        if not sel: return
        cant = simpledialog.askinteger("Venta", "¿Cuántas unidades?", minvalue=1)
        if not cant: return

        for item in sel:
            d = tabla_inv.item(item)['values']
            if int(d[5]) >= cant:
                precio_unit = float(d[4])
                total_venta = precio_unit * cant
                gan = (precio_unit - float(d[3])) * cant
                prod_nombre = d[2]
                prod_id = d[0]

                def procesar_venta(datos_cliente, _cant=cant, _gan=gan, _prod_nombre=prod_nombre,
                                   _prod_id=prod_id, _precio_unit=precio_unit, _total_venta=total_venta):
                    conn.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id = ?", (_cant, _prod_id))
                    conn.execute("INSERT INTO ventas (fecha, producto, unidades, ganancia) VALUES (?,?,?,?)",
                                 (datetime.now().strftime("%d/%m/%Y %H:%M"), _prod_nombre, _cant, _gan))
                    id_venta = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                    registrar_movimiento(_prod_nombre, "VENTA", _cant, f"Venta Realizada")
                    conn.commit()
                    actualizar_tabla_inv(tabla_inv)
                    generar_factura_cliente(datos_cliente, _prod_nombre, _cant, _precio_unit, _total_venta, id_venta)

                formulario_datos_cliente(v_inv, prod_nombre, cant, precio_unit, total_venta, procesar_venta)
            else:
                messagebox.showwarning("Stock insuficiente", f"No hay suficiente stock de {d[2]}.")

    def eliminar_local():
        sel = tabla_inv.selection()
        if not sel or not messagebox.askyesno("Eliminar", "¿Borrar seleccionados?"): return
        for item in sel:
            d = tabla_inv.item(item)['values']; conn.execute("DELETE FROM productos WHERE id = ?", (d[0],))
            registrar_movimiento(d[2], "ELIMINACIÓN", 0, "Producto borrado")
        conn.commit(); actualizar_tabla_inv(tabla_inv)

    tk.Button(btns, text="💰 VENDER", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), width=15, height=2, command=vender_local).pack(side="left", padx=5)
    tk.Button(btns, text="📜 HISTORIAL", bg="#FFD700", font=("Arial", 10, "bold"), width=15, height=2, command=abrir_historial).pack(side="left", padx=5)
    tk.Button(btns, text="📄 FACTURAS", bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=15, height=2, command=abrir_facturas).pack(side="left", padx=5)
    tk.Button(btns, text="🗑 ELIMINAR", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=15, height=2, command=eliminar_local).pack(side="left", padx=5)
    tk.Button(btns, text="← VOLVER", bg="#555", fg="white", font=("Arial", 10, "bold"), width=15, height=2, command=v_inv.destroy).pack(side="left", padx=5)
    
    actualizar_tabla_inv(tabla_inv)

# ==========================================
# VENTANA: ANÁLISIS BI (INTELIGENCIA DE NEGOCIOS)
# ==========================================

def abrir_analisis_bi():
    v_bi = tk.Toplevel()
    v_bi.title("Análisis BI - Inteligencia de Negocios")
    v_bi.geometry("1100x850")
    v_bi.configure(bg="#0d0d0d")
    v_bi.grab_set()

    tk.Label(v_bi, text="📊 INTELIGENCIA DE NEGOCIOS", font=("Arial", 22, "bold"), fg="#00e5ff", bg="#0d0d0d").pack(pady=10)

    nb_bi = ttk.Notebook(v_bi)
    nb_bi.pack(pady=5, padx=15, fill="both", expand=True)

    # ── Estilos de tabla compartidos ──
    style = ttk.Style()
    style.configure("BI.Treeview", background="#1a1a1a", fieldbackground="#1a1a1a",
                    foreground="white", rowheight=24, font=("Arial", 9))
    style.configure("BI.Treeview.Heading", background="#003344", foreground="#00e5ff",
                    font=("Arial", 9, "bold"))

    def make_treeview(parent, cols, widths, height=12):
        frame = tk.Frame(parent, bg="#1a1a1a")
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        sb = ttk.Scrollbar(frame, orient="vertical")
        t = ttk.Treeview(frame, columns=cols, show="headings", height=height,
                         style="BI.Treeview", yscrollcommand=sb.set)
        sb.config(command=t.yview)
        for col, w in zip(cols, widths):
            t.heading(col, text=col)
            t.column(col, width=w, anchor="center")
        t.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return t

    # ══════════════════════════════════════
    # PESTAÑA 1: RENDIMIENTO DE VENTAS
    # ══════════════════════════════════════
    tab1 = tk.Frame(nb_bi, bg="#0d0d0d")
    nb_bi.add(tab1, text="  📈 Rendimiento de Ventas  ")

    tk.Label(tab1, text="Ventas por Periodo", font=("Arial", 13, "bold"), fg="#00e5ff", bg="#0d0d0d").pack(pady=8)

    f_kpi = tk.Frame(tab1, bg="#0d0d0d")
    f_kpi.pack(fill="x", padx=15, pady=5)

    kpi_vars = {}
    kpi_defs = [
        ("HOY", "#2ecc71"), ("ESTE MES", "#3498db"), ("ESTE AÑO", "#9b59b6"), ("TOTAL", "#e67e22")
    ]
    for titulo, color in kpi_defs:
        box = tk.Frame(f_kpi, bg=color, padx=12, pady=10, relief="ridge", bd=2)
        box.pack(side="left", expand=True, fill="x", padx=6)
        tk.Label(box, text=titulo, font=("Arial", 8, "bold"), fg="white", bg=color).pack()
        lbl = tk.Label(box, text="$0.00", font=("Arial", 15, "bold"), fg="white", bg=color)
        lbl.pack()
        lbl_u = tk.Label(box, text="0 ventas", font=("Arial", 8), fg="white", bg=color)
        lbl_u.pack()
        kpi_vars[titulo] = (lbl, lbl_u)

    # Tabla detalle diario (últimos 30 días)
    tk.Label(tab1, text="Detalle diario — últimos 30 días", font=("Arial", 10, "italic"), fg="#aaaaaa", bg="#0d0d0d").pack()
    cols_r = ("FECHA", "# VENTAS", "UNIDADES", "GANANCIA TOTAL", "TICKET PROMEDIO")
    t_rend = make_treeview(tab1, cols_r, [130, 90, 90, 140, 140], height=10)
    t_rend.tag_configure('par', background="#1a1a2a")
    t_rend.tag_configure('impar', background="#0d0d1a")

    def cargar_rendimiento():
        cursor = conn.cursor()
        hoy = datetime.now()

        # KPIs
        periodos = {
            "HOY": f"WHERE fecha LIKE '{hoy.strftime('%d/%m/%Y')}%'",
            "ESTE MES": f"WHERE fecha LIKE '%/{hoy.strftime('%m/%Y')}%'",
            "ESTE AÑO": f"WHERE fecha LIKE '%/%/{hoy.strftime('%Y')}%'",
            "TOTAL": ""
        }
        for titulo, cond in periodos.items():
            cursor.execute(f"SELECT SUM(ganancia), COUNT(*) FROM ventas {cond}")
            row = cursor.fetchone()
            gan = row[0] or 0
            cnt = row[1] or 0
            kpi_vars[titulo][0].config(text=f"${gan:,.2f}")
            kpi_vars[titulo][1].config(text=f"{cnt} venta{'s' if cnt != 1 else ''}")

        # Detalle diario últimos 30 días
        t_rend.delete(*t_rend.get_children())
        for i in range(29, -1, -1):
            dia = (hoy - timedelta(days=i)).strftime('%d/%m/%Y')
            cursor.execute("SELECT COUNT(*), SUM(unidades), SUM(ganancia) FROM ventas WHERE fecha LIKE ?", (f"{dia}%",))
            r = cursor.fetchone()
            cnt_v, unds, gan = r[0] or 0, r[1] or 0, r[2] or 0
            ticket = (gan / cnt_v) if cnt_v > 0 else 0
            tag = 'par' if i % 2 == 0 else 'impar'
            t_rend.insert('', tk.END, values=(dia, cnt_v, unds, f"${gan:,.2f}", f"${ticket:,.2f}"), tags=(tag,))

    tk.Button(tab1, text="🔄 ACTUALIZAR", bg="#00e5ff", fg="#0d0d0d", font=("Arial", 9, "bold"),
              command=cargar_rendimiento).pack(pady=6)

    # ══════════════════════════════════════
    # PESTAÑA 2: PRODUCTOS ESTRELLA
    # ══════════════════════════════════════
    tab2 = tk.Frame(nb_bi, bg="#0d0d0d")
    nb_bi.add(tab2, text="  ⭐ Productos Estrella  ")

    tk.Label(tab2, text="Ranking de Productos por Rendimiento", font=("Arial", 13, "bold"), fg="#00e5ff", bg="#0d0d0d").pack(pady=8)

    f_filtro = tk.Frame(tab2, bg="#0d0d0d")
    f_filtro.pack(pady=4)
    tk.Label(f_filtro, text="Periodo:", fg="white", bg="#0d0d0d", font=("Arial", 10)).pack(side="left", padx=5)
    cb_periodo = ttk.Combobox(f_filtro, values=["HOY", "ESTE MES", "ESTE AÑO", "TOTAL"], state="readonly", width=12)
    cb_periodo.set("ESTE MES"); cb_periodo.pack(side="left", padx=5)

    cols_e = ("RANK", "PRODUCTO", "UNIDADES VENDIDAS", "GANANCIA TOTAL", "# TRANSACCIONES", "MARGEN PROM. %")
    t_estrella = make_treeview(tab2, cols_e, [55, 200, 130, 130, 130, 120], height=14)
    t_estrella.tag_configure('oro', foreground="#FFD700", font=("Arial", 9, "bold"))
    t_estrella.tag_configure('plata', foreground="#C0C0C0")
    t_estrella.tag_configure('bronce', foreground="#cd7f32")
    t_estrella.tag_configure('normal', foreground="white")

    def cargar_estrella():
        t_estrella.delete(*t_estrella.get_children())
        cursor = conn.cursor()
        hoy = datetime.now()
        periodo = cb_periodo.get()
        cond = {
            "HOY": f"WHERE v.fecha LIKE '{hoy.strftime('%d/%m/%Y')}%'",
            "ESTE MES": f"WHERE v.fecha LIKE '%/{hoy.strftime('%m/%Y')}%'",
            "ESTE AÑO": f"WHERE v.fecha LIKE '%/%/{hoy.strftime('%Y')}%'",
            "TOTAL": ""
        }.get(periodo, "")

        cursor.execute(f"""
            SELECT v.producto,
                   SUM(v.unidades) as total_unds,
                   SUM(v.ganancia) as total_gan,
                   COUNT(*) as num_trans,
                   p.costo, p.venta
            FROM ventas v
            LEFT JOIN productos p ON LOWER(v.producto) = LOWER(p.nombre)
            {cond}
            GROUP BY v.producto
            ORDER BY total_unds DESC
        """)
        filas = cursor.fetchall()
        for i, f in enumerate(filas, 1):
            prod, unds, gan, trans, costo, venta = f
            if venta and costo and venta > 0:
                margen = ((venta - costo) / venta) * 100
            else:
                margen = 0
            tag = 'oro' if i == 1 else 'plata' if i == 2 else 'bronce' if i == 3 else 'normal'
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else str(i)
            t_estrella.insert('', tk.END,
                              values=(medal, prod, unds or 0, f"${gan or 0:,.2f}", trans, f"{margen:.1f}%"),
                              tags=(tag,))

    tk.Button(tab2, text="🔄 ACTUALIZAR RANKING", bg="#FFD700", fg="#0d0d0d", font=("Arial", 9, "bold"),
              command=cargar_estrella).pack(pady=6)
    cb_periodo.bind("<<ComboboxSelected>>", lambda e: cargar_estrella())

    # ══════════════════════════════════════
    # PESTAÑA 3: RECOMENDACIONES BI
    # ══════════════════════════════════════
    tab3 = tk.Frame(nb_bi, bg="#0d0d0d")
    nb_bi.add(tab3, text="  🤖 Recomendaciones BI  ")

    tk.Label(tab3, text="Motor de Recomendaciones Estratégicas", font=("Arial", 13, "bold"), fg="#00e5ff", bg="#0d0d0d").pack(pady=8)

    # Panel de alertas críticas
    f_alertas = tk.LabelFrame(tab3, text=" 🚨 Alertas Críticas ", bg="#0d0d0d", fg="#e74c3c", font=("Arial", 10, "bold"), padx=8, pady=8)
    f_alertas.pack(fill="x", padx=15, pady=5)
    txt_alertas = tk.Text(f_alertas, height=5, bg="#1a0000", fg="#ff6b6b", font=("Courier", 9),
                          relief="flat", state="disabled", wrap="word")
    txt_alertas.pack(fill="x")

    # Panel de oportunidades
    f_opor = tk.LabelFrame(tab3, text=" 💡 Oportunidades de Inversión ", bg="#0d0d0d", fg="#2ecc71", font=("Arial", 10, "bold"), padx=8, pady=8)
    f_opor.pack(fill="x", padx=15, pady=5)
    txt_opor = tk.Text(f_opor, height=5, bg="#001a00", fg="#00e676", font=("Courier", 9),
                       relief="flat", state="disabled", wrap="word")
    txt_opor.pack(fill="x")

    # Tabla resumen de productos con análisis cruzado
    tk.Label(tab3, text="Análisis cruzado: Margen × Stock × Rotación", font=("Arial", 10, "italic"), fg="#aaaaaa", bg="#0d0d0d").pack(pady=4)
    cols_bi = ("PRODUCTO", "STOCK", "MARGEN %", "VENTAS 30d", "DÍAS DE STOCK", "ESTADO", "ACCIÓN RECOMENDADA")
    t_bi = make_treeview(tab3, cols_bi, [160, 60, 80, 80, 90, 100, 200], height=9)
    t_bi.tag_configure('critico', foreground="#ff4d4d", font=("Arial", 9, "bold"))
    t_bi.tag_configure('invertir', foreground="#00e676", font=("Arial", 9, "bold"))
    t_bi.tag_configure('revisar', foreground="#FFD700")
    t_bi.tag_configure('ok', foreground="#aaaaaa")

    def cargar_recomendaciones():
        cursor = conn.cursor()
        hoy = datetime.now()

        # Obtener todos los productos
        cursor.execute("SELECT id, nombre, costo, venta, cantidad FROM productos")
        productos = cursor.fetchall()

        alertas = []
        oportunidades = []
        t_bi.delete(*t_bi.get_children())

        for p in productos:
            pid, nombre, costo, precio_venta, stock = p
            margen = ((precio_venta - costo) / precio_venta * 100) if precio_venta > 0 else 0

            # Ventas en últimos 30 días
            hace_30 = (hoy - timedelta(days=30)).strftime('%Y%m%d')
            cursor.execute("""SELECT SUM(unidades) FROM ventas
                              WHERE LOWER(producto) = LOWER(?)
                              AND (substr(fecha,7,4)||substr(fecha,4,2)||substr(fecha,1,2)) >= ?""",
                           (nombre, hace_30))
            ventas_30 = cursor.fetchone()[0] or 0

            # Días de stock estimados
            rotacion_diaria = ventas_30 / 30 if ventas_30 > 0 else 0
            dias_stock = int(stock / rotacion_diaria) if rotacion_diaria > 0 else 999

            # Lógica de estado y recomendación
            if stock <= 3 and ventas_30 > 0:
                estado = "⚠️ CRÍTICO"
                accion = "REPOSICIÓN URGENTE — alta demanda"
                tag = 'critico'
                alertas.append(f"  ⚠  {nombre}: solo {stock} unidades, {ventas_30} vendidas en 30d → REPONER YA")
            elif stock <= 3 and ventas_30 == 0:
                estado = "📦 SIN MOVIM."
                accion = "Evaluar descontinuar o promover"
                tag = 'revisar'
            elif margen >= 40 and ventas_30 >= 5:
                estado = "🌟 ESTRELLA"
                accion = f"INVERTIR MÁS — margen {margen:.0f}%, alta rotación"
                tag = 'invertir'
                oportunidades.append(f"  💰  {nombre}: margen {margen:.0f}%, {ventas_30} uds/30d → Aumentar stock")
            elif margen >= 40 and ventas_30 < 5:
                estado = "💎 ALTO MARGEN"
                accion = "Promover — buen margen, baja rotación"
                tag = 'revisar'
                oportunidades.append(f"  📢  {nombre}: margen {margen:.0f}% — necesita mayor visibilidad")
            elif dias_stock < 7 and ventas_30 > 0:
                estado = "🔴 POR AGOTAR"
                accion = f"Reponer pronto — quedan ~{dias_stock}d de stock"
                tag = 'critico'
                alertas.append(f"  🔴  {nombre}: stock para ~{dias_stock} días solamente → PLANIFICAR COMPRA")
            elif ventas_30 == 0 and stock > 10:
                estado = "❄️ ESTANCADO"
                accion = "Sin ventas 30d — considerar descuento"
                tag = 'revisar'
            else:
                estado = "✅ NORMAL"
                accion = "Mantener operación actual"
                tag = 'ok'

            dias_txt = f"~{dias_stock}d" if dias_stock < 999 else "∞"
            t_bi.insert('', tk.END,
                        values=(nombre, stock, f"{margen:.1f}%", ventas_30, dias_txt, estado, accion),
                        tags=(tag,))

        # Actualizar paneles de texto
        for txt_widget, lineas, default in [
            (txt_alertas, alertas, "  ✅  Sin alertas críticas en este momento."),
            (txt_opor, oportunidades, "  ℹ️  No se detectaron oportunidades destacadas con los datos actuales.")
        ]:
            txt_widget.config(state="normal")
            txt_widget.delete(1.0, tk.END)
            txt_widget.insert(tk.END, "\n".join(lineas) if lineas else default)
            txt_widget.config(state="disabled")

    tk.Button(tab3, text="🤖 GENERAR ANÁLISIS COMPLETO", bg="#00e5ff", fg="#0d0d0d",
              font=("Arial", 10, "bold"), width=30, command=cargar_recomendaciones).pack(pady=8)

    # ── Cargar todo al abrir ──
    cargar_rendimiento()
    cargar_estrella()
    cargar_recomendaciones()

    tk.Button(v_bi, text="← VOLVER", bg="#444", fg="white", font=("Arial", 10, "bold"),
              width=20, command=v_bi.destroy).pack(pady=10)


# ==========================================
# MENÚ PRINCIPAL Y LOGIN
# ==========================================

def mostrar_menu_principal():
    menu = tk.Toplevel(); menu.title("Panel VapeHouse"); menu.geometry("450x650"); menu.configure(bg="#121212"); menu.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    tk.Label(menu, text="VAPEHOUSE", font=("Impact", 50), fg="#00FF7F", bg="#121212").pack(pady=50)
    tk.Button(menu, text="📦 INVENTARIO", command=abrir_inventario, font=("Arial", 12, "bold"), bg="#00FF7F", width=25, height=2).pack(pady=10)
    tk.Button(menu, text="💰 CONTABILIDAD", command=abrir_contabilidad, font=("Arial", 12, "bold"), bg="#3498db", fg="white", width=25, height=2).pack(pady=10)
    tk.Button(menu, text="📈 GASTO/GANANCIA", command=abrir_analisis, font=("Arial", 12, "bold"), bg="#bb86fc", fg="white", width=25, height=2).pack(pady=10)
    tk.Button(menu, text="📊 ANÁLISIS BI", command=abrir_analisis_bi, font=("Arial", 12, "bold"), bg="#00e5ff", fg="#0d0d0d", width=25, height=2).pack(pady=10)
    tk.Button(menu, text="Cerrar Sesión", command=lambda: (menu.destroy(), root.deiconify()), bg="#e74c3c", fg="white", width=15).pack(pady=40)

def login():
    l = tk.Toplevel(); l.title("Acceso"); l.geometry("350x450"); l.configure(bg="#1a1a1a"); l.grab_set()
    tk.Label(l, text="ACCESO", font=("Arial", 18, "bold"), fg="#00FF7F", bg="#1a1a1a").pack(pady=40)
    u, p = tk.Entry(l, justify="center", font=("Arial", 12)), tk.Entry(l, show="*", justify="center", font=("Arial", 12))
    u.pack(pady=10, ipady=5); p.pack(pady=10, ipady=5)
    def auth():
        if u.get() == USUARIO_CORRECTO and p.get() == CLAVE_CORRECTA: l.destroy(); root.withdraw(); mostrar_menu_principal()
        else: messagebox.showerror("Error", "Datos incorrectos")
    tk.Button(l, text="ENTRAR", bg="#00FF7F", font=("Arial", 11, "bold"), command=auth, width=20, height=2).pack(pady=40)

iniciar_db()
root = tk.Tk(); root.title("VapeHouse"); root.geometry("500x400"); root.configure(bg="#121212")
tk.Label(root, text="VAPEHOUSE", font=("Impact", 70), fg="#00FF7F", bg="#121212").pack(expand=True)
tk.Button(root, text="ENTRAR AL SISTEMA", font=("Arial", 12, "bold"), bg="#00FF7F", command=login, padx=30, pady=10).pack(pady=50)
root.mainloop()
