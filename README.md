# Laboratorio de reglas — Polymarket (papel)

Hipótesis: en mercados medianos de Polymarket, el precio tarda en reflejar lo que la **regla escrita** y la **fuente
nombrada** ya determinan. Un lector que verifica regla + fuente cada día puede cobrar esa diferencia.

- Universo diario: mercados que cierran en ≤3 días, volumen ≥ $10k, precio 0.05-0.95, sin deportes, cripto 5-min ni temperatura.
- Marcado: solo si (1) se verificó la fuente nombrada en la regla y (2) dos fuentes independientes; probabilidad propia escrita
  ANTES de mirar más el precio. Si no se puede verificar, no se marca.
- Papel: $100 por caso al mejor ask disponible (+1c). Se espera la resolución; salida anticipada solo si el token toca ≥0.97.
- Corte: 60 casos → real $50-100 por caso si retorno ≥ +10 % por caso con IC95 > 0. 30 casos con < −5 % → cerrar.

Archivos:
- `scan.py` → `candidatos/YYYY-MM-DD.json` (lista del día con regla completa y fuente).
- `registro.csv` → un caso marcado por fila (fecha, id, pregunta, lado, precio, costo, prob_mia, stake, fuentes, razon, …).
- `resolver.py` → cierra casos resueltos, calcula retorno, IC95 y escribe `marcador.md`.
- `diario/YYYY-MM-DD.md` → resumen del día (casos revisados, marcados, descartados y por qué).
