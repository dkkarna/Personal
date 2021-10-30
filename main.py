import datetime
from flask import Flask, render_template, request, url_for, redirect
from google.cloud import datastore
from form import RegistrationForm, LoginForm, AddGPUForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'c394d22892a5d1a4d87ca6ed74bc15eb'

# get access to the datastore client so we can add and store data in the datastore
datastore_client = datastore.Client()
USERS = "USERS"
GPU_DATA = "GPU_DATA"

@app.route('/', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        query = datastore_client.query(kind=USERS)
        filterData = query.add_filter('email','=', form.email.data)
        result = list(filterData.fetch())
        if len(result) == 0:
            #// not exis
            print("")
        else:
            user = result[0]
            if user["password"] == form.password.data:
                return redirect(url_for('home'))
            else:
                print("wrong Email or Password")
    return render_template('index.html', form=form)

@app.route('/addGPU', methods=['GET','POST'])
def addGPU():
    form = AddGPUForm()
    if form.validate_on_submit():
        gpy_key = datastore_client.key(GPU_DATA)
        entity = datastore.Entity(key = gpy_key)
        entity["name"] = form.name.data
        entity["manufacturer"] = form.manufacturer.data
        entity["dateissued"] = form.dateissued.data
        entity["geometryshader"] = form.geometryshader.data
        entity["tesselationShader"] = form.tesselationShader.data
        entity["shaderInt16"] = form.shaderInt16.data
        entity["sparseBinding"] = form.sparseBinding.data
        entity["texturecompressionETC2"] = form.texturecompressionETC2.data
        entity["vertexPipelineStoresAndAtomics"] = form.vertexPipelineStoresAndAtomics.data
        datastore_client.put(entity)
        return redirect(url_for('home'))
    return render_template('addgpu.html', form=form)

@app.route('/home', methods=["GET","POST"])
def home():
    query = datastore_client.query(kind=GPU_DATA)
    result = list(query.fetch())
    # user_key = datastore_client.key(USERS)
    # entity = datastore.Entity(key = user_key)
    # entity.update({'timestamp' : "KARNA DESAI"})
    # datastore_client.put(entity)
    return render_template('home.html', gpuData=result)



@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_key = datastore_client.key(USERS)
        entity = datastore.Entity(key = user_key)
        entity["email"] = form.email.data
        entity["password"] = form.password.data
        entity["confirm_password"] = form.confirm_password.data
        datastore_client.put(entity)
        return redirect(url_for('home'))
    return render_template('signUp.html', form=form)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
