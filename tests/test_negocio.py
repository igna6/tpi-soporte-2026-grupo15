import unittest
from datetime import datetime
from capa_negocio.gestor_inversiones import GestorInversiones, Inversor, Posicion, ReglaNegocioException

class TestGestorInversiones(unittest.TestCase):
    
    def setUp(self):
        # Preparar entorno para cada test
        self.gestor = GestorInversiones()
        self.gestor.usar_db = False # Evitar afectar la base de datos real durante los tests
        
        self.inversor = Inversor(
            id_inversor=1,
            nombre_usuario="inversor_test",
            saldo_efectivo=1000.0,
            fecha_creacion=datetime.now()
        )
        self.gestor.set_inversor(self.inversor)

    def test_rn03_monto_minimo_compra(self):
        """
        Prueba la RN-03: Toda COMPRA debe abortarse si el costo total es MENOR a $10.00 USD.
        """
        cantidad = 1.0
        precio_unitario = 5.0
        
        with self.assertRaises(ReglaNegocioException) as context:
            self.gestor.comprar_activo("AAPL", cantidad, precio_unitario)
            
        self.assertIn("menor al mínimo permitido de $10.00 USD", str(context.exception))
        self.assertEqual(self.inversor.saldo_efectivo, 1000.0)
        self.assertEqual(len(self.gestor.posiciones), 0)

    def test_rn01_saldo_insuficiente(self):
        """
        Prueba la RN-01: Una COMPRA debe abortarse si el costo supera el saldo.
        """
        with self.assertRaises(ReglaNegocioException) as context:
            self.gestor.comprar_activo("MSFT", 10.0, 200.0)
            
        self.assertIn("Saldo insuficiente", str(context.exception))

    def test_rn02_tenencia_insuficiente(self):
        """
        Prueba la RN-02: Una VENTA debe abortarse si la cantidad a vender es mayor a la tenencia.
        """
        posicion = Posicion(1, 1, "TSLA", 5.0, 150.0)
        self.gestor.agregar_posicion_inicial(posicion)
        
        with self.assertRaises(ReglaNegocioException) as context:
            self.gestor.vender_activo("TSLA", 10.0, 160.0)
            
        self.assertIn("supera la tenencia actual", str(context.exception))

if __name__ == '__main__':
    unittest.main()
