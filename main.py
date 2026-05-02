import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD
# ==========================================
USUARIO_CORRECTO = "Cosimono"
CLAVE_CORRECTA = "Cosi29032005"

# ==========================================
# BASE DE DATOS Y REPARACIÓN DE COLUMNAS
# ==========================================
def conectar_db():
    # El timeout ayuda a evitar que la DB se bloquee si hay procesos pendientes
    return sqlite3.connect('vapehouse_datos.db', timeout=10)

def iniciar_db():
    conn = conectar_db()
    cursor = conn.cursor()
    # Tabla productos (usamos 'cantidad' en lugar de 'stock')
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        categoria TEXT,
                        nombre TEXT,
                        costo REAL,
                        venta REAL,
                        cantidad INTEGER)''')
    
    # Tabla ventas (incluimos 'unidades' para el reporte)
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
                        id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        producto TEXT,
                        unidades INTEGER,
                        ganancia REAL)''')
    
    # MIGRACIÓN AUTOMÁTICA: Si las tablas son viejas, corregimos las columnas
    cursor.execute("PRAGMA table_info(productos)")
    cols_p = [c[1] for c in cursor.fetchall()]
    if 'stock' in cols_p:
        cursor.execute("ALTER TABLE productos RENAME COLUMN stock TO cantidad")
        
    cursor.execute("PRAGMA table_info(ventas)")
    cols_v = [c[1] for c in cursor.fetchall()]
    if 'unidades' not in cols_v:
        cursor.execute("ALTER TABLE ventas ADD COLUMN unidades INTEGER DEFAULT 1")
    
    conn.commit()
    conn.close()

# ==========================================
# LÓGICA DE NEGOCIO
# ==========================================

def guardar_producto(cb, ent_n, ent_c, ent_v, ent_s, tabla):
    try:
        cat, nom = cb.get(), ent_n.get()
        if not all([cat, nom, ent_c.get(), ent_v.get(), ent_s.get()]):
            messagebox.showwarning("Atención", "Por favor, llena todos los campos")
            return
        
        c, v, s = float(ent_c.get()), float(ent_v.get()), int(ent_s.get())
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (categoria, nombre, costo, venta, cantidad) VALUES (?,?,?,?,?)", 
                       (cat, nom, c, v, s))
        conn.commit()
        conn.close()
        actualizar_tabla(tabla)
        for e in [ent_n, ent_c, ent_v, ent_s]: e.delete(0, tk.END)
        messagebox.showinfo("Éxito", "Producto registrado correctamente")
    except ValueError:
        messagebox.showerror("Error", "Los valores de costo, venta y cantidad deben ser numéricos")

def realizar_ventas_multiples(tabla):
    selecciones = tabla.selection()
    if not selecciones:
        messagebox.showwarning("Venta", "Selecciona uno o más productos de la lista")
        return
    
    unidades_a_vender = simpledialog.askinteger("Unidades", "¿Cuántas unidades vas a vender de cada artículo?", minvalue=1)
    if not unidades_a_vender: return

    conn = conectar_db()
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    try:
        for item_id in selecciones:
            item = tabla.item(item_id)['values']
            # El orden de los valores debe coincidir con el de la tabla
            id_p, nom, costo, venta, cant_actual = item[0], item[2], item[3], item[4], item[5]

            if int(cant_actual) >= unidades_a_vender:
                ganancia = (float(venta) - float(costo)) * unidades_a_vender
                cursor.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id = ?", (unidades_a_vender, id_p))
                cursor.execute("INSERT INTO ventas (fecha, producto, unidades, ganancia) VALUES (?,?,?,?)", 
                               (fecha, nom, unidades_a_vender, ganancia))
            else:
                messagebox.showwarning("Sin Stock", f"No hay suficiente cantidad para '{nom}'")
        
        conn.commit()
        messagebox.showinfo("Venta", "Venta procesada con éxito")
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar la venta: {e}")
    finally:
        conn.close()
        actualizar_tabla(tabla)

def eliminar_productos(tabla):
    selecciones = tabla.selection()
    if not selecciones:
        messagebox.showwarning("Eliminar", "Selecciona los artículos a borrar")
        return
    if messagebox.askyesno("Confirmar", "¿Eliminar permanentemente los productos seleccionados?"):
        conn = conectar_db()
        cursor = conn.cursor()
        for item_id in selecciones:
            id_p = tabla.item(item_id)['values'][0]
            cursor.execute("DELETE FROM productos WHERE id = ?", (id_p,))
        conn.commit()
        conn.close()
        actualizar_tabla(tabla)

