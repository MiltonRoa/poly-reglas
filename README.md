# ⚰️ CERRADO 15/10/2026 — Laboratorio de reglas Polymarket (papel)

**Resultado (3 días, 11 casos, 10 resueltos):** nivel A 0/6 (−$600, −100 %/caso); nivel B 2/4 (−$66). Total −$666 de $900.
**PUB: 0 de 11.** El mecanismo (dato ya publicado en la fuente + precio atrasado) nunca apareció en ~18 corridas; todo lo marcado fue proyección.
**Calibración:** el lector esperaba 54 % de aciertos y tuvo 20 %; el mercado implicaba 36 %. El lector es peor que el mercado.
**Salidas:** vender a 0.80/0.90/0.97 = −$694/−$681/−$671 vs esperar −$666. Ninguna ayuda.
Rutina apagada. $0 reales. Lápida 135 en LIBRETA_HIPOTESIS.md. Lo de abajo queda como documentación.

---

# Laboratorio de reglas — Polymarket (papel)

Hipótesis: en mercados medianos de Polymarket, el precio tarda en reflejar lo que la **regla escrita** y la **fuente
nombrada** ya determinan. Un lector que verifica regla + fuente seis veces por día puede cobrar esa diferencia.

- Universo por corrida: mercados que cierran en ≤2 días, volumen ≥ $5k, precio 0.05-0.95, sin deportes, cripto 5-min ni temperatura.
- Verificación A CIEGAS: el lector trabaja con `candidatos/FECHA_ciego.json` (sin precios), escribe su probabilidad y la razón
  de TODOS los candidatos en el diario, y recién después abre `candidatos/FECHA.json` (con precios) para comparar.
- Marcado: solo si (1) se verificó la fuente nombrada en la regla y (2) dos fuentes independientes. Si no se puede verificar, no se marca.
  - Nivel A ($100): |prob − precio| ≥ 0.15 y ventaja ≥ 15 % sobre el costo.
  - Nivel B ($50): diferencia 0.08-0.15 y ventaja ≥ 8 %. Solo se mide.
  - Tipo PUB: el dato que decide ya estaba publicado en la fuente nombrada (el mecanismo). Tipo PROY: proyección (contadores,
    datos por salir, hechos futuros). Se miden por separado; la decisión de pasar a real se toma sobre nivel A y mira PUB vs PROY.
- Papel: entrada al mejor ask disponible (+1c). Se espera la resolución; salida anticipada solo si el token toca ≥0.97.
- Corte: 60 casos → real $50-100 por caso si retorno ≥ +10 % por caso con IC95 > 0. 30 casos con < −5 % → cerrar.
- PnL siempre en retorno simple sobre el costo.

Archivos:
- `scan.py` → `candidatos/FECHA_ciego.json` (sin precios) y `candidatos/FECHA.json` (con precios).
- `registro.csv` → un caso marcado por fila (fecha, id, pregunta, lado, precio, costo, prob_mia, stake, fuentes, razon, …, tipo).
- `resolver.py` → cierra casos resueltos, calcula retorno simple, IC95 bootstrap y escribe `marcador.md` por nivel y por tipo.
- `diario/FECHA.md` → una sección por corrida: tabla de probabilidades a ciegas, marcados, descartados y "sin verificar".
