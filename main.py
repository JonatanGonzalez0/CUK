from flask import Flask, render_template, request, redirect, session, url_for, flash,jsonify
from datetime import datetime
from Datos.Usuario import Usuario
from Datos.Receta import Receta
from Datos.Post import Post
from os import environ
import json
import base64
import csv

app = Flask(__name__)
app.secret_key = "IngenieriaUsacAdmin"

#usuario maestro y arreglo de usuarios
usuarios = []
usuarioMaestro = Usuario("admin","admin","Usuario", "Maestro",)
usuarios.append(usuarioMaestro)

#Lista de recetas
recetas= []
recetaPrueba = Receta("Jonatan","Sandwitch Americano","Elaboracion de un Sandwitch americano con ingredientes frescos.","Pan , Jamon, Queso, Lechuga, Tomate","En un sartén disponer las lonchas de tocineta cortadas por la mitad y cocinar a fuego bajo hasta que suelten su grasa y queden crocantes. Cuando estén listas pasar por papel absorbente para eliminar el exceso de grasa. Aparte en otro sartén, derretir un poco de mantequilla y añadir las rodajas de pan, dorar por ambos lados. ","20 min","https://www.hogar.mapfre.es/media/2019/02/sandwich-americano.jpg")
recetaPrueba2 = Receta("Admin","PIZZA HAWAIANA","La pizza hawaiana es la opción favorita de muchos, simplemente porque su combinación de piña con jamón es exquisita. Aquí te presentamos una receta muy original para que la prepares en tu casa.","1/2 taza de salsa de jitomate 1 taza de piña cortada en cubos pequeños 1 taza de cubos de jamón pequeños 1 cda. de chile habanero picado finamente 1 cda. de cebolla morada picada finamente 4 cdas. de aceite de oliva 1 taza de queso manchego","Salsea las bases y esparce sobre ella el jamón y la piña. Espolvorea el queso y hornea por 20 minutos o hasta que la masa esté cocida Revuelve el chile habanero en un tazón junto con la cebolla morada y el aceite de oliva. Cuando esté lista la pizza, cucharea esta mezcla sobre ella y lleva a la mesa.","1 Hora","https://dam.cocinafacil.com.mx/wp-content/uploads/2019/04/pizza-hawaiana.png")
recetas.append(recetaPrueba2)
recetas.append(recetaPrueba)

##Lista de posts
posts = []
now = datetime.now()
StrFecha = now.strftime("%B %d, %Y %H:%M:%S")
post1 = Post("PIZZA HAWAIANA",StrFecha,"Admin","Me gusta esta Receta")
posts.append(post1)

#iniciar contadores de reacciones a las recetas
contadorLikes = 0
contadorDislike = 0
contadorBad = 0

#Funcion para validar login
def validarLogin(user,password):
    confirm = False
    for x in usuarios:
        if x.usuario == user and x.contrasena == password: 
            confirm = True
            return confirm        
    return confirm  

#Funcion verificar usuario
def usuarioExistente(user):
    confirm =False
    for usuario in usuarios:
        if usuario.usuario ==user:
            confirm = True
            return confirm
    return confirm

def deleteUsuario(user):
    for usuariox in usuarios:
        if usuariox.usuario == user:
            usuarios.remove(usuariox)

def imprimirUsuarios():
    for usuario in usuarios:
        print(usuario.nombre  + usuario.apellido + usuario.usuario + usuario.contrasena)  

#funcion para buscar datos de un usuario
def buscarUsuario(user):
    for usuariox in usuarios:
        if usuariox.usuario ==user:
            datosUsuario = [usuariox.nombre,usuariox.apellido,usuariox.contrasena]
            return datosUsuario 

@app.route("/")
def home():
    return redirect(url_for("index"))

@app.route("/Index")
def index():
    return render_template("Home.html",recetas = recetas)