def actualizar_tabla(tabla):
    for row in tabla.get_children(): tabla.delete(row)
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, categoria, nombre, costo, venta, cantidad FROM productos")
    for fila in cursor.fetchall(): tabla.insert('', tk.END, values=fila)
    conn.close()

# ==========================================
# INTERFAZ GRÁFICA (ESTILO ORIGINAL)
# ==========================================

def abrir_inventario():
    ventana_inv = tk.Toplevel()
    ventana_inv.title("VapeHouse - Inventario")
    ventana_inv.geometry("950x750")
    ventana_inv.configure(bg="#1a1a1a")
    ventana_inv.grab_set()

    tk.Label(ventana_inv, text="GESTIÓN DE INVENTARIO", font=("Arial", 22, "bold"), fg="#00FF7F", bg="#1a1a1a").pack(pady=15)

    # Formulario de registro con etiquetas claras
    f = tk.LabelFrame(ventana_inv, text=" Datos del Producto ", bg="#1a1a1a", fg="#00FF7F", padx=10, pady=10)
    f.pack(pady=10, padx=20, fill="x")
    
    tk.Label(f, text="Categoría:", bg="#1a1a1a", fg="white").grid(row=0, column=0)
    cb_cat = ttk.Combobox(f, values=["Vapers", "Esencias", "Destilados", "Relojes", "Perfumes", "Gorras", "Camisetas"], state="readonly")
    cb_cat.grid(row=0, column=1, padx=5)
    
    tk.Label(f, text="Nombre:", bg="#1a1a1a", fg="white").grid(row=0, column=2)
    ent_n = tk.Entry(f); ent_n.grid(row=0, column=3, padx=5)
    
    tk.Label(f, text="Costo $:", bg="#1a1a1a", fg="white").grid(row=1, column=0)
    ent_c = tk.Entry(f); ent_c.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(f, text="Venta $:", bg="#1a1a1a", fg="white").grid(row=1, column=2)
    ent_v = tk.Entry(f); ent_v.grid(row=1, column=3, padx=5)
    
    tk.Label(f, text="Cantidad:", bg="#1a1a1a", fg="white").grid(row=2, column=0)
    ent_s = tk.Entry(f); ent_s.grid(row=2, column=1, padx=5)
    
    tk.Button(f, text="GUARDAR ARTÍCULO", bg="#00FF7F", fg="#121212", font=("Arial", 9, "bold"), 
              command=lambda: guardar_producto(cb_cat, ent_n, ent_c, ent_v, ent_s, tabla_inv)).grid(row=2, column=3, pady=10)

    # Tabla de productos (selección múltiple habilitada)
    cols = ("ID", "CATEGORÍA", "NOMBRE", "COSTO", "VENTA", "CANTIDAD")
    tabla_inv = ttk.Treeview(ventana_inv, columns=cols, show="headings", selectmode="extended")
    for col in cols: 
        tabla_inv.heading(col, text=col)
        tabla_inv.column(col, width=100, anchor="center")
    tabla_inv.pack(pady=10, padx=20, fill="both", expand=True)

    # Panel de botones de acción
    btns = tk.Frame(ventana_inv, bg="#1a1a1a")
    btns.pack(pady=20, fill="x", padx=20)
    
    tk.Button(btns, text="💰 VENDER SELECCIÓN", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), 
              command=lambda: realizar_ventas_multiples(tabla_inv), width=25, height=2).pack(side="left", padx=5)
    
    tk.Button(btns, text="🗑 ELIMINAR", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), 
              command=lambda: eliminar_productos(tabla_inv), width=15, height=2).pack(side="left", padx=5)
    
    tk.Button(btns, text="← VOLVER AL MENÚ", bg="#555555", fg="white", font=("Arial", 10, "bold"), 
              command=ventana_inv.destroy, width=20, height=2).pack(side="right", padx=5)
    
    actualizar_tabla(tabla_inv)

