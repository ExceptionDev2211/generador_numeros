import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd  


def half_squares(seed, numQuantity):
    numbers = []
    length = len(str(seed))
    for _ in range(numQuantity):
        number = str(seed**2).zfill(2 * length)
        mid = number[len(number)//2 - length//2 : len(number)//2 + length//2]
        seed = int(mid)
        numbers.append(seed / (10 ** length))
    return numbers

def congruencia_lineal(x0, a, c, m, n):
    numeros = []
    x = x0
    for _ in range(n):
        x = (a * x + c) % m
        numeros.append(x / (m-1))
    return numeros

def multiplicative_congruential(seed, a, m, numQuantity):
    numbers = []
    Xn = seed
    for _ in range(numQuantity):
        Xn = (a * Xn) % m
        numbers.append(Xn / m)
    return np.array(numbers)

def congruencial_mixto(seed, a, c, m, numQuantity):
    numbers = []
    for _ in range(numQuantity):
        seed = (a * seed + c) % m
        numbers.append(seed / m)
    return numbers


def prueba_chi_cuadrado(numeros, k=10):
    n = len(numeros)
    frec_observada, _ = np.histogram(numeros, bins=k, range=(0,1))
    frec_esperada = [n/k] * k
    chi_cuadrado = sum((fo - fe) ** 2 / fe for fo, fe in zip(frec_observada, frec_esperada))
    p_valor = 1 - stats.chi2.cdf(chi_cuadrado, df=k-1)
    return chi_cuadrado, p_valor

def prueba_ks(numeros):
    statistic, p_value = stats.kstest(numeros, 'uniform')
    return statistic, p_value

def prueba_varianza(numeros):
    n = len(numeros)
    variance = np.var(numeros, ddof=1)
    sigma = 1 / np.sqrt(12)
    Z = (variance - sigma**2) / (sigma**2 / np.sqrt(n))
    z_critical = stats.norm.ppf(0.975)
    return variance, Z, z_critical


def generar_numeros():
    try:
        metodo = metodo_var.get()
        prueba = prueba_var.get()
        seed = int(seed_entry.get())
        numQuantity = int(cantidad_entry.get())

        if metodo == "Cuadrados Medios":
            numeros = half_squares(seed, numQuantity)
        else:
            a, m = int(a_entry.get()), int(m_entry.get())
            c = int(c_entry.get()) if metodo in ["Congruencial Lineal", "Congruencial Mixto"] else 0
            
            if metodo == "Congruencial Lineal":
                numeros = congruencia_lineal(seed, a, c, m, numQuantity)
            elif metodo == "Congruencial Multiplicativo":
                numeros = multiplicative_congruential(seed, a, m, numQuantity)
            elif metodo == "Congruencial Mixto":
                numeros = congruencial_mixto(seed, a, c, m, numQuantity)


        resultado = ""
        if prueba == "Chi-Cuadrado":
            chi2, p = prueba_chi_cuadrado(numeros)
            resultado = f"Chi-cuadrado: {chi2:.5f}, p-valor: {p:.5f}\n"
            resultado += "Distribución aceptable." if p > 0.05 else "Distribución no uniforme."
        elif prueba == "Kolmogorov-Smirnov":
            ks_stat, p_value = prueba_ks(numeros)
            resultado = f"Estadístico KS: {ks_stat:.5f}, p-valor: {p_value:.5f}\n"
            resultado += "Distribución aceptable." if p_value > 0.05 else "Distribución no uniforme."
        elif prueba == "Varianza":
            variance, Z, z_critical = prueba_varianza(numeros)
            resultado = f"Varianza: {variance:.5f}\n"
            resultado += f"Z: {Z:.5f}, Valor crítico: ±{z_critical:.5f}\n"
            resultado += "Distribución aceptable." if abs(Z) < z_critical else "Distribución no uniforme."

        resultado_label.config(text=resultado)


        for row in table.get_children():
            table.delete(row)


        for i, num in enumerate(numeros, start=1):
            table.insert("", "end", values=(i, f"{num:.5f}"))


        plt.hist(numeros, bins=10, edgecolor='black', alpha=0.7)
        plt.title("Histograma de los números generados")
        plt.xlabel("Valor")
        plt.ylabel("Frecuencia")
        plt.show()


        exportar_a_excel(numeros)

    except ValueError:
        messagebox.showerror("Error", "Ingrese valores numéricos válidos")


def exportar_a_excel(numeros):
    try:

        df = pd.DataFrame(numeros, columns=["Número"])


        archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

        if archivo:

            df.to_excel(archivo, index=False)
            messagebox.showinfo("Éxito", f"Archivo guardado en: {archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar el archivo: {e}")


root = tk.Tk()
root.title("Generador de Números Pseudoaleatorios")
root.geometry("900x500")


frame_izquierda = tk.Frame(root)
frame_izquierda.pack(side="left", padx=20, pady=20, fill="both", expand=True)

frame_derecha = tk.Frame(root)
frame_derecha.pack(side="right", padx=20, pady=20, fill="both", expand=True)


metodo_var = tk.StringVar(value="Cuadrados Medios")
prueba_var = tk.StringVar(value="Chi-Cuadrado")


tk.Label(frame_izquierda, text="Método:", font=("Arial", 12)).pack(anchor="w")
metodo_combobox = ttk.Combobox(frame_izquierda, textvariable=metodo_var, values=[
    "Cuadrados Medios", "Congruencial Lineal", "Congruencial Multiplicativo", "Congruencial Mixto"
], state="readonly")
metodo_combobox.pack(fill="x")

tk.Label(frame_izquierda, text="Semilla:", font=("Arial", 12)).pack(anchor="w")
seed_entry = tk.Entry(frame_izquierda, font=("Arial", 12))
seed_entry.pack(fill="x")

tk.Label(frame_izquierda, text="Cantidad de números:", font=("Arial", 12)).pack(anchor="w")
cantidad_entry = tk.Entry(frame_izquierda, font=("Arial", 12))
cantidad_entry.pack(fill="x")


parametros_frame = tk.Frame(frame_izquierda)
parametros_frame.pack(fill="x", pady=10)

a_label = tk.Label(parametros_frame, text="a:", font=("Arial", 12))
a_label.grid(row=0, column=0, padx=5)
a_entry = tk.Entry(parametros_frame, font=("Arial", 12), width=10)
a_entry.grid(row=0, column=1, padx=5)

c_label = tk.Label(parametros_frame, text="c:", font=("Arial", 12))
c_label.grid(row=0, column=2, padx=5)
c_entry = tk.Entry(parametros_frame, font=("Arial", 12), width=10)
c_entry.grid(row=0, column=3, padx=5)

m_label = tk.Label(parametros_frame, text="m:", font=("Arial", 12))
m_label.grid(row=0, column=4, padx=5)
m_entry = tk.Entry(parametros_frame, font=("Arial", 12), width=10)
m_entry.grid(row=0, column=5, padx=5)


def actualizar_parametros(*args):
    metodo = metodo_var.get()
    if metodo == "Cuadrados Medios":
        a_label.grid_remove()
        a_entry.grid_remove()
        c_label.grid_remove()
        c_entry.grid_remove()
        m_label.grid_remove()
        m_entry.grid_remove()
    elif metodo == "Congruencial Lineal":
        a_label.grid()
        a_entry.grid()
        c_label.grid()
        c_entry.grid()
        m_label.grid()
        m_entry.grid()
    elif metodo == "Congruencial Multiplicativo":
        a_label.grid()
        a_entry.grid()
        c_label.grid_remove()
        c_entry.grid_remove()
        m_label.grid()
        m_entry.grid()
    elif metodo == "Congruencial Mixto":
        a_label.grid()
        a_entry.grid()
        c_label.grid()
        c_entry.grid()
        m_label.grid()
        m_entry.grid()


metodo_var.trace("w", actualizar_parametros)


actualizar_parametros()

tk.Label(frame_izquierda, text="Prueba de Validación:", font=("Arial", 12)).pack(anchor="w")
ttk.Combobox(frame_izquierda, textvariable=prueba_var, values=[
    "Chi-Cuadrado", "Kolmogorov-Smirnov", "Varianza"
], state="readonly").pack(fill="x")

tk.Button(frame_izquierda, text="Generar y Validar", command=generar_numeros).pack(pady=10)


table = ttk.Treeview(frame_derecha, columns=("#", "Número"), show="headings")
table.heading("#", text="#")
table.heading("Número", text="Número")
table.pack(fill="both", expand=True)

resultado_label = tk.Label(frame_izquierda, text="", font=("Arial", 12))
resultado_label.pack()

root.mainloop()