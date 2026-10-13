"""
resolver.py — Cierra los casos de papel ya resueltos y recalcula el marcador.
Lee registro.csv (una fila por caso marcado), consulta Gamma por id de mercado, y si closed=true anota el resultado
(outcomePrices del lado apostado), el retorno simple sobre el costo y actualiza marcador.md con n, acierto, retorno medio,
IC95 bootstrap por caso y curva acumulada. También registra el precio máximo alcanzado por el token apostado tras la entrada
(para la regla de salida a 0.97). Uso: python resolver.py
"""
import json, csv, time, datetime as dt
from pathlib import Path
from urllib.request import urlopen, Request
import numpy as np
REG = Path("registro.csv"); MARC = Path("marcador.md")
COLS = ["fecha", "id", "pregunta", "lado", "precio_entrada", "costo", "prob_mia", "stake", "fuentes", "razon", "cierre_prev", "estado", "resultado", "retorno", "max_precio", "fecha_resuelto", "tipo"]
# tipo: PUB = el dato que decide el mercado YA está publicado en la fuente nombrada (el mecanismo del laboratorio);
#       PROY = falta que ocurra o se publique algo (contadores, datos por salir, hechos futuros). Se mide aparte.
def jget(u, tries=3):
    for i in range(tries):
        try: return json.loads(urlopen(Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40).read().decode())
        except Exception: time.sleep(2 * (i + 1))
    return None
rows = list(csv.DictReader(open(REG, encoding="utf-8"))) if REG.exists() else []
for r in rows:
    if r.get("estado") == "resuelto": continue
    m = jget(f"https://gamma-api.polymarket.com/markets/{r['id']}")
    if not m: continue
    try: toks = json.loads(m.get("clobTokenIds") or "[]"); pr = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
    except Exception: continue
    idx = 0 if r["lado"].upper() == "YES" else 1
    # precio máximo del token apostado desde la entrada (historial horario)
    try:
        t0 = int(dt.datetime.fromisoformat(r["fecha"]).replace(tzinfo=dt.timezone.utc).timestamp()); t1 = int(time.time())
        h = jget(f"https://clob.polymarket.com/prices-history?market={toks[idx]}&startTs={t0}&endTs={min(t1, t0 + 6*86400)}&fidelity=60") or {}
        mx = max([float(p["p"]) for p in h.get("history", [])] + [float(r.get("max_precio") or 0)])
        r["max_precio"] = f"{mx:.3f}"
    except Exception: pass
    if m.get("closed") and len(pr) == 2 and max(pr) >= 0.99:
        won = 1.0 if pr[idx] > 0.5 else 0.0; cost = float(r["costo"])
        r["resultado"] = "GANA" if won else "PIERDE"; r["retorno"] = f"{(won - cost) / cost:.4f}"; r["estado"] = "resuelto"; r["fecha_resuelto"] = (m.get("closedTime") or "")[:16]
    time.sleep(0.1)
with open(REG, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); [w.writerow({k: r.get(k, "") for k in COLS}) for r in rows]
res = [r for r in rows if r.get("estado") == "resuelto"]; pend = [r for r in rows if r.get("estado") != "resuelto"]
def tier(r):
    try: return "A" if float(r.get("stake") or 100) >= 100 else "B"
    except Exception: return "A"
def tipo(r): return (r.get("tipo") or "PROY").strip().upper()[:4] or "PROY"
def ci(x, n=2000, seed=0):
    x = np.asarray(x, float); rng = np.random.default_rng(seed)
    if len(x) < 5: return (float("nan"), float("nan"))
    b = [rng.choice(x, len(x)).mean() for _ in range(n)]; return (np.percentile(b, 2.5), np.percentile(b, 97.5))
lines = [f"# Marcador — laboratorio de reglas (papel; nivel A = $100, diferencia ≥0.15; nivel B = $50, diferencia 0.08-0.15)", f"Actualizado: {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC", "",
         f"- Casos marcados: {len(rows)} (A {sum(tier(r)=='A' for r in rows)} / B {sum(tier(r)=='B' for r in rows)}; PUB {sum(tipo(r)=='PUB' for r in rows)} / PROY {sum(tipo(r)=='PROY' for r in rows)}) | resueltos: {len(res)} | pendientes: {len(pend)}",
         "- tipo PUB = el dato que decide ya estaba publicado en la fuente nombrada al marcar (el mecanismo del laboratorio); PROY = proyección (contadores, datos por salir, hechos futuros)."]
def resumen(etq, rt):
    r_ = np.array([float(x["retorno"]) for x in rt]); lo, hi = ci(r_); won = np.mean([x["resultado"] == "GANA" for x in rt])
    pnl = (r_ * np.array([float(x["stake"]) for x in rt])).sum()
    return f"- {etq}: n={len(rt)} | acierto {won*100:.0f}% | retorno medio por caso {r_.mean()*100:+.1f}% | IC95 [{lo*100:+.1f}, {hi*100:+.1f}] | PnL papel ${pnl:+.0f}"
for T in ("A", "B"):
    rt = [x for x in res if tier(x) == T]
    if rt: lines.append(resumen(f"NIVEL {T}", rt))
for P in ("PUB", "PROY"):
    rt = [x for x in res if tipo(x) == P]
    if rt: lines.append(resumen(f"TIPO {P}", rt))
for T in ("A", "B"):
    for P in ("PUB", "PROY"):
        rt = [x for x in res if tier(x) == T and tipo(x) == P]
        if rt: lines.append(resumen(f"NIVEL {T} × {P}", rt))
if res:
    lines += [f"- Regla de corte (nivel A): ≥+10% por caso con IC95 > 0 a los 60 casos → real $50-100/caso; < −5% a los 30 casos → cerrar. Nivel B solo se mide.", "",
              "| fecha | nivel | tipo | mercado | lado | entrada | prob mía | resultado | retorno | máx precio |", "|---|---|---|---|---|---|---|---|---|---|"]
    for x in res[-60:]: lines.append(f"| {x['fecha'][:10]} | {tier(x)} | {tipo(x)} | {x['pregunta'][:60]} | {x['lado']} | {x['precio_entrada']} | {x['prob_mia']} | {x['resultado']} | {float(x['retorno'])*100:+.0f}% | {x.get('max_precio','')} |")
if pend:
    lines += ["", "## Pendientes", "| fecha | nivel | tipo | mercado | lado | entrada | prob mía | máx precio | cierre previsto |", "|---|---|---|---|---|---|---|---|---|"]
    for x in pend: lines.append(f"| {x['fecha'][:10]} | {tier(x)} | {tipo(x)} | {x['pregunta'][:60]} | {x['lado']} | {x['precio_entrada']} | {x['prob_mia']} | {x.get('max_precio','')} | {x['cierre_prev'][:10]} |")
MARC.write_text("\n".join(lines), encoding="utf-8"); print("\n".join(lines[:8]))
