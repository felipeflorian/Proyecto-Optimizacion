import flask
from flask import Flask, redirect, url_for, request, render_template
import pandas, pulp
from tabulate import tabulate

""" Creacion aplicacion """

app = flask.Flask(__name__)
app.config["DEBUG"] = True

""" Lectura data_sets en formata .csv separado por punto y coma"""

dataset_jumbo = rutas = pandas.read_csv("jumbo.csv", sep=";", encoding="latin1").fillna("-")
dataset_exito = rutas2 = pandas.read_csv("exito.csv", sep=";", encoding="latin1").fillna("-")
dataset_d1 = rutas3 = pandas.read_csv("d1.csv", sep=";", encoding="latin1").fillna("-")
dataset_carulla = rutas4 = pandas.read_csv("carulla.csv", sep=";", encoding="latin1").fillna("-")

def construir_listas(dataset):
    productos = []
    producto_marca = []
    costos_asociados = {}
    cantidades_asociadas = {}
    for index, row in dataset.iterrows():
        producto = row["nombre"]
        producto = producto.replace(" ", "_")
        marca = row["marca"]
        marca = marca.replace(" ", "_")
        precio = row["precio"]
        cantidad = row["cantidad"]
        if producto not in productos:
            productos.append(str(producto))
        nombre_total = producto+"_"+marca+"_"+str(cantidad)
        producto_marca.append(nombre_total)
        costos_asociados[nombre_total] = precio
        cantidades_asociadas[nombre_total] = cantidad
    return productos, producto_marca, costos_asociados, cantidades_asociadas


def opti(solicitud,productos,producto_marca,costos_asociados,cantidades_asociadas):
    marca = pulp.LpProblem("Problema Canasta Familiar en el Éxito", pulp.LpMinimize)
    variables_decision = pulp.LpVariable.dicts("BuyProduct", producto_marca, 0, cat="Integer")
    terminosFuncionCosto = []
    for prod in producto_marca:
        terminosFuncionCosto.append(costos_asociados[prod]*variables_decision[prod])
    marca += pulp.lpSum(terminosFuncionCosto)
    for prod in solicitud.keys():
        possible_prods = []
        for possible in producto_marca:
            if prod == possible[0:len(prod)]:
                possible_prods.append(possible)
        marca += pulp.lpSum([cantidades_asociadas[p]*variables_decision[p]for p in possible_prods]) >= solicitud[prod]
    status = marca.solve()
    print("La lista de compra es: ")
    print(solicitud)
    print("El problema es: ")
    print(pulp.LpStatus[status])
    print("Debe comprar: ")
    total = 0
    for var in marca.variables():
        if var.varValue > 0:
            compra = var.name.replace("BuyProduct_", "")
            total += costos_asociados[compra]*var.varValue
            print(var.varValue, "unidades de", compra)
    print("Su total es:", total)
    return total, marca


@app.route("/",methods=["GET"])
def home():
    return render_template("inicio.html")

@app.route("/jumbo",methods=["GET"])
def solicitud_jumbo():
    return app.send_static_file("jumbo.html")


@app.route("/resultadoJumbo",methods=["POST","GET"])
def opti_jumbo():
    productos, producto_marca, costos_asociados, cantidades_asociadas = construir_listas(dataset_jumbo)
    solicitud = {}
    for p in productos:
        valor = request.values.get(p)
        if valor != "":
            solicitud[p] = int(valor)
            print(valor)
    tot, exito = opti(solicitud, productos, producto_marca,costos_asociados, cantidades_asociadas)
    strng = "Debe comprar: <br/>"
    for var in exito.variables():
        if var.varValue > 0:
            compra = var.name.replace("BuyProduct_","")
            precio = var.varValue*costos_asociados[compra]
            strng += str(var.varValue) + " unidades de " + compra +" con precio "+str(precio)+" (cada uno "+str(costos_asociados[compra])+") <br/>"
    strng += "Para un total de "+str(tot) +" <br/>"
    strng += "<a href = \"http://localhost:5000/\" > Inicio </a>"
    return strng

@app.route("/exito",methods=["GET"])
def solicitud_exito():
    return app.send_static_file("exito.html")

@app.route("/resultadoExito",methods=["POST","GET"])
def opti_exito():
    productos, producto_marca, costos_asociados, cantidades_asociadas = construir_listas(dataset_exito)
    solicitud = {}
    print(productos)
    for p in productos:
        valor = request.values.get(p)
        if valor != "":
            print(p, type(valor))
            solicitud[p] = int(valor)
            #print(valor)
    tot, exito = opti(solicitud, productos, producto_marca,costos_asociados, cantidades_asociadas)
    print(tot)
    strng = "Debe comprar: <br/>"
    for var in exito.variables():
        if var.varValue > 0:
            compra = var.name.replace("BuyProduct_","")
            precio = var.varValue*costos_asociados[compra]
            strng += str(var.varValue) + " unidades de " + compra +" con precio "+str(precio)+" (cada uno "+str(costos_asociados[compra])+") <br/>"
    strng += "Para un total de "+str(tot) +" <br/>"
    strng += "<a href = \"http://localhost:5000/\" > Inicio </a>"
    return strng

@app.route("/D1",methods=["GET"])
def solicitud_d1():
    return app.send_static_file("d1.html")

@app.route("/resultadoD1",methods=["POST","GET"])
def opti_d1():
    productos, producto_marca, costos_asociados, cantidades_asociadas = construir_listas(dataset_d1)
    solicitud = {}
    print(productos)
    for p in productos:
        print(p)
        valor = request.values.get(p)
        print(valor)
        if valor != "" and valor != None:
            print(p, type(valor))
            solicitud[p] = int(valor)
            #print(valor)
    tot, d1 = opti(solicitud, productos, producto_marca,costos_asociados, cantidades_asociadas)
    print(tot)
    strng = "Debe comprar: <br/>"
    for var in d1.variables():
        if var.varValue > 0:
            compra = var.name.replace("BuyProduct_","")
            precio = var.varValue*costos_asociados[compra]
            strng += str(var.varValue) + " unidades de " + compra +" con precio "+str(precio)+" (cada uno "+str(costos_asociados[compra])+") <br/>"
    strng += "Para un total de "+str(tot) +" <br/>"
    strng += "<a href = \"http://localhost:5000/\" > Inicio </a>"
    return strng

@app.route("/carulla",methods=["GET"])
def solicitud_carulla():
    return app.send_static_file("carulla.html")


@app.route("/resultadoCarulla",methods=["POST","GET"])
def opti_carulla():
    productos, producto_marca, costos_asociados, cantidades_asociadas = construir_listas(dataset_carulla)
    solicitud = {}
    for p in productos:
        valor = request.values.get(p)
        if valor != "":
            print(p, type(valor))
            solicitud[p] = int(valor)
            #print(valor)
    tot, carulla = opti(solicitud, productos, producto_marca,costos_asociados, cantidades_asociadas)
    strng = "Debe comprar: <br/>"
    for var in carulla.variables():
        if var.varValue > 0:
            compra = var.name.replace("BuyProduct_","")
            precio = var.varValue*costos_asociados[compra]
            strng += str(var.varValue) + " unidades de " + compra +" con precio "+str(precio)+" (cada uno "+str(costos_asociados[compra])+") <br/>"
    strng += "Para un total de "+str(tot) +" <br/>"
    strng += "<a href = \"http://localhost:5000/\" > Inicio </a>"
    return strng



app.run()
