from flask import Flask, render_template, request
from barril.units import Scalar
from calculos.rotor import calcular_rotor

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    resultados = None
    erro = None

    if request.method == "POST":
        try:
            V_dot = Scalar(float(request.form["V_dot"]), request.form["V_dot_unidade"])
            H = Scalar(float(request.form["H"]), request.form["H_unidade"])
            N = Scalar(float(request.form["N"]), request.form["N_unidade"])

            configuracao_rotor = request.form["configuracao_rotor"]
            Estagios = request.form["Estagios"]
            tipo_rotor = request.form["tipo_rotor"]
            tipo_difusor = request.form["tipo_difusor"]

            resultados = calcular_rotor(V_dot, H, N, configuracao_rotor, Estagios, tipo_rotor, tipo_difusor)

        except Exception as e:
            erro = str(e)

    return render_template("index.html", resultados=resultados, erro=erro)

if __name__ == "__main__":
    app.run(debug=True)