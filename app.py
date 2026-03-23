from flask import Flask, jsonify, request
from config.database import db, DATABASE_URI
from models.article import Article  # Import du modèle depuis models/
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration de la base de données MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

# Clé secrète pour les sessions
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Initialisation de la base de données
db.init_app(app)

# Création des tables (à exécuter une seule fois)
with app.app_context():
    try:
        db.create_all()
        print("✅ Base de données MySQL connectée avec succès")
        print(f"📊 Base : {os.getenv('DB_NAME')} sur {os.getenv('DB_HOST')}")
    except Exception as e:
        print(f"❌ Erreur de connexion à MySQL : {e}")
        print("Vérifiez que MySQL est démarré et que les identifiants sont corrects")

# ============ ROUTES ============

# Route d'accueil
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'name': 'Blog API',
        'version': '1.0.0',
        'description': 'API pour la gestion d\'articles de blog',
        'endpoints': {
            'POST /api/articles': 'Créer un article',
            'GET /api/articles': 'Lister les articles',
            'GET /api/articles/{id}': 'Récupérer un article',
            'PUT /api/articles/{id}': 'Modifier un article',
            'DELETE /api/articles/{id}': 'Supprimer un article',
            'GET /api/articles/search?query=': 'Rechercher des articles',
            'GET /api/articles/category/{categorie}': 'Filtrer par catégorie',
            'GET /api/health': 'Vérifier l\'état de l\'API'
        }
    })

# 1. Créer un article
@app.route('/api/articles', methods=['POST'])
def create_article():
    try:
        data = request.get_json()
        
        # Validation des entrées
        if not data.get('titre'):
            return jsonify({'error': 'Le titre est obligatoire'}), 400
        if not data.get('contenu'):
            return jsonify({'error': 'Le contenu est obligatoire'}), 400
        if not data.get('auteur'):
            return jsonify({'error': "L'auteur est obligatoire"}), 400
        if not data.get('categorie'):
            return jsonify({'error': 'La catégorie est obligatoire'}), 400
        
        # Création de l'article
        article = Article(
            titre=data['titre'],
            contenu=data['contenu'],
            auteur=data['auteur'],
            categorie=data['categorie'],
        )
        
        db.session.add(article)
        db.session.commit()
        
        return jsonify({
            'message': 'Article créé avec succès',
            'id': article.id,
            'article': article.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 2. Récupérer tous les articles (avec filtres optionnels)
@app.route('/api/articles', methods=['GET'])
def get_articles():
    try:
        # Récupérer les paramètres de filtre
        categorie = request.args.get('categorie')
        auteur = request.args.get('auteur')
        date_filter = request.args.get('date')
        
        query = Article.query
        
        # Appliquer les filtres
        if categorie:
            query = query.filter_by(categorie=categorie)
        if auteur:
            query = query.filter_by(auteur=auteur)
        if date_filter:
            query = query.filter(db.func.date(Article.date) == date_filter)
        
        articles = query.order_by(Article.date.desc()).all()
        
        return jsonify({
            'articles': [article.to_dict() for article in articles],
            'count': len(articles)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 3. Récupérer un article par ID
@app.route('/api/articles/<int:id>', methods=['GET'])
def get_article(id):
    try:
        article = Article.query.get(id)
        
        if not article:
            return jsonify({'error': 'Article non trouvé'}), 404
            
        return jsonify(article.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 4. Modifier un article
@app.route('/api/articles/<int:id>', methods=['PUT'])
def update_article(id):
    try:
        article = Article.query.get(id)
        
        if not article:
            return jsonify({'error': 'Article non trouvé'}), 404
        
        data = request.get_json()
        
        # Mise à jour des champs
        if 'titre' in data:
            article.titre = data['titre']
        if 'contenu' in data:
            article.contenu = data['contenu']
        if 'categorie' in data:
            article.categorie = data['categorie']
        if 'auteur' in data:
            article.auteur = data['auteur']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Article modifié avec succès',
            'article': article.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 5. Supprimer un article
@app.route('/api/articles/<int:id>', methods=['DELETE'])
def delete_article(id):
    try:
        article = Article.query.get(id)
        
        if not article:
            return jsonify({'error': 'Article non trouvé'}), 404
        
        db.session.delete(article)
        db.session.commit()
        
        return jsonify({'message': 'Article supprimé avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 6. Rechercher des articles
@app.route('/api/articles/search', methods=['GET'])
def search_articles():
    try:
        query = request.args.get('query', '')
        
        if not query:
            return jsonify({'error': 'Le paramètre query est requis'}), 400
        
        # Recherche dans titre et contenu (insensible à la casse)
        articles = Article.query.filter(
            (Article.titre.like(f'%{query}%')) | 
            (Article.contenu.like(f'%{query}%'))
        ).order_by(Article.date.desc()).all()
        
        return jsonify({
            'articles': [article.to_dict() for article in articles],
            'count': len(articles),
            'search_term': query
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 7. Route optionnelle : articles par catégorie
@app.route('/api/articles/category/<categorie>', methods=['GET'])
def get_articles_by_category(categorie):
    try:
        articles = Article.query.filter_by(categorie=categorie).order_by(Article.date.desc()).all()
        
        if not articles:
            return jsonify({
                'message': f'Aucun article trouvé dans la catégorie {categorie}',
                'articles': [],
                'count': 0
            }), 200
        
        return jsonify({
            'articles': [article.to_dict() for article in articles],
            'count': len(articles),
            'category': categorie
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 8. Route de test pour vérifier la connexion MySQL
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Tester la connexion à la base de données
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'database_type': 'MySQL',
            'database_name': os.getenv('DB_NAME'),
            'host': os.getenv('DB_HOST')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

#Si on utilise: python app.py  pour executer l'app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
