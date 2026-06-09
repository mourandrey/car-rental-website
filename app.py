from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

app = Flask(__name__) #servidor web de flask
app.secret_key = "luxurywheel_secret_key"  #Chave secreta para proteger dados da sessão do usuário
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/projeto_final.db'
db = SQLAlchemy(app) #cursor para a base de dados SQLite

#Criação da tabela usuários coletando os dados necessários
class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    primeiro_nome = db.Column(db.String(100), nullable=False)
    ultimo_nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)


#Criação da tabela de carros com marca, modelo, transmissão, categoria e quantidade (lugares)
class Carro(db.Model):
    __tablename__ = "carros"
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    transmissao = db.Column(db.String(20), nullable=False) #Manual ou Automático
    categoria = db.Column(db.String(50), nullable=False)   #pequeno, médio, grande, SUV ou luxo
    quantidade = db.Column(db.String(20), nullable=False)  #quantidade de lugares(1-4, 5-6 ou 7)
    preco_diaria = db.Column(db.Integer, nullable=False)   #preço de uma diária do carro
    data_legalizacao = db.Column(db.Date)
    data_proxima_revisao = db.Column(db.Date)

with app.app_context():
    db.create_all()

    if not Carro.query.first(): #Verifica os carros existentes para não duplicá-los
        carros = [
            Carro(marca="Mitsubishi",
                  modelo="Pajero Sport",
                  transmissao="automatico",
                  categoria="suv",
                  quantidade="7",
                  preco_diaria=40,
                  data_legalizacao=datetime(2025,6,1).date(),
                  data_proxima_revisao=datetime(2026,8,1).date()),
            Carro(marca="Volkswagen",
                  modelo="Golf Sportsvan",
                  transmissao="manual",
                  categoria="medio",
                  quantidade="5-6",
                  preco_diaria=20,
                  data_legalizacao=datetime(2025,9,15).date(),
                  data_proxima_revisao=datetime(2026,7,20).date()),
            Carro(marca="Rolls Royce",
                  modelo="Ghost",
                  transmissao="automatico",
                  categoria="luxo",
                  quantidade="5-6",
                  preco_diaria=50,
                  data_legalizacao=datetime(2023,1,1).date(),
                  data_proxima_revisao=datetime(2026,10,10).date()),
            Carro(marca="Mitsubishi",
                  modelo="Mirage",
                  transmissao="automatico",
                  categoria="pequeno",
                  quantidade="1-4",
                  preco_diaria=20,
                  data_legalizacao=datetime(2025,3,1).date(),
                  data_proxima_revisao=datetime(2025,12,1).date()),
            Carro(marca="Toyota",
                  modelo="Tacoma",
                  transmissao="manual",
                  categoria="grande",
                  quantidade="5-6",
                  preco_diaria=30,
                  data_legalizacao=datetime(2023,5,1).date(),
                  data_proxima_revisao=datetime(2025,1,1).date())
        ]
        for carro in carros: #Coloca/cria em cada linha os objetos acima criados
            db.session.add(carro)
        db.session.commit()

