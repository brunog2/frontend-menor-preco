from model.user import User
from flask import Flask, render_template, request, jsonify, redirect, url_for
from controller.user_controller import user_controller
from database import db
from flask_login import login_user, logout_user
from login.login_manager import login_manager
from flask_login import current_user
import requests
import json
import os 
import math

TEMPLATE = './templates'
STATIC = './static'

app = Flask(__name__, static_url_path='', template_folder=TEMPLATE, static_folder=STATIC)
app.register_blueprint(user_controller)

login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./dbtest.db'
db.init_app(app)

app.secret_key = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'

with app.app_context():
  db.create_all()

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

productsOnCart = []
cartLength = 0
latitudeUsuario = -9.6432331
longitudeUsuario = -35.7190686

@app.route("/")
def login():  
  return render_template('index.html')
  
  #if not hasattr(current_user, 'id'):
  #  return render_template("login.html")
  #else:
  #  return render_template("index.html")


@app.route("/products", methods=['GET', 'POST'])
def products():
  global latitudeUsuario
  global longitudeUsuario

  if request.method == "POST":
    pass

  else:
    newProducts = []
    print("as coordenadas do usuário: ", request.args.get("latitudeUsuario"), request.args.get("longitudeUsuario"))
    print("as coordenadas do usuário: ", latitudeUsuario, longitudeUsuario)
    #page = request.args.get('page', 1)
    
    productDescription = request.args.get('q')
    latitudeUsuario = request.args.get("latitudeUsuario")
    longitudeUsuario = request.args.get("longitudeUsuario")
    print("descricao do produto: ", productDescription)
    url = "http://api.sefaz.al.gov.br/sfz_nfce_api/api/public/consultarPrecosPorDescricao"
    header = {"appToken": "7be9c184660a004d6ec383b11c50e16b02981bd0"}
    payload = {"descricao": productDescription,"dias": 1,"latitude": latitudeUsuario,"longitude": longitudeUsuario,"raio": 15}
    response = requests.post(url, headers=header, json=payload)

    products = response.json()

    productsDescriptions = []
    productsCodes = []

    for product in products:
      print("o código é: ", product["codGetin"])
      #if product["dscProduto"].lower() in productsDescriptions and product["codGetin"] not in productsCodes:
      #  for productVerification in newProducts:
      #    if productVerification["dscProduto"] == product["dscProduto"]:
      #      productVerification["codsGetin"].append(product["codGetin"])
      #      productsCodes.append(product["codGetin"])

      # or product["dscProduto"] in productsDescriptions
      # erro conhecido: alguns códigos de barras começam por 1 e precisam desse número antes para a consulta na api, 

      if product["codGetin"] == None or product["codGetin"] == "" or product["codGetin"].upper() == "SEM GTIN" or product["codGetin"][-13:] in productsCodes:
        continue

      else:
        productsDescriptions.append(product["dscProduto"].lower())
        print("na posicao 0: ", product["codGetin"][0])
        newProduct = {}
        if product["codGetin"][0] == '0':
          print("entrou no if ", product["codGetin"])
          productsCodes.append(product["codGetin"][-13:])
          newProduct = {"dscProduto": product["dscProduto"], "codGetin": product["codGetin"][-13:]}
        else:
          print("entrou no else ", product["codGetin"])
          productsCodes.append(product["codGetin"])
          newProduct = {"dscProduto": product["dscProduto"], "codGetin": product["codGetin"]}
        
        newProducts.append(newProduct)

    #print("codigos do produto: ", productsCodes)
    #print("nomes do produto: ", productsDescriptions)
    #print("os novos produtos: ", newProducts)
    return render_template('products.html', products=newProducts, searchText=productDescription, latitudeUsuario=latitudeUsuario, longitudeUsuario=longitudeUsuario)

  

  
  #if not hasattr(current_user, 'id'):
  #  return render_template("login.html")
  #else:
  #  return render_template("index.html")


@app.route("/addToCart", methods=['POST'])
def addToCart():
  global productsOnCart  
  global cartLength
  dscProduto = request.form["dscProduto"]
  codGetin = request.form["codGetin"]
  newProduct = {"dscProduto": dscProduto, "codGetin": codGetin, "qtd": 1}
  productsOnCart.append(newProduct)
  cartLength += 1
  print("carrinho: ", productsOnCart)
  return ("", 204)

