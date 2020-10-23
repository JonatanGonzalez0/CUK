from flask import Flask, render_template, request, redirect, session, url_for, make_response
from Datos.Usuario import Usuario
from Datos.Receta import Receta

app = Flask(__name__)
app.secret_key = "IngenieriaUsacAdmin"

usuarioMaestro = Usuario("admin","admin","Usuario", "Maestro",)
usuarios = [usuarioMaestro]
recetaPrueba = Receta("Jonatan","Sandwitch Americano","Elaboracion de un Sandwitch americano con ingredientes frescos.","Pan , Jamon, Queso, Lechuga, Tomate","En un sartén disponer las lonchas de tocineta cortadas por la mitad y cocinar a fuego bajo hasta que suelten su grasa y queden crocantes. Cuando estén listas pasar por papel absorbente para eliminar el exceso de grasa. Aparte en otro sartén, derretir un poco de mantequilla y añadir las rodajas de pan, dorar por ambos lados. ","20 min","https://www.hogar.mapfre.es/media/2019/02/sandwich-americano.jpg")
recetas= []
recetas.append(recetaPrueba)


#Funcion para validar login
def validarLogin(user,password):
    for usuario in usuarios:
        if usuario.usuario == user and usuario.contrasena == password:
            
            return True
    return False
#Funcion verificar usuario
def usuarioExistente(user):
    for usuario in usuarios:
        if usuario.usuario ==user:
            return True
    return False
#Funcion para registrar usuario
def registroUsuario(nombre,apellido,user,password,password2):
    if(password==password2):
        usuarios.append(Usuario(user,password,nombre,apellido))
    else:
        return False 

def buscarUsuario(user):
    for usuario in usuarios:
        if usuario.usuario ==user:
            return usuario
    return False     

def deleteUsuario(user):
    for usuariox in usuarios:
        if usuariox.usuario == user:
            usuarios.remove(usuariox)

def imprimirUsuarios():
    for usuario in usuarios:
        print(usuario.nombre  + usuario.apellido + usuario.usuario + usuario.contrasena)        



@app.route("/")
def index():
    return render_template("Home.html",recetas = recetas)