@app.route('/Login', methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        contra = request.form['password']

        if validarLogin(user,contra) and user== "admin" :
            error = None
            session['user'] =  user
            return redirect(url_for("Dashboard"))
        elif validarLogin(user, contra) and user != "admin":
            error = None
            session['user'] = user
            return redirect(url_for("inicio"))
        else:
            error = 'Credenciales no validas, vuelva a intentarlo'
            return render_template('Login.html', error=error)                                                
    else:
        return render_template('Login.html', error = None)  

@app.route('/Logout',methods = ['POST', 'GET'])
def Logout():
    session.pop("user",None)
    return render_template("Home.html",recetas = recetas)
    
@app.route('/Inicio',methods=['POST','GET'])
def inicio():
    if "user" in session:
        usuario = session["user"]
        return render_template('HomeLoged.html', usuario = usuario , recetas = recetas,posts = posts)  
    else:
        return redirect(url_for("login"))                
            
@app.route('/Registro', methods=['POST', 'GET'])
def SignUp(): 
    error = None
    confirm = None
    if request.method == 'POST':
        #obtener valores del formulario
        usuario  = request.form['usuario']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        contrasena = request.form['psw']
        contrasena2 = request.form['psw-repeat']
        
        if usuarioExistente(usuario)==False and contrasena==contrasena2:
            usuarios.append(Usuario(usuario,contrasena,nombre,apellido))
            error = None
            confirm = 'Se a registrado el usuario'
            return render_template('Sign.html', confirm = confirm,error=None)
        else:
            confirm = None
            error = 'Ya existe el usuaio, intenta con otro'  
            return render_template('Sign.html', confirm = confirm,error=error)         
    else:
        return render_template('Sign.html',confirm = None,error=None)
        
@app.route('/Recuperacion',methods=['POST', 'GET'])
def Forgot():
    error = None
    confirm = None
    if request.method == 'POST':
        user = request.form['usuario']
        if usuarioExistente(user) and user != "admin":
            error = None
            datosUsuario = buscarUsuario(user)
            contrasena = datosUsuario[2]
            confirm = 'Su contrasena es : ' + contrasena
            return render_template('Forgot.html', confirm = confirm, error = error)        
        else:
            confirm = None
            error = 'No se encontro al usuario, intente de nuevo'
            return render_template('Forgot.html', confirm=confirm, error = error)

    return render_template('Forgot.html',confirm = confirm,error = error)  

@app.route('/Modificar',methods=['POST','GET'])
def modificarUser():
    confirm = None
    error = None
    if request.method=='POST':
        if "user" in session:
            usuario = session['user']  
            currentUser = usuario
    
            userMod  = request.form['usuario']
            nombreMod = request.form['nombre']
            apellidoMod = request.form['apellido']
            contrasenaMod = request.form['psw']
            contrasena2Mod = request.form['psw-repeat']

            if userMod==currentUser and contrasenaMod==contrasena2Mod:
                
                deleteUsuario(currentUser)
                usuarios.append(Usuario(userMod,contrasenaMod,nombreMod,apellidoMod))
         
                error = None
                confirm = 'Se han modificado los datos del usuario correctamente' 
                return render_template('modifyUser.html', confirm = confirm,error =None,nombre = nombreMod, apellido = apellidoMod , usuario = userMod, contrasena= contrasenaMod)
            if usuarioExistente(userMod)==False:
                currentUser = session['user']
                deleteUsuario(currentUser)
                session.pop("user",None)   
                newUser=Usuario(userMod,contrasenaMod,nombreMod,apellidoMod)

                usuarios.append(newUser)

                session['user'] = userMod
                confirm = 'Se a modificado el nombre de usuario correctamente'
                
                return render_template('modifyUser.html', confirm = confirm,error =None,nombre = nombreMod, apellido = apellidoMod , usuario = userMod, contrasena= contrasenaMod)
            else:
                error = 'Ya existe un usuario con ese nombre, intenta con otro'
                    
                return render_template('modifyUser.html',confirm = None,error =error,nombre = nombreMod, apellido = apellidoMod , usuario = usuario, contrasena= contrasenaMod)        
        else:
            return redirect(url_for("login")) 
    
    if request.method =='GET':
        if "user" in session:
            usuario = session['user']
            datosCurrentUser = buscarUsuario(usuario)

            currentName = datosCurrentUser[0]
            currentApellido = datosCurrentUser[1]
            currentPass = datosCurrentUser[2]
            return render_template('modifyUser.html',confirm = None ,error = None,nombre = currentName, apellido = currentApellido, usuario = usuario, contrasena = currentPass)        
        else:
            return redirect(url_for("login"))  

@app.route('/Dashboard',methods=['POST','GET']) 
def Dashboard():
    if "user" in session:
        usuario = session["user"]
        if usuario == "admin":
            numRecetas = len(recetas)
            numUsuarios = len(usuarios)
            numComentarios = len(posts)
            numReacciones = contadorLikes + contadorDislike + contadorBad
            if numReacciones != 0:
                porcentLikes = (contadorLikes*100)/numReacciones
                porcentDisLikes = (contadorDislike*100)/numReacciones
                porcentBad = (contadorBad*100)/numReacciones
            else:
                porcentLikes =0
                porcentDisLikes = 0
                porcentBad = 0
            
            return render_template('DashboardAdmin.html', usuario = usuario , recetas = recetas, usuarios = usuarios, posts= posts, numRecetas = numRecetas, numUsuarios = numUsuarios,numReacciones = numReacciones, numComentarios = numComentarios , porcentLikes = porcentLikes, porcentDisLikes = porcentDisLikes, porcentBad = porcentBad)  
    else:
        return redirect(url_for("login")) 


@app.route('/RegistrarReceta', methods=['POST', 'GET'])
def RegistrarReceta():
    if "user" in session:
        confirm = None
        if request.method == 'POST':
            #obtener valores del formulario
            autor = session["user"]
            titulo  = request.form['titulo']
            resumen = request.form['resumen']
            ingredientes = request.form['ingredientes']
            procedimiento = request.form['procedimiento']
            tiempo = request.form['tiempo']
            imagen = request.form['imagen']

            recetas.append(Receta(autor,titulo,resumen,ingredientes,procedimiento,tiempo,imagen)) 
            confirm = 'La receta se agrego correctamente'
            return redirect(url_for("inicio"))    
        return render_template('RegistrarReceta.html', confirm = confirm )
    else:
        return redirect(url_for("login")) 

@app.route('/Comentar', methods = ['POST', 'GET']) 
def comentar():
    if "user" in session:
        if request.method == 'POST':
            coment = request.form['coment']
            titulo = request.form['comentId']
            usuario = session["user"]
            #agregar un post al arreglo de posts
            #obtener fecha sistema
            now = datetime.now()
            StrFecha = now.strftime("%B %d, %Y %H:%M:%S")
            posts.append(Post(titulo,StrFecha,usuario,coment))
            return redirect(url_for("inicio"))
        else:
            return redirect(url_for("inicio"))      
    else:
        return redirect(url_for("login")) 
        
@app.route('/cargarRecetas',methods=['POST']) 
def uploadFile():
    if "user" in session:
        usuario = session["user"]
        if usuario == "admin":
            if request.method == 'POST':
                datos = request.get_json()
                if datos['data'] == '':
                    return {"msg": 'Error en contenido'}

                contenido = base64.b64decode(datos['data']).decode('utf-8')

                filas = contenido.splitlines()
                reader = csv.reader(filas, delimiter=',')
                
                for row in reader:
                    receta = Receta(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                    recetas.append(receta)
                    
                
                numRecetas = len(recetas)
                numUsuarios = len(usuarios)
                numComentarios = len(posts)
                numReacciones = contadorLikes +  contadorDislike +  contadorBad
                return {"msg": 'Receta agregada'}
                return render_template('DashboardAdmin.html', usuario = usuario , recetas = recetas, usuarios = usuarios, posts= posts, numRecetas = numRecetas, numUsuarios = numUsuarios,numReacciones = numReacciones, numComentarios = numComentarios)  
    else:
        return redirect(url_for("login")) 

@app.route('/Like')          
def reactionLike():
    if "user" in session:
        global contadorLikes
        contadorLikes = contadorLikes + 1
        return redirect(url_for("inicio"))
    else:
        return redirect(url_for("login"))  

@app.route('/DisLike')          
def reactionDislike():
    if "user" in session:
        global contadorDislike 
        contadorDislike = contadorDislike + 1
        return redirect(url_for("inicio"))
    else:
        return redirect(url_for("login"))   

@app.route('/BadLike')          
def reactionBadlike():
    if "user" in session:
        global contadorBad
        contadorBad = contadorBad + 1
        return redirect(url_for("inicio"))
    else:
        return redirect(url_for("inicio"))                 

@app.route('/DescargarReportePDF')
def DescargarReportePDF():
    flash( 'Procesando descarga')
    return redirect(url_for('Dashboard'))
if __name__ == '__main__':
    app.run( port = 5000,threaded = False)
