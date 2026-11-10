# Simulador de Inversiones

---
[![Documentacion]([https://drive.google.com/uc?export=view&id=1e7ciR7wceGImaaelErfbyrsjsjFLi6hy](https://drive.google.com/drive/folders/1cqcP50Q9E3WfAuoIeOK2L_lEJ1y1z2Ge?usp=sharing))]
## Descripción del proyecto

El alcance de este proyecto es desarrollar un **Simulador de Inversiones** interactivo. Es una aplicación web que permite a cualquier persona simular la compra y venta de acciones de empresas reales (como Apple, Tesla o Google) utilizando dinero virtual, fundamentado en cotizaciones obtenidas del mercado actual en tiempo real.

**Objetivos principales:**
* **Cotizaciones Reales:** Conectarse automáticamente a internet mediante Yahoo Finance para consultar el valor exacto de las acciones al momento de la operación.
* **Análisis Fundamental (Research):** Proveer información detallada del perfil de la empresa (sector, industria) y las noticias financieras más recientes para que el usuario tome decisiones informadas.
* **Experiencia de Usuario Interactiva:** Proveer una interfaz gráfica donde el usuario ingrese la abreviatura de la empresa (Ticker) y la cantidad, y el sistema calcule totales a pagar de forma automática.
* **Validación de Operaciones:** Revisar que las transacciones cumplan con reglas financieras lógicas (fondos, tenencias, montos mínimos) antes de ser registradas.
* **Gestión de Portafolio:** Almacenar las operaciones exitosas en una base de datos local y proveer una vista del historial de compras y el estado del portafolio virtual.
* **Análisis Visual:** Recopilar datos de las inversiones para generar gráficos que muestren las ganancias o pérdidas en un determinado período de tiempo.

---

## Modelo de Dominio

*(Nota: Reemplazar la ruta de la imagen con la ubicación real de tu diagrama exportado de draw.io actualizado)*

[![Diagrama DER](https://drive.google.com/uc?export=view&id=1e7ciR7wceGImaaelErfbyrsjsjFLi6hy)](https://drive.google.com/file/d/1e7ciR7wceGImaaelErfbyrsjsjFLi6hy/view?usp=sharing)

---

## Bosquejo de Arquitectura

El sistema implementa una arquitectura estructurada lógicamente en 3 capas (Presentación, Negocio y Datos).

*(Nota: Reemplazar la ruta de la imagen con la ubicación real de tu diagrama de arquitectura)*

[![Bosquejo de Arquitectura](https://drive.google.com/uc?export=view&id=1f09V20dCgih-TdjhEtRT3qMIOuhM4mQx)](https://drive.google.com/file/d/1f09V20dCgih-TdjhEtRT3qMIOuhM4mQx/view?usp=sharing)

---

## Requerimientos

### Funcionales

**Módulo 1: Operaciones de Mercado**
* **RF-01 | Consultar Cotización en Tiempo Real:** El sistema debe permitir al usuario ingresar el Ticker de un activo financiero y consultar su precio de mercado actual conectándose a la API de Yahoo Finance.
* **RF-02 | Registrar Orden de Compra:** El sistema debe permitir al usuario registrar la compra de un activo indicando la cantidad deseada. El sistema calculará el monto total en base al precio actual de la API y lo descontará del saldo disponible del usuario.
* **RF-03 | Registrar Orden de Venta:** El sistema debe permitir al usuario registrar la venta de un activo que posea en su portafolio. El sistema calculará el total a recibir basándose en la cotización actual de la API y sumará ese monto al saldo del usuario.
* **RF-04 | Seleccionar Agente Bursátil (Broker) y Calcular Comisión:** El sistema debe permitir al usuario seleccionar el broker para la operación (PPI, IOL o Sin Comisión). La Capa de Negocio calculará automáticamente la comisión aplicable (porcentual o arancel mínimo fijado) y la sumará al costo total de la compra o la descontará del neto de la venta.

**Módulo 2: Visualización y Reportes**
* **RF-05 | Visualizar Portafolio (Posiciones Actuales):** El sistema debe mostrar en pantalla un listado con los activos que el usuario posee actualmente, indicando para cada uno el Ticker, la cantidad de acciones en tenencia y el precio promedio al que fueron compradas.
* **RF-06| Consultar Historial de Transacciones:** El sistema debe proveer una vista donde el usuario pueda revisar el registro histórico de todas sus operaciones (compras y ventas), mostrando fecha, tipo de operación, Ticker, cantidad, precio de ejecución y monto total.
* **RF-07 | Visualizar Saldo de Cuenta:** El sistema debe mantener visible en todo momento el saldo de dinero virtual (efectivo) que el usuario tiene disponible para realizar nuevas compras.
* **RF-08 | Generación de Gráficos:** A partir de las inversiones realizadas, se podrán generar gráficos que muestren las ganancias o pérdidas del usuario en un determinado tiempo.
* **RF-09 | Consultar Perfil del Activo:** El sistema debe permitir al usuario visualizar la información fundamental de la empresa seleccionada (sector, industria y descripción breve) obtenida a través de la API externa.
* **RF-10 | Visualizar Noticias Relevantes:** El sistema debe mostrar los titulares de las noticias financieras más recientes asociadas al Ticker consultado, extraídas en tiempo real para apoyar la decisión de inversión.
* **RF-11 | Watchlist (Lista de Seguimiento):** El sistema debe permitir al usuario marcar acciones como "favoritas" y proveer una vista rápida de las cotizaciones en tiempo real de esta lista, sin necesidad de realizar una búsqueda manual.
* **RF-12 | Comparativa con Índice (Benchmark):** Al generar gráficos de rendimiento, el sistema debe mostrar opcionalmente una curva comparativa con el índice S&P 500 (Ticker: SPY) para evaluar el desempeño de las inversiones contra el mercado.
* **RF-13 | Indicadores de Análisis Técnico / Alertas de Posición:** El sistema debe mostrar sugerencias automáticas de Take Profit (ganancia esperada) y Stop Loss (límite de pérdida) sobre cada activo del portafolio, calculados sobre el precio promedio ponderado de compra.

**Módulo 3: Validaciones del Sistema (Reglas de Negocio)**
* **RF-14 | Validar Fondos Suficientes (RN-01):** Al intentar realizar una compra, el sistema debe impedir la transacción y mostrar un mensaje de error si el costo total (Monto del Activo + Comisión del Broker seleccionado) supera el saldo de cuenta disponible.
* **RF-15 | Validar Tenencia Previa (RN-02):** Al intentar realizar una venta, el sistema debe impedir la transacción y mostrar un mensaje de error si el usuario intenta vender una cantidad mayor a la que posee en su portafolio.
* **RF-16 | Validar Monto Mínimo (RN-03):** El sistema debe rechazar cualquier operación de compra cuyo monto total calculado sea inferior a $10.00 USD (o la moneda base definida), mostrando el aviso correspondiente para evitar micro-transacciones.
* **RF-17 | Seleccionar Agente Bursátil (Broker) y Calcular Comisión:** El sistema debe permitir al usuario seleccionar el broker para la operación (PPI, IOL o Sin Comisión). La Capa de Negocio calculará automáticamente la comisión aplicable (porcentual o arancel mínimo fijado) y la sumará al costo total de la compra o la descontará del neto de la venta.

---

### No Funcionales

#### Portability
* **Obligatorio:** El sistema debe ejecutarse desde un único archivo `.py` llamado `app.py` que sirva como backend Web o aplicación de escritorio.

#### Security
* **Obligatorio:** Todas las contraseñas deben guardarse con encriptado criptográfico (SHA o equivalente).
* **Obligatorio:** Todos los Tokens / API Keys o similares no deben exponerse de manera pública.

#### Maintainability
* **Obligatorio:** El sistema debe diseñarse con la arquitectura en 3 capas.
* **Obligatorio:** El sistema debe utilizar control de versiones mediante GIT.
* **Obligatorio:** El sistema debe estar programado en Python 3.8 o superior.

#### Reliability
* El sistema debe manejar de manera controlada las desconexiones a internet o las caídas de la API de Yahoo Finance, informando al usuario sin cerrar la aplicación inesperadamente.

#### Scalability
* La base de datos local debe poder manejar el crecimiento del historial de transacciones del usuario sin degradar los tiempos de respuesta de la interfaz.

#### Performance
* **Obligatorio:** El sistema debe funcionar en un equipo hogareño estándar.

#### Reusability
* La lógica de validación financiera y consumo de APIs (Capa de Negocio) debe estar completamente desacoplada de la interfaz gráfica para permitir su reutilización.

#### Flexibility
* **Obligatorio:** El sistema debe utilizar una base de datos SQL o NoSQL.

---

## Stack Tecnológico

### Capa de Datos
* **Tecnología:** Base de Datos SQL (SQLite 3) mediante el módulo database.py.
* **Justificación:** Se escogió SQLite porque es un motor relacional extremadamente ligero que guarda todos los datos en un archivo local `.db`. Esto cumple con el requerimiento de funcionar en un equipo hogareño estándar sin necesidad de configurar ni levantar servidores externos. Las noticias, al ser volátiles, no se persistirán, pero el catálogo de activos se enriquecerá con el perfil de cada empresa.

### Capa de Negocio
* **Tecnología:** Python (Core).
* **Librerías / APIs:** Librería externa `yfinance`.
* **Justificación:** Se utilizó `yfinance` porque provee un puente directo, estable y gratuito hacia la API de Yahoo Finance. Permite descargar datos de mercado en tiempo real, así como extraer el perfil corporativo (`info`) y los titulares de noticias (`news`) devolviendo estructuras de datos fáciles de procesar en Python, agilizando el desarrollo sin exponer credenciales ni gestionar tokens de autenticación complejos.

### Capa de Presentación
* **Tecnología:** Interfaz Web con HTML/JS y framework `Flask` en el backend. Gráficos mediante librerías web (ej. Lightweight Charts o Chart.js).
* **Justificación:** Se eligió una arquitectura web con Flask para permitir que el usuario interactúe con el simulador desde cualquier navegador, ofreciendo una experiencia moderna, responsiva y escalable. Las tecnologías web facilitan la creación de interfaces dinámicas e interactivas, como la visualización en tiempo real de gráficos bursátiles, que son complejas de implementar en frameworks de escritorio tradicionales.
