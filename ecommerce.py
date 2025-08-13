from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ayakkabilar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Ayakkabi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marka = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    boyut = db.Column(db.Float, nullable=False)
    fiyat = db.Column(db.Float, nullable=False)
    resim_url = db.Column(db.String(200), default='https://placehold.co/200x200?text=Ayakkabı')

    def __repr__(self):
        return f'<Ayakkabi {self.marka} {self.model}>'

@app.route('/')
def anasayfa():
  
    ayakkabilar_sorgu = Ayakkabi.query


    arama_sorgusu = request.args.get('search_query')
    if arama_sorgusu:
        ayakkabilar_sorgu = ayakkabilar_sorgu.filter(
            (Ayakkabi.marka.ilike(f'%{arama_sorgusu}%')) | 
            (Ayakkabi.model.ilike(f'%{arama_sorgusu}%'))
        )


    min_fiyat = request.args.get('min_fiyat', type=float)
    max_fiyat = request.args.get('max_fiyat', type=float)
    filtre_marka = request.args.get('filtre_marka') 
    if min_fiyat is not None:
        ayakkabilar_sorgu = ayakkabilar_sorgu.filter(Ayakkabi.fiyat >= min_fiyat)
    if max_fiyat is not None:
        ayakkabilar_sorgu = ayakkabilar_sorgu.filter(Ayakkabi.fiyat <= max_fiyat)
    if filtre_marka:
        ayakkabilar_sorgu = ayakkabilar_sorgu.filter(Ayakkabi.marka.ilike(f'%{filtre_marka}%'))

    
    siralama = request.args.get('siralama')
    if siralama == 'fiyat_asc':
        ayakkabilar_sorgu = ayakkabilar_sorgu.order_by(Ayakkabi.fiyat.asc())
    elif siralama == 'fiyat_desc':
        ayakkabilar_sorgu = ayakkabilar_sorgu.order_by(Ayakkabi.fiyat.desc())

    ayakkabilar = ayakkabilar_sorgu.all()
    
    return render_template('index.html', 
                           ayakkabilar=ayakkabilar, 
                           current_search_query=arama_sorgusu,
                           current_min_fiyat=min_fiyat,
                           current_max_fiyat=max_fiyat,
                           current_filtre_marka=filtre_marka,
                           current_siralama=siralama)

@app.route('/urun_ekle', methods=['GET', 'POST'])
def urun_ekle():
    if request.method == 'POST':
        marka = request.form['marka']
        model = request.form['model']
        boyut = float(request.form['boyut'])
        fiyat = float(request.form['fiyat'])
        resim_url = request.form['resim_url']

        yeni_ayakkabi = Ayakkabi(
            marka=marka,
            model=model,
            boyut=boyut,
            fiyat=fiyat,
            resim_url=resim_url
        )

        db.session.add(yeni_ayakkabi)
        db.session.commit()
        
        return redirect(url_for('anasayfa'))
    
    return render_template('add_product.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
