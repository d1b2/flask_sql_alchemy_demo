from flask import Flask
from flask import Flask,request,app,render_template,redirect,flash
from flask_sqlalchemy import SQLAlchemy
import pickle
import numpy as np
from datetime import datetime
# Import for Migrations
from flask_migrate import Migrate, migrate
 
 
app = Flask(__name__)
#app.secret_key = "super secret key"
app.debug = True
model=pickle.load(open('model.pkl','rb'))
# adding configuration for using a sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///website.db'
 
# Creating an SQLAlchemy instance
db = SQLAlchemy(app)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sepal_length = db.Column(db.Float, unique=False, nullable=False)
    sepal_width = db.Column(db.Float, unique=False, nullable=False)
    petal_length = db.Column(db.Float, unique=False, nullable=False)
    petal_width = db.Column(db.Float, unique=False, nullable=False)
    species = db.Column(db.String(20), unique=False, nullable=False)
    time_stamp=db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    model_response_time=db.Column(db.Float, unique=False, nullable=False)
    
 
    # repr method represents how one object of this datatable
    # will look like
    def __repr__(self):
        return f"Sepal(length X width) : {self.sepal_length} X {self.sepal_width}, Petal(length X width) : {self.petal_length} X {self.petal_width}, Species: {self.species}"


# Settings for migrations
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template('home1.html')

@app.route('/predict',methods=['POST'])
def predict():
    start = datetime.utcnow()
    data=[float(x) for x in request.form.values()]
    final_features = [np.array(data)]
    output=model.predict(final_features)[0]
    end = datetime.utcnow()
    eval_time = round(((end-start).microseconds)/1e6,2)
    output_species=str
    #print(output)

    if output==0:output_species='Iris-setosa'
    elif output==1:output_species='Iris-versicolor'
    elif output==2:output_species='Iris-virginica'
    
    p = Profile(sepal_length=data[0], 
                sepal_width=data[1],
                petal_length=data[2],
                petal_width=data[3],
                species=output_species,
                model_response_time=eval_time)
    db.session.add(p)
    db.session.commit()  
   
    
    return render_template('results1.html',prediction_text=output_species,values=data)

@app.route('/previous-prediction')
def previous():
    result=Profile.query.order_by(Profile.id.desc()).first().id
    data_to_show = Profile.query.get(result)
    return render_template('results2.html',values=data_to_show)

@app.route('/record')
def records():
    data = Profile.query.all()
    return render_template('records.html',data=data)

@app.route('/delete/<int:id>')
def delete(id):
    # Deletes the data on the basis of unique id and
    # redirects to home page
    entry_to_delete = Profile.query.get_or_404(id)
    db.session.delete(entry_to_delete)
    db.session.commit()
    #flash("Record Deleted")
    #data = Profile.query.all()
    return redirect('/record')
if __name__ == '__main__':
    app.run()