@app.route("/cart", methods=['GET'])
def cart():
  global productsOnCart
  global cartLength
  
  return render_template('cart.html', products=productsOnCart, cartLength=cartLength)

@app.route("/subQtProduct", methods=['POST'])
def subQtProduct():
  global cartLength
  codGetin = request.form["codGetin"]

  print("o codigo é ", codGetin)
  for product in productsOnCart:
    if product["codGetin"] == codGetin:
      if product["qtd"] != 1:
        product["qtd"] -= 1
        cartLength -= 1
        return redirect(url_for('cart'))
      else:
        return ("", 204)
      break

@app.route("/addQtProduct", methods=['POST'])
def addQtProduct():
  global cartLength
  codGetin = request.form["codGetin"]

  print("o codigo é ", codGetin)
  for product in productsOnCart:
    if product["codGetin"] == codGetin:
      product["qtd"] += 1
      cartLength += 1
      return redirect(url_for('cart'))
      break


@app.route("/deleteProduct", methods=['POST'])
def deleteProduct():
  global productsOnCart
  print("chegou pra excluir")
  codGetin = request.form["codCard"]
  print("removendo produto com o código: ", codGetin)

  for product in productsOnCart:
    if product["codGetin"] == codGetin:
      productsOnCart.remove(product)
      break

  print(productsOnCart)
  return render_template("cart.html", products=productsOnCart)