#Criação da tabela de reservas
class Reserva(db.Model):
    __tablename__ = "reservas"
    id = db.Column(db.Integer, primary_key=True)
    carro_id = db.Column(db.Integer, db.ForeignKey('carros.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="ativa")
    carro_marca = db.Column(db.String(100), nullable=False)
    carro_modelo = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("login.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        #Faz a verificação de usuário
        usuario = Usuario.query.filter_by(email=email).first()

        #Se estiver tudo correto, faz o login na página. Se não, mostra o erro
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            return redirect(url_for('carros'))
        else:
            return render_template('login.html', erro="E-mail ou senha incorretos")
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/registar', methods=['POST'])
def registar():
    #Pega os dados preenchidos nos campos da página register
    primeiro_nome = request.form['primeiro_nome']
    ultimo_nome = request.form['ultimo_nome']
    email = request.form['email']
    senha = request.form['senha']
    senha2 = request.form['senha2']

    # Verifica se as senhas introduzidas são iguais
    if senha != senha2:
        return render_template('register.html',
                               erro="As senhas inseridas devem ser iguais.",
                               primeiro_nome=primeiro_nome,
                               ultimo_nome=ultimo_nome,
                               email=email
                               )

    #Cria hash de senha para garantir a segurança
    senha_hash = generate_password_hash(senha)

    #Criação de novo usuário
    novo_usuario = Usuario(
        primeiro_nome = primeiro_nome,
        ultimo_nome = ultimo_nome,
        email = email,
        senha = senha_hash
    )

    db.session.add(novo_usuario)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/carros')
def carros():
    #Consulta na tabela Carro
    query = Carro.query

    marca = request.args.get('marca')
    categoria = request.args.get('categoria')
    preco_diaria = request.args.get('preco_diaria')
    quantidade = request.args.get('quantidade')

    #Condicional para quando se aplicam os filtros na página
    if marca:
        query = query.filter_by(marca=marca)

    if categoria:
        query = query.filter_by(categoria=categoria)

    if preco_diaria:
        query = query.filter_by(preco_diaria=int(preco_diaria))

    if quantidade:
        query = query.filter_by(quantidade=quantidade)

    carros = query.all()

    #Filtrar disponibilidade pela data de legalização ou data de revisão
    hoje = date.today()
    carros_disponiveis = []

    for carro in carros:
        legalizacao_valida = (hoje - carro.data_legalizacao).days <= 365
        revisao_valida = carro.data_proxima_revisao >= hoje

        if legalizacao_valida and revisao_valida:
            carros_disponiveis.append(carro)

    #Cria uma lista com os modelos de carro para usar o filtro no HTML
    modelos = [carro.modelo for carro in carros_disponiveis]

    return render_template("carros.html", carros=carros_disponiveis, modelos=modelos)


@app.route('/reservas',methods=['GET', 'POST'])
def reservas():
    carro_id = request.args.get('carro_id')
    diaria = request.args.get('diaria')

    #Caso nada seja dado como parâmetro, retorna para a página dos carros, ou seja, mesmo que clique em Reservas, continua na página Carros
    if not carro_id or not diaria:
        return redirect(url_for('carros'))

    carro = Carro.query.get(carro_id)
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    diaria = int(diaria) #Faz com que a string seja convertida para inteiro

    if request.method == 'POST':
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        forma_pagamento = request.form['forma_pagamento']

        #converte para data
        data_de_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        data_do_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()

        if data_do_fim < data_de_inicio:
            erro = "Data final não pode ser anterior à data inicial"
            return render_template('reservas.html', carro=carro, diaria=diaria, erro=erro)

        #Verificação de reserva
        reserva_existente= Reserva.query.filter(Reserva.carro_id == int(carro_id),
                                                Reserva.status == "ativa",
                                                Reserva.data_fim >= data_de_inicio,
                                                Reserva.data_inicio <= data_do_fim
                                                ).first()
        if reserva_existente:
            erro = "Este carro já se encontra reservado."
            return render_template('reservas.html', carro=carro, diaria=diaria, erro=erro)

        #Calcula o valor da diária
        dias = (data_do_fim - data_de_inicio).days + 1
        total = diaria * dias

        #Exemplo de que o usuario com id 1 estaria fazendo a reserva
        usuario_id = session.get('usuario_id')

        nova_reserva = Reserva(carro_id = int(carro_id),
                             usuario_id = usuario_id,
                             data_inicio = data_de_inicio,
                             data_fim = data_do_fim,
                             forma_pagamento = forma_pagamento,
                             valor_total = total,
                             status = "ativa",
                             carro_marca=carro.marca,
                             carro_modelo=carro.modelo
                             )
        db.session.add(nova_reserva)
        db.session.commit()

        reservado = f'Reserva efetuada. Total: €{total}'
        return render_template('reservas.html', carro=carro, diaria=diaria,
                               total=total, reservado=reservado
                               )
    return render_template('reservas.html', carro=carro, diaria=diaria)


@app.route('/minhas_reservas')
def minhas_reservas():
    #Fazr com que o cliente logado seja identificado
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('login'))

    reservas = Reserva.query.filter_by(usuario_id=usuario_id).all() #Faz menção ao id de usuario que coloquei como 1

    editar_id = request.args.get('editar_id')
    if editar_id:
        editar_id = int(editar_id) #Converte para inteiro

    return render_template('minhas_reservas.html', reservas=reservas, editar_id=editar_id)


@app.route('/salvar_edicao', methods=['POST'])
def salvar_edicao():
    reserva_id = request.form.get('reserva_id')
    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')

    reserva = Reserva.query.get(reserva_id)
    #Alterar as datas de reserva
    if reserva:
        reserva.data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        reserva.data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        db.session.commit()

    return redirect(url_for('minhas_reservas'))


@app.route('/cancelar_reserva', methods=['POST'])
def cancelar_reserva():
    reserva_id = request.form.get('reserva_id')

    reserva = Reserva.query.get(reserva_id)

    #Condicional para modificar o status da reserva
    if reserva:
        reserva.status = "cancelada"
        db.session.commit()

    return redirect(url_for('minhas_reservas'))


@app.route('/contactos')
def contactos():
    return render_template("contactos.html")

if __name__=="__main__":
    app.run(debug=True)