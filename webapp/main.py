from flask import Flask, render_template, request, redirect, url_for, session
import re

from db import DB
from logs import Logs

try:
    app = Flask(__name__)
    db = DB()

    app.secret_key = 'cualquiercosa'

    @app.route('/concienciasonora/login/', methods = ['GET', 'POST'])
    def login():
        """
            def login():
                http://localhost:5000/concienciasonora/login/ - esta es la pagina LOGIN, se implementa GET y POST requests
        """  

        # Mensaje de salida que visualiza el usuario
        msg = ''

        # Chequear si "username" y "password" POST requests existen (submitted form)
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            # Crear variables de rapido acceso
            username = request.form['username']
            password = request.form['password']
            
            # Consultar si existe la cuenta - MySQL            
            qi = 'SELECT * FROM cuentas WHERE username = %s AND password = %s'
            values = (username, password)
            account = db.getWhere(qi,values)
            if account:
                # Si la cuenta existe crear una sesion que puede ser accedida desde otras rutas
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                # redirijo a home.html
                return redirect(url_for('home'))
            else:
                # Si la cuenta no existe o username/password son incorrectos
                msg = 'Usuario o contraseña incorrecta'

        # Mostrar el mensaje resultante
        return render_template('index.html', msg=msg)
    
    @app.route('/concienciasonora/logout')
    def logout():
        """
            def login():
                http://localhost:5000/concienciasonora/logout - esta es la pagina LOGOUT
        """  

        # Eliminar session data
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)

        # # redirijo a index.html
        return redirect(url_for('login'))    
    
    @app.route('/concienciasonora/register', methods=['GET', 'POST'])
    def register():
        """
            def login():
                http://localhost:5000/concienciasonora/register/ - esta es la pagina REGISTER, se implementa GET y POST requests
        """  

        # Mensaje de salida que visualiza el usuario
        msg = ''

        # Chequear si "username" y "password" POST requests existen (submitted form)
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            # Crear variables de rapido acceso  
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            
            # Consultar si existe la cuenta - MySQL            
            qi = 'SELECT * FROM cuentas WHERE username = %s'
            values = (username,)
            account = db.getWhere(qi,values)
            
            # Si la cuenta existe chequear errores y validar datos ingresados
            if account:
                msg = 'La cuenta ya existe!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Email invalido!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'El usuario solo debe contener caracteres y números!'
            elif not username or not password or not email:
                msg = 'Por favor completar el formulario!'
            else:
                # Si la cuenta no existe y los datos son validos, insertar una nueva cuenta en la tabla
                qi = 'INSERT INTO cuentas VALUES (NULL, %s, %s, %s)'
                values = (username, password, email)
                account = db.insert(qi,values)
                msg = 'Su usuario fue registrado exitosamente!'

        elif request.method == 'POST':
            # si el formulario esta vacio... (no POST data)
            msg = 'Por favor completar el formulario!'

        # Mostrar el mensaje resultante
        return render_template('register.html', msg=msg)

    # http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
    @app.route('/concienciasonora/home')
    def home():
        # Check if user is loggedin
        if 'loggedin' in session:
            # User is loggedin show them the home page
            return render_template('home.html', username=session['username'])
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))

    # http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
    @app.route('/concienciasonora/profile')
    def profile():
        # Check if user is loggedin
        if 'loggedin' in session:
            # We need all the account info for the user so we can display it on the profile page

            qi = 'SELECT * FROM cuentas WHERE id = %s'
            values = (session['id'],)
            account = db.getWhere(qi,values)
            print(account)
            # Show the profile page with account info
            return render_template('profile.html', account=account)
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))
    
    # con host='0.0.0.0', se puede acceder desde cualquier cliente externo, a la direccion del equipo que se ejecuta el servidor flask
    app.run(host='0.0.0.0', port=5000, debug=True)

except Exception as e:
    logs = Logs()
    logs.appendFile(e)   
    print(e)