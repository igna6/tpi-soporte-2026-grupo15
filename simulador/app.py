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
            
        # Calcular SMA 20 (Simple Moving Average de 20 días)
        hist['SMA20'] = hist['Close'].rolling(window=20).mean()
            
        # Formatear para Lightweight Charts (time, open, high, low, close)
        data = []
        for index, row in hist.iterrows():
            sma = row['SMA20']
            data.append({
                'time': index.strftime('%Y-%m-%d'),
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'sma20': sma if not str(sma) == 'nan' else None
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

@app.route('/api/info/<ticker>', methods=['GET'])
def get_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        # fast_info es mas rapido si existe, sino caemos a info
        info = stock.info
        
        return jsonify({
            'sector': info.get('sector', 'Desconocido'),
            'industry': info.get('industry', 'Desconocido'),
            'marketCap': info.get('marketCap', 0),
            'trailingPE': info.get('trailingPE', 0),
            'dividendYield': info.get('dividendYield', 0),
            'recommendation': info.get('recommendationKey', 'none'),
            'longName': info.get('longName', ticker)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/<ticker>', methods=['GET'])
def get_news(ticker):
    try:
        stock = yf.Ticker(ticker)
        noticias = stock.news
        result = []
        for n in noticias[:5]:
            # Dependiendo de la version de yfinance, la estructura puede variar
            if 'content' in n:
                content = n['content']
                provider = content.get('provider', {})
                link = content.get('previewUrl', '')
                if not link and 'canonicalUrl' in content:
                    link = content['canonicalUrl'].get('url', '')
                
                result.append({
                    'title': content.get('title'),
                    'link': link,
                    'publisher': provider.get('displayName', 'Desconocido'),
                    'time': content.get('pubDate')
                })
            else:
                # Estructura antigua
                result.append({
                    'title': n.get('title'),
                    'link': n.get('link'),
                    'publisher': n.get('publisher'),
                    'time': n.get('providerPublishTime')
                })
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

@app.route('/api/roi_chart.png')
def roi_chart():
    try:
        # Registrar valor actual antes de graficar
        gestor.calcular_y_registrar_patrimonio()
        
        from capa_datos import database
        historial = database.obtener_historial_patrimonio(1)
        if not historial:
            return jsonify({'error': 'No hay datos'}), 404
            
        import io
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        fechas = [row['fecha'] for row in historial]
        valores = [row['total_patrimonio'] for row in historial]
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(fechas, valores, marker='o', color='#2563eb', linewidth=2)
        ax.fill_between(fechas, valores, color='#2563eb', alpha=0.1)
        
        ax.set_title('Evolución de Patrimonio', fontsize=14, color='#1e293b', pad=10)
        ax.set_ylabel('USD', fontsize=10)
        
        plt.xticks(rotation=30, ha='right', fontsize=8)
        plt.yticks(fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        img.seek(0)
        plt.close(fig)
        
        from flask import send_file
        return send_file(img, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
