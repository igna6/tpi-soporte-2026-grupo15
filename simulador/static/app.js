// Variables Globales
let chart;
let lineSeries;
let currentTicker = null;

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    try {
        initChart();
    } catch (e) {
        console.error("Error al inicializar el gráfico:", e);
        showToast("Error cargando librería de gráficos. Verifica tu conexión.", "error");
    }

    try {
        loadPortfolio();
    } catch (e) {
        console.error("Error cargando portafolio:", e);
    }

    try {
        loadMarketTickers();
    } catch (e) {
        console.error("Error cargando tickers:", e);
    }
    
    // Auto-refresh market data every 30 seconds
    setInterval(() => {
        try { loadMarketTickers(); } catch(e){}
    }, 30000);

    // Event Listeners
    document.getElementById('btn-search').addEventListener('click', handleSearch);
    document.getElementById('search-ticker').addEventListener('keypress', (e) => {
        if(e.key === 'Enter') handleSearch();
    });

    document.getElementById('btn-buy').addEventListener('click', () => handleTrade('comprar'));
    document.getElementById('btn-sell').addEventListener('click', () => handleTrade('vender'));
});

function initChart() {
    const chartContainer = document.getElementById('tvchart');
    chart = LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: chartContainer.clientHeight,
        layout: {
            background: { type: 'solid', color: 'transparent' },
            textColor: '#64748b', // Texto secundario
        },
        grid: {
            vertLines: { color: 'rgba(0, 0, 0, 0.05)' },
            horzLines: { color: 'rgba(0, 0, 0, 0.05)' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: 'rgba(0, 0, 0, 0.1)',
        },
        timeScale: {
            borderColor: 'rgba(0, 0, 0, 0.1)',
        },
    });

    lineSeries = chart.addCandlestickSeries({
        upColor: '#16a34a', // Verde institucional
        downColor: '#dc2626', // Rojo institucional
        borderDownColor: '#dc2626',
        borderUpColor: '#16a34a',
        wickDownColor: '#dc2626',
        wickUpColor: '#16a34a',
    });

    // Handle resize
    window.addEventListener('resize', () => {
        chart.applyOptions({
            width: chartContainer.clientWidth,
            height: chartContainer.clientHeight
        });
    });
}

async function loadPortfolio() {
    try {
        const res = await fetch('/api/portfolio');
        const data = await res.json();
        
        // Actualizar saldo
        document.getElementById('saldo-value').innerText = `$${data.saldo.toFixed(2)}`;
        
        // Actualizar tabla
        const tbody = document.getElementById('portfolio-body');
        tbody.innerHTML = '';
        data.posiciones.forEach(pos => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${pos.ticker}</strong></td>
                <td>${pos.cantidad.toFixed(2)}</td>
                <td>$${pos.precio_promedio.toFixed(2)}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        showToast('Error cargando portafolio', 'error');
    }
}

async function loadMarketTickers() {
    try {
        const res = await fetch('/api/tickers');
        if (!res.ok) return;
        const tickers = await res.json();
        
        const container = document.getElementById('market-tickers');
        container.innerHTML = '';
        
        tickers.forEach(t => {
            const isUp = t.change >= 0;
            const sign = isUp ? '+' : '';
            const colorClass = isUp ? 'up' : 'down';
            
            const div = document.createElement('div');
            div.className = 'ticker-item';
            div.innerHTML = `
                <div class="ticker-name">${t.ticker}</div>
                <div class="ticker-price">
                    <span class="val">$${t.price.toFixed(2)}</span>
                    <span class="pct ${colorClass}">${sign}${t.change_percent.toFixed(2)}%</span>
                </div>
            `;
            
            div.addEventListener('click', () => {
                document.getElementById('search-ticker').value = t.ticker;
                handleSearch();
            });
            
            container.appendChild(div);
        });
    } catch (e) {
        console.error('Error cargando mercado', e);
    }
}

async function handleSearch() {
    const ticker = document.getElementById('search-ticker').value.trim().toUpperCase();
    if(!ticker) return;

    currentTicker = ticker;
    document.getElementById('asset-title').innerText = ticker;
    document.getElementById('trade-ticker-label').innerText = ticker;
    
    document.getElementById('chart-loader').classList.remove('hidden');
    lineSeries.setData([]);

    try {
        const res = await fetch(`/api/chart/${ticker}`);
        const data = await res.json();
        
        if (res.ok) {
            lineSeries.setData(data);
            chart.timeScale().fitContent();
        } else {
            showToast(data.error || 'Error cargando gráfico', 'error');
            document.getElementById('asset-title').innerText = 'Activo no encontrado';
        }
    } catch (e) {
        showToast('Error de conexión', 'error');
    } finally {
        document.getElementById('chart-loader').classList.add('hidden');
    }
}

async function handleTrade(action) {
    if(!currentTicker) {
        showToast('Primero busque y seleccione un Ticker.', 'error');
        return;
    }

    const qty = parseFloat(document.getElementById('trade-qty').value);
    if(isNaN(qty) || qty <= 0) {
        showToast('Ingrese una cantidad válida mayor a 0.', 'error');
        return;
    }

    try {
        const res = await fetch(`/api/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker: currentTicker, cantidad: qty })
        });
        
        const data = await res.json();
        
        if (res.ok) {
            showToast(data.message, 'success');
            loadPortfolio();
        } else {
            showToast(data.error, 'error');
        }
    } catch (e) {
        showToast('Error en la transacción', 'error');
    }
}

function showToast(msg, type='info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = msg;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}
