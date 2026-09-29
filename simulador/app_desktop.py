import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf
from capa_negocio.gestor_inversiones import GestorInversiones

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("Dark")  # Modos: "System" (estándar), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue" (estándar), "green", "dark-blue"

class SimuladorDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Simulador de Inversiones TPI")
        self.geometry("900x600")
        
        # Inicializar el Gestor de Inversiones (Capa Negocio)
        self.gestor = GestorInversiones()
        self.gestor.cargar_datos_inicio(id_inversor=1)
        
        # Crear sistema de Pestañas
        self.tabview = ctk.CTkTabview(self, width=850, height=550)
        self.tabview.pack(padx=20, pady=20)
        
        self.tabview.add("Watchlist")
        self.tabview.add("Benchmark (Índice)")
        
        self.configurar_pestaña_watchlist()
        self.configurar_pestaña_benchmark()

    def configurar_pestaña_watchlist(self):
        tab = self.tabview.tab("Watchlist")
        
        # Frame superior para agregar
        top_frame = ctk.CTkFrame(tab)
        top_frame.pack(pady=10, fill="x")
        
        self.entry_ticker = ctk.CTkEntry(top_frame, placeholder_text="Ticker (ej. AAPL)")
        self.entry_ticker.pack(side="left", padx=10)
        
        btn_agregar = ctk.CTkButton(top_frame, text="Agregar a Watchlist", command=self.agregar_ticker)
        btn_agregar.pack(side="left", padx=10)
        
        # Frame para mostrar la lista
        self.lista_frame = ctk.CTkScrollableFrame(tab, label_text="Tus Favoritos")
        self.lista_frame.pack(pady=10, fill="both", expand=True)
        
        self.actualizar_ui_watchlist()

    def agregar_ticker(self):
        ticker = self.entry_ticker.get().upper().strip()
        if ticker:
            self.gestor.agregar_a_watchlist(ticker)
            self.entry_ticker.delete(0, "end")
            self.actualizar_ui_watchlist()

    def actualizar_ui_watchlist(self):
        # Limpiar frame
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
            
        tickers = self.gestor.obtener_watchlist()
        for t in tickers:
            label = ctk.CTkLabel(self.lista_frame, text=f"⭐ {t}", font=("Arial", 16, "bold"))
            label.pack(pady=5, anchor="w", padx=20)

    def configurar_pestaña_benchmark(self):
        tab = self.tabview.tab("Benchmark (Índice)")
        
        btn_cargar = ctk.CTkButton(tab, text="Cargar Gráfico (S&P 500 vs AAPL de prueba)", command=self.mostrar_grafico)
        btn_cargar.pack(pady=10)
        
        self.grafico_frame = ctk.CTkFrame(tab)
        self.grafico_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def mostrar_grafico(self):
        # Limpiar frame anterior
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()
            
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Descargar datos de ejemplo: SPY (S&P 500) y AAPL (como simulador del portafolio)
        # En tu proyecto real, reemplazarías AAPL por los datos del HistorialPatrimonio
        try:
            data = yf.download(["SPY", "AAPL"], period="1mo", progress=False)
            spy_close = data['Close']['SPY']
            aapl_close = data['Close']['AAPL']
            
            # Normalizar a porcentaje (base 0)
            spy_pct = ((spy_close - spy_close.iloc[0]) / spy_close.iloc[0]) * 100
            aapl_pct = ((aapl_close - aapl_close.iloc[0]) / aapl_close.iloc[0]) * 100
            
            ax.plot(spy_pct.index, spy_pct, label='S&P 500 (SPY)', color='blue')
            ax.plot(aapl_pct.index, aapl_pct, label='Portafolio (AAPL de ref)', color='orange')
            
            ax.set_title("Rendimiento: Portafolio vs Mercado")
            ax.set_ylabel("Rendimiento (%)")
            ax.legend()
            ax.grid(True)
            fig.autofmt_xdate()
            
            canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            lbl_error = ctk.CTkLabel(self.grafico_frame, text=f"Error al cargar: {str(e)}", text_color="red")
            lbl_error.pack(pady=20)

if __name__ == "__main__":
    app = SimuladorDesktopApp()
    app.mainloop()
