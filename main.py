from flask import Flask, render_template, request, flash
import pandas as pd

app = Flask(__name__)
app.secret_key = "mysecretkey"


def validar_formato_fecha(fecha):
    try:
        if fecha != pd.to_datetime(fecha, format="%Y-%m-%d %H:%M:%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        ):
            return False
        else:
            return True
    except ValueError:
        return False


def validar_identificacion(id):
    return len(str(id)) <= 21


def validar_resultado_maquina(resultado):
    valid_results = [
        "ABANDON",
        "NO-ANSWER",
        "FAILED",
        "NORMAL_CLEARING",
        "CALL_REJECTED",
        "ANSWER-MACHINE-MSG",
    ]
    return resultado in valid_results


def validar_telefono(telefono):
    return len(str(telefono)) <= 10


def validar_operador(operador):
    valid_operators = [
        "PyA",
        "CDC_2",
        "PyA_2",
        "DIGITAL",
        "PISCINA",
        "AYS_BB7",
        "QNT_BB5",
        "QNT_JUD",
        "PAZ_SALVO",
        "QNT_RBK_1",
        "QNT_RBK_2",
        "QNT_RBK_3",
        "QNT_RBK_4",
        "CX_BB5_JUD",
        "CDC_DIGITAL",
        "Masssolution",
        "NEXTDATA_BB7",
        "QNT_RECAUDO_3",
        "PISCINA_COMITE",
        "STUDIO_ABOGADO",
        "QNT_RECAUDO_1_2",
        "NEXTDATA_BB5_JUD",
        "MANTENIMIENTO-QNT",
        "OPERACIONES_INTERNO",
        "DIGITAL_MONTOS_BAJOS",
        "MANTENIMIENTO-ESP-QNT",
        "MANTENIMIENTO_DIGITAL",
        "MANTENIMIENTO_TDC_PyS",
        "MANTENIMIENTO_REVISION",
        "MANTENIMIENTO_TDC_OPERACIONES",
    ]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["file"]
        df = pd.read_excel(file)
        errores = []

        for i, row in df.iterrows():
            if not validar_formato_fecha(str(row["fecha"])):
                errores.append((i, "fecha", row["fecha"]))
            if not validar_identificacion(row["Identificacion"]):
                errores.append((i, "Identificacion", row["Identificacion"]))
            if not validar_resultado_maquina(row["resultado_maquina"]):
                errores.append((i, "resultado_maquina", row["resultado_maquina"]))
            if not validar_telefono(row["telefono"]):
                errores.append((i, "telefono", row["telefono"]))
            if not validar_operador(row["operado_por"]):
                errores.append((i, "operado_por", row["operado_por"]))

        if errores:
            for error in errores:
                flash(
                    (
                        "danger",
                        f"Fila: {error[0]+2}, campo: {error[1]}, valor: {error[2]}",
                    )
                )
        else:
            flash(("success", "Todos los datos son correctos."))

    except Exception as e:
        flash(f"Error: {str(e)}")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
