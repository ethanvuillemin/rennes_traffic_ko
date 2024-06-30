from flask import Flask, render_template, request
import plotly.express as px
from keras.models import load_model

import logging

from src.get_data import GetData
from src.utils import create_figure, prediction_from_model

import flask_monitoringdashboard as dashboard

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration des logs
app.logger.setLevel(logging.INFO)  # Niveau de log défini sur INFO
handler = logging.FileHandler('flask_monitoring_dashboard.log')  # Fichier de log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Configuration du tableau de bord de surveillance Flask
dashboard.config.init_from(file='config.cfg')
dashboard.bind(app)

# Initialisation de l'objet GetData pour récupérer les données de trafic
data_loader = GetData(url="https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B")
data = data_loader()

# Chargement du modèle Keras pré-entraîné pour les prédictions de trafic
model = load_model('model.h5')

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Route principale de l'application Flask.
    Affiche un graphique interactif avec les données de trafic et les prédictions.
    """
    try:
        if request.method == 'POST':
            # Si la méthode est POST, une heure est sélectionnée depuis le formulaire
            selected_hour = request.form['hour']
            # Prédiction de la catégorie de trafic pour l'heure sélectionnée
            cat_predict = prediction_from_model(model=model, hour_to_predict=selected_hour)
            # Mapping des catégories prédites avec les couleurs associées
            color_pred_map = {
                0: ["Prédiction : Libre", "green"],
                1: ["Prédiction : Dense", "orange"],
                2: ["Prédiction : Bloqué", "red"]
            }
            # Création du graphique interactif avec les données de trafic
            fig_map = create_figure(data)
            # Conversion du graphique en format JSON pour l'envoyer au template HTML
            graph_json = fig_map.to_json() if fig_map is not None else None
            # Logging des informations sur la requête POST et la prédiction de trafic
            app.logger.info(f'POST request. Predicted category: {color_pred_map[cat_predict][0]}.')

            # Renvoi du template HTML avec le graphique et les informations de prédiction
            return render_template('index.html',
                                graph_json=graph_json,
                                text_pred=color_pred_map[cat_predict][0],
                                color_pred=color_pred_map[cat_predict][1])
        else:
            # Si la méthode est GET, affiche simplement le graphique interactif avec les données de trafic
            fig_map = create_figure(data)
            graph_json = fig_map.to_json() if fig_map is not None else None
            # Logging des informations sur la requête GET
            app.logger.info(f'GET request. Graph JSON: {graph_json}')
            # Renvoi du template HTML avec le graphique
            return render_template('index.html', graph_json=graph_json)
    except Exception as e:
        # En cas d'erreur, log l'exception
        app.logger.error(f'Error processing {request.method} request: {str(e)}')

if __name__ == '__main__':
    # Exécute l'application Flask en mode debug
    app.run(debug=True)
