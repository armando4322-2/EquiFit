import pandas as pd
import pytest

from equifit import config as C
from equifit import data as D
from equifit import metrics as Mt
from equifit import model as M


def test_simulacion_tiene_el_esquema_del_protocolo():
    df = D.simular(n=80)
    for col in C.COLUMNAS_REQUERIDAS + [C.COL_FOLIO, C.COL_OBJETIVO]:
        assert col in df.columns
    assert set(df[C.COL_GENERO]) == set(C.GRUPOS)
    assert df[list(C.LIKERT)].isin([1, 2, 3, 4, 5]).all().all()
    assert df[list(C.COTEJO)].isin([0, 1]).all().all()


def test_regla_objetivo():
    base = D.simular(n=4, semilla=1)[[C.COL_FOLIO] + C.COLUMNAS_REQUERIDAS].copy()
    base[list(C.LIKERT)] = 5
    base[list(C.COTEJO)] = [0, 1, 0]
    base.loc[1, "cuello_corta"] = 1      # falla crítica
    base.loc[2, "likert_comodidad"] = 2  # promedio 3.5 < 4
    out = D.derivar_objetivo(base)
    assert out[C.COL_OBJETIVO].tolist() == [1, 0, 0, 1]


def test_validar_detecta_columnas_faltantes():
    df = D.simular(n=40).drop(columns=["contorno_pecho_cm"])
    with pytest.raises(D.ErrorDatos, match="contorno_pecho_cm"):
        D.validar(df)


def test_validar_normaliza_genero():
    df = D.simular(n=40)
    df[C.COL_GENERO] = df[C.COL_GENERO].map({"Mujer": "F", "Hombre": "masculino"})
    limpio, _ = D.validar(df)
    assert set(limpio[C.COL_GENERO]) == set(C.GRUPOS)


def test_metricas_en_caso_conocido():
    preds = pd.DataFrame({
        C.COL_FOLIO: list("abcdefgh"),
        C.COL_GENERO: ["Mujer"] * 4 + ["Hombre"] * 4,
        "real": [1, 0, 0, 1, 1, 1, 0, 0],
        "pred": [1, 1, 0, 0, 1, 1, 0, 0],
    })
    pg = Mt.metricas_por_grupo(preds)
    assert pg.loc["Mujer", "error"] == 0.5
    assert pg.loc["Mujer", "fpr"] == 0.5
    assert pg.loc["Hombre", "error"] == 0.0
    assert Mt.resumen_equidad(pg)["brecha_error"] == 0.5


def test_a_y_b_comparten_particion_y_difieren_en_variables():
    df = D.simular(n=200)
    exp = M.ejecutar(df)
    assert exp.A.predicciones[C.COL_FOLIO].tolist() == exp.B.predicciones[C.COL_FOLIO].tolist()
    assert set(exp.A.variables) < set(exp.B.variables)
    assert exp.A.modelo.get_params()["max_depth"] == exp.B.modelo.get_params()["max_depth"]


def test_escenario_historico_no_toca_la_prueba():
    df = D.simular(n=200)
    _, test_normal = M.particion(df)
    train_h, test_h = M.particion(df, prop_mujeres_entrenamiento=0.15)
    assert test_normal[C.COL_FOLIO].tolist() == test_h[C.COL_FOLIO].tolist()
    assert (train_h[C.COL_GENERO] == "Mujer").mean() == pytest.approx(0.15, abs=0.03)
