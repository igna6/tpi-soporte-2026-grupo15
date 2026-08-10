from flask import Flask, render_template, jsonify, request
import yfinance as yf
from capa_negocio.gestor_inversiones import GestorInversiones, ReglaNegocioException

app = Flask(__name__)
gestor = GestorInversiones()
gestor.cargar_datos_inicio(id_inversor=1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    saldo = gestor.inversor.saldo_efectivo if gestor.inversor else 0.0
    posiciones = []
    for ticker, pos in gestor.posiciones.items():
        posiciones.append({
            'ticker': ticker,
            'cantidad': pos.cant_actual,
            'precio_promedio': pos.prec_prom_compra
        })
    return jsonify({
        'saldo': saldo,
        'posiciones': posiciones
    })

@app.route('/api/chart/<ticker>', methods=['GET'])
def get_chart(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Traemos historia de 3 meses para el gráfico interactivo
        hist = stock.history(period="3mo")
        if hist.empty:
            return jsonify({'error': 'No hay datos para este ticker'}), 404
            
        # Formatear para Lightweight Charts (time, open, high, low, close)
        data = []
        for index, row in hist.iterrows():
            data.append({
                'time': index.strftime('%Y-%m-%d'),
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close']
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickers', methods=['GET'])
def get_tickers():
    try:
        popular_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']
        # yf.download es mucho más rápido y no satura la API en comparacion a iterar Ticker
        data = yf.download(popular_tickers, period="2d", group_by="ticker", progress=False)
        result = []
        
        for t in popular_tickers:
            try:
                # Extraer precios de los ultimos 2 dias
                if t in data:
                    df = data[t]['Close'].dropna()
                else:
                    # En caso de que se descargue diferente
                    df = data['Close'][t].dropna() if 'Close' in data else []
                    
                if len(df) >= 2:
                    prev_close = float(df.iloc[-2])
                    curr_price = float(df.iloc[-1])
                elif len(df) == 1:
                    prev_close = float(df.iloc[-1])
                    curr_price = float(df.iloc[-1])
                else:
                    continue
                    
                change = curr_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
                
                result.append({
                    'ticker': t,
                    'price': curr_price,
                    'change': change,
                    'change_percent': change_pct
                })
            except Exception:
                pass
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/comprar', methods=['POST'])
def comprar():
    data = request.json
    ticker = data.get('ticker', '').upper().strip()
    try:
        cantidad = float(data.get('cantidad', 0))
        if cantidad <= 0:
            return jsonify({'error': 'Cantidad debe ser mayor a 0'}), 400
            
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if hist.empty:
            return jsonify({'error': 'Ticker no encontrado en Yahoo Finance'}), 404
        precio = float(hist['Close'].iloc[-1])
        
        gestor.comprar_activo(ticker, cantidad, precio)
        return jsonify({'message': f'Compra exitosa de {cantidad} {ticker} a ${precio:.2f}'})
    except ReglaNegocioException as e:
        return jsonify({'error': str(e)}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vender', methods=['POST'])
def vender():
    data = request.json
    ticker = data.get('ticker', '').upper().strip()
    try:
        cantidad = float(data.get('cantidad', 0))
        if cantidad <= 0:
            return jsonify({'error': 'Cantidad debe ser mayor a 0'}), 400
            
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if hist.empty:
            return jsonify({'error': 'Ticker no encontrado en Yahoo Finance'}), 404
        precio = float(hist['Close'].iloc[-1])
        
        gestor.vender_activo(ticker, cantidad, precio)
        return jsonify({'message': f'Venta exitosa de {cantidad} {ticker} a ${precio:.2f}'})
    except ReglaNegocioException as e:
        return jsonify({'error': str(e)}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
