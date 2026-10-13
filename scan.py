"""
scan.py — Laboratorio de reglas de Polymarket (papel). Lista mercados candidatos a verificación por regla + fuente.
Criterios: cierran en los próximos DIAS días, volumen ≥ VOL_MIN, precio YES entre 0.05 y 0.95, sin deportes/cripto-5min/
temperatura. Escribe candidatos/YYYY-MM-DD_ciego.json (pregunta, regla completa, fuente nombrada, cierre, volumen; SIN precios)
y candidatos/YYYY-MM-DD.json (lo mismo más p_yes, bid, ask, spread). El lector verifica con el ciego y recién después abre el otro.
Uso: python scan.py [DIAS=3] [VOL_MIN=10000]
"""
import json, re, sys, time, datetime as dt
from pathlib import Path
from urllib.request import urlopen, Request
DIAS = int(sys.argv[1]) if len(sys.argv) > 1 else 3; VOL_MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
def jget(u, tries=3):
    for i in range(tries):
        try: return json.loads(urlopen(Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40).read().decode())
        except Exception: time.sleep(2 * (i + 1))
    return None
hoy = dt.datetime.now(dt.timezone.utc); rows = []; seen = set()
for k in range(0, DIAS + 1):
    d0 = (hoy + dt.timedelta(days=k)).strftime("%Y-%m-%d"); d1 = (hoy + dt.timedelta(days=k + 1)).strftime("%Y-%m-%d")
    for off in range(0, 2000, 100):
        ms = jget(f"https://gamma-api.polymarket.com/markets?closed=false&limit=100&offset={off}&volume_num_min={VOL_MIN}&end_date_min={d0}T00:00:00Z&end_date_max={d1}T00:00:00Z")
        if not ms: break
        for m in ms:
            q = m.get("question") or ""; ft = m.get("feeType") or ""
            if m["id"] in seen or "sport" in ft or "crypto" in ft or re.search(r"up or down|\bvs\.?\b|temperature|win on 20|\bO/U\b", q, re.I): continue
            try: p = float(json.loads(m.get("outcomePrices") or "[0]")[0]); toks = json.loads(m.get("clobTokenIds") or "[]")
            except Exception: continue
            if not (0.05 <= p <= 0.95): continue
            seen.add(m["id"])
            rows.append({"id": m["id"], "conditionId": m.get("conditionId"), "slug": m.get("slug"), "q": q, "p_yes": round(p, 3), "bid": m.get("bestBid"), "ask": m.get("bestAsk"),
                         "spread": m.get("spread"), "liq": round(float(m.get("liquidityNum") or 0)), "vol": round(float(m.get("volumeNum") or 0)), "end": m.get("endDate"), "feeType": ft,
                         "resolutionSource": m.get("resolutionSource") or "", "rules": (m.get("description") or "").strip(), "event": (m.get("events") or [{}])[0].get("title") if m.get("events") else None, "tok_yes": toks[0] if toks else None})
        if len(ms) < 100: break
        time.sleep(0.1)
rows.sort(key=lambda r: (r["end"], -r["vol"]))
Path("candidatos").mkdir(exist_ok=True); out = Path("candidatos") / f"{hoy:%Y-%m-%d}.json"; out_ciego = Path("candidatos") / f"{hoy:%Y-%m-%d}_ciego.json"
json.dump({"generado": hoy.strftime("%Y-%m-%d %H:%M UTC"), "n": len(rows), "mercados": rows}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# Versión CIEGA (sin precio, bid, ask ni spread): es la única que el lector abre mientras escribe sus probabilidades.
CIEGO = ["id", "slug", "q", "event", "end", "vol", "liq", "resolutionSource", "rules"]
json.dump({"generado": hoy.strftime("%Y-%m-%d %H:%M UTC"), "n": len(rows), "mercados": [{k: r[k] for k in CIEGO} for r in rows]}, open(out_ciego, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(rows)} candidatos → {out_ciego} (ciego, para verificar) y {out} (con precios, solo para marcar)")
for r in rows: print(f"[{r['id']}] {r['end'][:16]} vol={r['vol']:,} liq={r['liq']:,} | {r['q'][:100]}")
