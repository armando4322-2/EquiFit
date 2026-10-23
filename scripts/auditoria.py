"""Auditoría A vs B desde la terminal.

Uso:
    python scripts/auditoria.py                      # datos simulados
    python scripts/auditoria.py datos/campo.csv      # datos reales
    python scripts/auditoria.py --historico 0.15     # escenario con pocas mujeres
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from equifit import analysis as A  # noqa: E402
from equifit import data as D  # noqa: E402
from equifit import model as M  # noqa: E402

p = argparse.ArgumentParser(description="EquiFit: auditoría de sesgo A vs B")
p.add_argument("csv", nargs="?", help="CSV con el esquema de la plantilla (si se omite, usa datos simulados)")
p.add_argument("--repeticiones", type=int, default=20)
p.add_argument("--historico", type=float, default=None, help="Proporción de mujeres en el entrenamiento (0–1)")
args = p.parse_args()

if args.csv:
    df, avisos = D.validar(D.leer_csv(args.csv))
    for a in avisos:
        print("Aviso:", a)
    print(f"Datos reales: {len(df)} participantes")
else:
    df = D.simular()
    print(f"Datos SIMULADOS: {len(df)} participantes (no son resultados del proyecto)")

print("\nPregunta descriptiva")
print(A.descriptiva(df).round(2).to_string())

cor = A.correlacion(df)
print(f"\nPregunta correlacional: {cor['metodo']} r = {cor['r']:.3f} (p = {cor['p']:.2g}), {A.interpretar_r(cor['r'])}")

print(f"\nPregunta experimental: {args.repeticiones} repeticiones pareadas")
res = M.resumir_repetido(M.ejecutar_repetido(df, args.repeticiones, args.historico))
print(res[["A_media", "B_media", "B_mejor_pct"]].round(3).to_string())
