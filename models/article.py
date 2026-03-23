from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config.database import db

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    auteur = db.Column(db.String(100), nullable=False)
    categorie = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'titre': self.titre,
            'contenu': self.contenu,
            'auteur': self.auteur,
            'date': self.date.isoformat() if self.date else None,
            'categorie': self.categorie,
        }
    
    def __repr__(self):
        return f"<Article {self.titre}>"
    