@app.route('/Login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        usuario = request.form['username']
        contra = request.form['password']
        
        if validarLogin(usuario, contra) and usuario != "admin":
            error = None
            usuario = request.form['username']
            session['user'] = usuario
            return redirect(url_for("Inicio"))
        elif validarLogin(usuario,contra) and usuario== "admin" :
            error = None
            session['user'] =  usuario
            return redirect(url_for("Dashboard"))
        else:
            error = 'Credenciales no validas, vuelva a intentarlo'
            return redirect(url_for("login"))             
    return render_template('Login.html', error = None)  

@app.route('/Logout')
def Logout():
    session.pop("user",None)
    return render_template("Home.html", recetas = recetas)            
            
@app.route('/Registro', methods=['POST', 'GET'])
def SignUp():
    
    if request.method == 'POST':
        #obtener valores del formulario
        usuario  = request.form['usuario']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        contrasena = request.form['psw']
        contrasena2 = request.form['psw-repeat']
        
        if usuarioExistente(usuario)==False:
            registroUsuario(nombre,apellido,usuario,contrasena,contrasena2)
            error = None
            confirm = 'Se a registrado completamente'
            return redirect(url_for("Registro"))
        else:
            confirm = None
            error = 'Ya existe el usuaio, intenta con otro'  
            return redirect(url_for("Registro"))    
    else:
        return render_template('Sign.html',confirm = confirm,error=error)
        
@app.route('/Recuperacion',methods=['POST', 'GET'])
def Forgot():
    error = None
    confirm = None
    if request.method == 'POST':
        user = request.form['usuario']
        if usuarioExistente(user):
            for usuario in usuarios:
                if usuario.usuario ==user:
                    error = None
                    confirm = 'Su contrasena es : ' + usuario.contrasena
                    return render_template('Forgot.html', confirm = confirm, error = error)  
        else:
            confirm = None
            error = 'No se encontro al usuario, intente de nuevo'
            return render_template('Forgot.html', confirm=confirm, error = error)

    return render_template('Forgot.html',confirm = confirm,error = error)  

@app.route('/Modificar',methods=['POST', 'GET'])
def modificarUser():
    confirm = None
    error = None
    if request.method=='POST':
        if "user" in session:
            usuario = session["user"]
            UserData = buscarUsuario(usuario)
            currentUser = UserData.usuario
    
            userMod  = request.form['usuario']
            nombreMod = request.form['nombre']
            apellidoMod = request.form['apellido']
            contrasenaMod = request.form['psw']
            contrasena2Mod = request.form['psw-repeat']

            if userMod==currentUser and contrasenaMod==contrasena2Mod:
                
                deleteUsuario(currentUser)
                registroUsuario(nombreMod,apellidoMod,userMod,contrasenaMod,contrasena2Mod)
                error = None
                confirm = 'Se a modificado completamente'
                imprimirUsuarios()
                
                return render_template('modifyUser.html', confirm = confirm,error =error,nombre = nombreMod, apellido = apellidoMod , usuario = usuario, contrasena= contrasenaMod)
            else:
                if usuarioExistente(userMod)==False:
                    
                    currentUser = session['user']
                    deleteUsuario(currentUser)
                    registroUsuario(nombreMod,apellidoMod,userMod,contrasenaMod,contrasena2Mod)
                    session['user'] = userMod
                    confirm = 'Se a modificado su usuario correctamente'
                
                    return render_template('modifyUser.html', confirm = confirm,error =None,nombre = nombreMod, apellido = apellidoMod , usuario = userMod, contrasena= contrasenaMod)
                else:
                    error = 'Ya existe un usuario con ese nombre, intenta con otro'
                    
                    return render_template('modifyUser.html',confirm = None,error =error,nombre = nombreMod, apellido = apellidoMod , usuario = usuario, contrasena= contrasenaMod)        
        else:
            return redirect(url_for("login")) 
    else:
        if "user" in session:
            usuario = session["user"]
            UserData = buscarUsuario(usuario)
            currentName = UserData.nombre
            currentApellido = UserData.apellido
            currentUser = UserData.usuario
            currentPass = UserData.contrasena 
            return render_template('modifyUser.html',confirm = None ,error = None,nombre = currentName, apellido = currentApellido, usuario = currentUser, contrasena = currentPass)        
        else:
            return redirect(url_for("login")) 
     

@app.route('/Inicio')
def Inicio():
    if "user" in session:
        usuario = session["user"]
        return render_template('HomeLoged.html', usuario = usuario , recetas = recetas)  
    else:
        return redirect(url_for("login"))   

@app.route('/Dashboard') 
def Dashboard():
    if "user" in session:
        usuario = session["user"]
        if usuario == 'admin':
            return render_template('DashboardAdmin.html', usuario = usuario , recetas = recetas, usuarios = usuarios)  
    else:
        return redirect(url_for("login")) 


@app.route('/RegistrarReceta', methods=['POST', 'GET'])
def RegistrarReceta():
    confirm = None
    if request.method == 'POST':
        #obtener valores del formulario
        
        autor = request.form['autor']
        titulo  = request.form['titulo']
        resumen = request.form['resumen']
        ingredientes = request.form['ingredientes']
        procedimiento = request.form['procedimiento']
        tiempo = request.form['tiempo']
        imagen = request.form['imagen']

        recetas.append(Receta(autor,titulo,resumen,ingredientes,procedimiento,tiempo,imagen)) 
        confirm = 'La receta se agrego correctamente'
        render_template('RegistrarReceta.html' , confirm = confirm)
        return redirect(url_for("Inicio"))        
    return render_template('RegistrarReceta.html', confirm = confirm )      

if __name__ == '__main__':
    app.run(threaded = True, port = 5000)
