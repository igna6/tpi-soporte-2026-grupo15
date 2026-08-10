from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from capa_datos import database

class ReglaNegocioException(Exception):
    """Excepción lanzada cuando se viola una regla de negocio."""
    pass

@dataclass
class Inversor:
    id_inversor: int
    nombre_usuario: str
    saldo_efectivo: float
    fecha_creacion: datetime

@dataclass
class ActivoFinanciero:
    ticker: str
    nombre_empresa: str
    tipo_activo: str

@dataclass
class Transaccion:
    id_transaccion: int
    id_inversor: int
    ticker_activo: str
    tipo_operacion: str
    cantidad: float
    precio_unitario_ejecucion: float
    fecha_hora: datetime

@dataclass
class Posicion:
    id_posicion: int
    id_inversor: int
    ticker_activo: str
    cant_actual: float
    prec_prom_compra: float

class GestorInversiones:
    def __init__(self):
        self.inversor: Optional[Inversor] = None
        self.posiciones: dict[str, Posicion] = {}
        # Flag para evitar escrituras a BD durante las pruebas unitarias
        self.usar_db = True 

    def cargar_datos_inicio(self, id_inversor: int = 1):
        """Carga los datos iniciales desde la Capa de Datos."""
        database.inicializar_db()
        inv_data = database.obtener_inversor(id_inversor)
        if inv_data:
            self.inversor = Inversor(
                id_inversor=inv_data['id_inversor'],
                nombre_usuario=inv_data['nombre_usuario'],
                saldo_efectivo=inv_data['saldo_efectivo'],
                fecha_creacion=datetime.fromisoformat(inv_data['fecha_creacion'])
            )
            
            pos_data = database.obtener_posiciones(id_inversor)
            for p in pos_data:
                pos = Posicion(
                    id_posicion=p['id_posicion'],
                    id_inversor=p['id_inversor'],
                    ticker_activo=p['ticker_activo'],
                    cant_actual=p['cant_actual'],
                    prec_prom_compra=p['prec_prom_compra']
                )
                self.posiciones[pos.ticker_activo] = pos

    def set_inversor(self, inversor: Inversor):
        """Configura el inversor (usado en tests)."""
        self.inversor = inversor

    def agregar_posicion_inicial(self, posicion: Posicion):
        """Método auxiliar para tests."""
        self.posiciones[posicion.ticker_activo] = posicion

    def comprar_activo(self, ticker: str, cantidad: float, precio_unitario: float) -> Transaccion:
        if not self.inversor:
            raise ValueError("Inversor no configurado en el Gestor.")

        costo_total = precio_unitario * cantidad

        # RN-03: Monto mínimo de compra
        if costo_total < 10.00:
            raise ReglaNegocioException(f"El costo total de la compra (${costo_total:.2f}) es menor al mínimo permitido de $10.00 USD.")

        # RN-01: Saldo suficiente
        if costo_total > self.inversor.saldo_efectivo:
            raise ReglaNegocioException(f"Saldo insuficiente. Saldo actual: ${self.inversor.saldo_efectivo:.2f}, Costo: ${costo_total:.2f}")

        # Descontar saldo
        self.inversor.saldo_efectivo -= costo_total

        # Actualizar posición
        if ticker in self.posiciones:
            pos = self.posiciones[ticker]
            costo_historico = pos.cant_actual * pos.prec_prom_compra
            nuevo_costo = costo_historico + costo_total
            pos.cant_actual += cantidad
            pos.prec_prom_compra = nuevo_costo / pos.cant_actual
        else:
            pos = Posicion(
                id_posicion=0,
                id_inversor=self.inversor.id_inversor,
                ticker_activo=ticker,
                cant_actual=cantidad,
                prec_prom_compra=precio_unitario
            )
            self.posiciones[ticker] = pos

        transaccion = Transaccion(
            id_transaccion=0,
            id_inversor=self.inversor.id_inversor,
            ticker_activo=ticker,
            tipo_operacion='COMPRA',
            cantidad=cantidad,
            precio_unitario_ejecucion=precio_unitario,
            fecha_hora=datetime.now()
        )

        # Delegar persistencia a Capa de Datos si corresponde
        if self.usar_db:
            database.actualizar_saldo_inversor(self.inversor.id_inversor, self.inversor.saldo_efectivo)
            database.asegurar_activo(ticker)
            database.registrar_transaccion(
                self.inversor.id_inversor, ticker, 'COMPRA', cantidad, precio_unitario, transaccion.fecha_hora.isoformat()
            )
            database.guardar_posicion(self.inversor.id_inversor, ticker, pos.cant_actual, pos.prec_prom_compra)

        return transaccion

    def vender_activo(self, ticker: str, cantidad: float, precio_unitario: float) -> Transaccion:
        if not self.inversor:
            raise ValueError("Inversor no configurado en el Gestor.")

        if ticker not in self.posiciones:
            raise ReglaNegocioException(f"No posee tenencia del activo '{ticker}' para vender.")

        pos = self.posiciones[ticker]

        # RN-02: Tenencia máxima a vender
        if cantidad > pos.cant_actual:
            raise ReglaNegocioException(f"Cantidad a vender ({cantidad}) supera la tenencia actual ({pos.cant_actual}).")

        # Sumar saldo
        ingreso_total = precio_unitario * cantidad
        self.inversor.saldo_efectivo += ingreso_total

        # Descontar cantidad de posición
        pos.cant_actual -= cantidad

        if pos.cant_actual == 0:
            del self.posiciones[ticker]

        transaccion = Transaccion(
            id_transaccion=0,
            id_inversor=self.inversor.id_inversor,
            ticker_activo=ticker,
            tipo_operacion='VENTA',
            cantidad=cantidad,
            precio_unitario_ejecucion=precio_unitario,
            fecha_hora=datetime.now()
        )

        # Delegar persistencia a Capa de Datos si corresponde
        if self.usar_db:
            database.actualizar_saldo_inversor(self.inversor.id_inversor, self.inversor.saldo_efectivo)
            database.registrar_transaccion(
                self.inversor.id_inversor, ticker, 'VENTA', cantidad, precio_unitario, transaccion.fecha_hora.isoformat()
            )
            if pos.cant_actual == 0:
                database.eliminar_posicion(self.inversor.id_inversor, ticker)
            else:
                database.guardar_posicion(self.inversor.id_inversor, ticker, pos.cant_actual, pos.prec_prom_compra)

        return transaccion

    def calcular_y_registrar_patrimonio(self):
        """Calcula el valor de mercado actual de todas las posiciones + efectivo y lo registra."""
        if not self.inversor or not self.usar_db:
            return

        import yfinance as yf
        from datetime import datetime
        
        valor_acciones = 0.0
        
        if self.posiciones:
            # Obtener todos los tickers
            tickers = list(self.posiciones.keys())
            try:
                # Descarga masiva para ser más rápido
                data = yf.download(tickers, period="1d", group_by="ticker", progress=False)
                for ticker, pos in self.posiciones.items():
                    try:
                        # Extraer precio de cierre más reciente
                        if len(tickers) == 1:
                            precio_actual = float(data['Close'].iloc[-1])
                        else:
                            if ticker in data:
                                df = data[ticker]['Close'].dropna()
                            else:
                                df = data['Close'][ticker].dropna() if 'Close' in data else []
                                
                            if len(df) > 0:
                                precio_actual = float(df.iloc[-1])
                            else:
                                precio_actual = pos.prec_prom_compra # fallback
                                
                        valor_acciones += precio_actual * pos.cant_actual
                    except Exception:
                        valor_acciones += pos.prec_prom_compra * pos.cant_actual
            except Exception as e:
                # Fallback si falla yfinance masivo
                for ticker, pos in self.posiciones.items():
                    valor_acciones += pos.prec_prom_compra * pos.cant_actual
                    
        total_patrimonio = self.inversor.saldo_efectivo + valor_acciones
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        
        database.registrar_patrimonio_diario(
            self.inversor.id_inversor,
            self.inversor.saldo_efectivo,
            valor_acciones,
            total_patrimonio,
            fecha_hoy
        )