def abrir_contabilidad():
    ventana_cont = tk.Toplevel()
    ventana_cont.title("VapeHouse - Contabilidad")
    ventana_cont.geometry("850x650")
    ventana_cont.configure(bg="#1a1a1a")
    ventana_cont.grab_set()

    tk.Label(ventana_cont, text="REPORTE DE VENTAS", font=("Arial", 22, "bold"), fg="#3498db", bg="#1a1a1a").pack(pady=20)

    cols = ("ID", "FECHA", "PRODUCTO", "UNDS", "GANANCIA")
    tabla_v = ttk.Treeview(ventana_cont, columns=cols, show="headings")
    for col in cols: 
        tabla_v.heading(col, text=col)
        tabla_v.column(col, width=120, anchor="center")
    tabla_v.pack(pady=10, padx=20, fill="both", expand=True)

    conn = conectar_db()
    cursor = conn.cursor()
    # Especificamos el orden para que los datos no se crucen en el reporte
    cursor.execute("SELECT id_venta, fecha, producto, unidades, ganancia FROM ventas")
    
    total_ganancia = 0
    for fila in cursor.fetchall():
        tabla_v.insert('', tk.END, values=fila)
        total_ganancia += fila[4] # Sumamos la ganancia real
    conn.close()

    tk.Label(ventana_cont, text=f"GANANCIA TOTAL: ${total_ganancia:,.2f}", 
             font=("Arial", 16, "bold"), fg="#00FF7F", bg="#1a1a1a").pack(pady=10)
    
    tk.Button(ventana_cont, text="← VOLVER AL MENÚ", bg="#555555", fg="white", 
              font=("Arial", 10, "bold"), command=ventana_cont.destroy, width=20).pack(pady=20)

def mostrar_menu_principal():
    menu = tk.Toplevel()
    menu.title("Panel de Control")
    menu.geometry("450x550")
    menu.configure(bg="#121212")
    menu.protocol("WM_DELETE_WINDOW", lambda: ventana_inicio.destroy())
    
    tk.Label(menu, text="VAPEHOUSE", font=("Impact", 45), fg="#00FF7F", bg="#121212").pack(pady=30)
    
    tk.Button(menu, text="📦 GESTIONAR INVENTARIO", command=abrir_inventario, font=("Arial", 11, "bold"), 
              bg="#00FF7F", width=30, height=2).pack(pady=10)
    
    tk.Button(menu, text="💰 VER CONTABILIDAD", command=abrir_contabilidad, font=("Arial", 11, "bold"), 
              bg="#3498db", fg="white", width=30, height=2).pack(pady=10)
    
    tk.Button(menu, text="← Cerrar Sesión", command=lambda: (menu.destroy(), ventana_inicio.deiconify()), 
              bg="#e74c3c", fg="white", font=("Arial", 9, "bold")).pack(pady=40)

def abrir_ventana_login():
    global ent_user, ent_pass, ventana_login
    ventana_login = tk.Toplevel()
    ventana_login.title("Acceso")
    ventana_login.geometry("350x400")
    ventana_login.configure(bg="#1a1a1a")
    
    tk.Label(ventana_login, text="INICIAR SESIÓN", font=("Arial", 18, "bold"), fg="#00FF7F", bg="#1a1a1a").pack(pady=30)
    
    ent_user = tk.Entry(ventana_login, justify="center", font=("Arial", 12))
    ent_user.pack(pady=10)
    
    ent_pass = tk.Entry(ventana_login, show="*", justify="center", font=("Arial", 12))
    ent_pass.pack(pady=10)
    
    tk.Button(ventana_login, text="INGRESAR", 
              command=lambda: (ventana_login.destroy(), ventana_inicio.withdraw(), mostrar_menu_principal()) 
              if ent_user.get()==USUARIO_CORRECTO and ent_pass.get()==CLAVE_CORRECTA 
              else messagebox.showerror("Error", "Acceso denegado"), 
              bg="#00FF7F", font=("Arial", 10, "bold"), width=15, height=2).pack(pady=30)

# ==========================================
# INICIO DE LA APLICACIÓN
# ==========================================
iniciar_db()
ventana_inicio = tk.Tk()
ventana_inicio.title("VapeHouse Pro")
ventana_inicio.geometry("650x550")
ventana_inicio.configure(bg="#121212")

tk.Label(ventana_inicio, text="VAPEHOUSE", font=("Impact", 80), fg="#00FF7F", bg="#121212").place(relx=0.5, rely=0.4, anchor="center")

tk.Button(ventana_inicio, text="INICIAR SESIÓN", command=abrir_ventana_login, 
          font=("Arial", 14, "bold"), bg="#00FF7F", padx=50, pady=18).place(relx=0.5, rely=0.7, anchor="center")

ventana_inicio.mainloop()