def calculate_distance(latitudeEstabelecimento, longitudeEstabelecimento, latitudeUsuario, longitudeUsuario):
    result = 0
    
    lat1 = int(latitudeEstabelecimento)
    lng1 = int(longitudeEstabelecimento)

    lat2 = int(latitudeUsuario)
    lng2 = int(longitudeUsuario)

    print("as coordenadas: \n usuario: {}, {} \n estabelecimento: {}, {}".format(lat2, lng2, lat1, lng1))

    degreesToRadians = (math.pi / 180)
    latrad1 = lat1 * degreesToRadians
    latrad2 = lat2 * degreesToRadians
    dlat = (lat2 - lat1) * degreesToRadians
    dlng = (lng2 - lng1) * degreesToRadians

    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(latrad1) * \
    math.cos(latrad2) * math.sin(dlng / 2) * math.sin(dlng / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    r = 6371000

    result = (r * c)

    return (result / 1000)  # Converting from m to km


@app.route("/searchMarket", methods=['POST'])
def searchMarket():
  global latitudeUsuario
  global longitudeUsuario

  # print("produtos a procurar: ", productsOnCart)
  codsBarras = []
  
  #adicionar apenas os códigos de barras em uma lista
  for produto in productsOnCart:
    codsBarras.append({"codBarras": produto['codGetin'], "cnpjs": []})

  #adicionar todos os cnpjs que vendem o produto com aquele codigo de barras
  for cod in codsBarras:
    # print("o código de barras:", cod["codBarras"])
    url = "http://api.sefaz.al.gov.br/sfz_nfce_api/api/public/consultarPrecosPorCodigoDeBarras"
    header = {"appToken": "7be9c184660a004d6ec383b11c50e16b02981bd0"}
    payload = {"codigoDeBarras": cod["codBarras"], "dias": 1,"latitude": latitudeUsuario,"longitude": longitudeUsuario,"raio": 15}
    response = requests.post(url, headers=header, json=payload)
    
    # lista de objetos
    estabelecimentos = response.json()

    for estabelecimento in estabelecimentos:
      latitudeEstabelecimento = estabelecimento["numLatitude"]
      longitudeEstabelecimento = estabelecimento["numLongitude"]
      distanciaUsuarioEstabelecimento = calculate_distance(latitudeEstabelecimento, longitudeEstabelecimento, latitudeUsuario, longitudeUsuario)

      if distanciaUsuarioEstabelecimento <= 15:
        cnpj = estabelecimento["numCNPJ"]
        cod["cnpjs"].append(cnpj)
      else: 
        continue


  # verificar os cnpjs que vendem TODOS os produtos da lista
  # percorrer todos os cnpjs em "cnpjs" de codBarras
  # verificar se cada um dos cpnjs está em cada um dos codBarras
  # se não estiver em pelo menos um, remover da lista
  # codbarras = [{"cod": 148418, "cpnjs": [1,2,3]}, {}]
  # cnpjTodosProdutos = [{"cpnj": cpnj, "cods": [{"cod": cod, "dscProduto": productsOnCart["dscProduto"], "preco": preco}], "precoTotal": precoTotal}]

  def isOnList(item, array):
    if item in array:
      return True
    else:
      return False

  def sellAllProducts(cnpj, index = 0):
    if isOnList(cnpj, codsBarras[index]["cnpjs"]):
      if index == len(codsBarras)-1:
        return True
      else: 
        return sellAllProducts(cnpj, index+1)
    else:
      return False


  print("os códgos de barras: ", codsBarras)

  cnpjsTodosProdutos = []
  for codBarras in codsBarras:
    print("os cnpjs que vendem {}: {}".format(codBarras["codBarras"], codBarras["cnpjs"]))
    for cnpj in codBarras["cnpjs"]:
      if sellAllProducts(cnpj):
        cnpjsTodosProdutos.append({"cnpj": cnpj, "marketName": "", "latitude": 0, "longitude": 0, "codsBarras": [], "precoTotal": 0})
  

  #consultar os preços dos produtos em cada cnpj
  print("cnpjs todos os produtos: ", cnpjsTodosProdutos)
  for cnpj in cnpjsTodosProdutos:
    cnpj["precoTotal"] = 0
    for cod in codsBarras:
      url = "http://api.sefaz.al.gov.br/sfz_nfce_api/api/public/consultarPrecoProdutoEmEstabelecimento"
      header = {"appToken": "7be9c184660a004d6ec383b11c50e16b02981bd0"}
      payload = {"codigoBarras": cod["codBarras"], "cnpj": cnpj["cnpj"], "quantidadeDeDias": 3}
      response = requests.post(url, headers=header, json=payload)
      dscProduto = response.json()["dscProduto"]
      marketName = response.json()["nomFantasia"]
      latitude = response.json()["numLatitude"]
      longitude = response.json()["numLongitude"]
      logradouro = response.json()["nomLogradouro"]
      numImovel = response.json()["numImovel"]
      print("nome do mercado: ", marketName)
      if marketName == None:
        marketName = response.json()["nomRazaoSocial"]
  
      preco = response.json()["valUnitarioUltimaVenda"]
      cnpj["codsBarras"].append({"cod": cod["codBarras"], "dscProduto": dscProduto, "preco": preco})
      cnpj["precoTotal"] += preco
      cnpj["marketName"] = marketName
      cnpj["latitude"] = latitude
      cnpj["longitude"] = longitude
      cnpj["logradouro"] = logradouro
      cnpj["numImovel"] = numImovel
      # cnpjTodosProdutos = [{cnpj: [{"cod": cod, "dscProduto": productsOnCart["dscProduto"], "preco": preco}], precoTotal: 15}]

  print("passou da parte de verificar cada preco em todos os estabelecimentos")
  print("novo cnpjsTodosProdutos: ", cnpjsTodosProdutos)

  # ordenar a lista em ordem crescente de preco total
  def myFunc(e):
    return e['precoTotal']

  cnpjsTodosProdutos.sort(key=myFunc)

  print("\n \n cnpjsTodosProdutos em ordem de preco crescente: ", cnpjsTodosProdutos)

  # return jsonify(cnpjsTodosProdutos[:10])
  return render_template('markets.html', markets=cnpjsTodosProdutos)













@app.route("/login", methods=['POST'])
def home():
  error = None
  if request.method == 'POST':
    users = User.query.filter_by(email=request.form['email'])
    if not users.first() == None:
      user = users.first()
      if user.password == request.form['password']:
        login_user(user, remember=True)
        return render_template('index.html') 
      else:
        error = 'Invalid Credentials. Please try again.'
    else:
      error = 'Invalid Credentials. Please try again.'
  return render_template('login.html', error=error)

@app.route("/register", methods=['GET', 'POST'])
def register ():
  if request.method == 'GET':
    return render_template('register.html')
  else: 
    pass

@app.route("/logout", methods=['GET'])
def logout():
  logout_user()
  return render_template('login.html')



app.run()