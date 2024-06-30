import logging
import psutil
from datetime import datetime
from pushbullet import Pushbullet
import time
import threading

# Configuration des logs
logger = logging.getLogger('monitoring')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('monitoring.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initialisation de Pushbullet
PUSHBULLET_API_KEY = 'o.l4hlr7zzv8D7LquYourZfrDr26swNSBQ'  
pb = Pushbullet(PUSHBULLET_API_KEY)

# Définir des seuils pour les notifications
MAX_REQUESTS_PER_DAY = 10
MAX_RAM_PERCENTAGE = 80  # Pourcentage d'utilisation de la RAM
MAX_CPU_PERCENTAGE = 80  # Pourcentage d'utilisation du CPU

# Stockage des requêtes par jour
requests_count = {}

def get_requests_count_for_today():
    """
    Obtient le nombre de requêtes pour la journée actuelle.
    """
    current_date = datetime.now().date()
    return requests_count.get(current_date, 0)

def check_system_usage():
    """
    Vérifie les statistiques d'utilisation du système et envoie des notifications si elles dépassent les seuils.
    """
    # Vérifie le nombre de requêtes reçues aujourd'hui
    current_date = datetime.now().date()
    requests_today = get_requests_count_for_today()

    # Vérifie l'utilisation de la RAM
    ram_usage = psutil.virtual_memory().percent

    # Vérifie l'utilisation du CPU
    cpu_usage = psutil.cpu_percent(interval=1)

    # Envoie des notifications si les seuils sont dépassés
    if requests_today > MAX_REQUESTS_PER_DAY:
        send_notification("Nombre de requêtes élevé aujourd'hui.")

    if ram_usage > MAX_RAM_PERCENTAGE:
        send_notification("Utilisation excessive de la RAM.")

    if cpu_usage > MAX_CPU_PERCENTAGE:
        send_notification("Utilisation excessive du CPU.")

def send_notification(message):
    """
    Envoie une notification avec le message spécifié via Pushbullet.
    """
    push = pb.push_note("Alerte de surveillance du système", message)
    logger.info(f'Notification sent: {message}')

def monitoring_task():
    """
    Tâche de monitoring exécutée en permanence.
    """
    while True:
        try:
            check_system_usage()
            time.sleep(60)  # Vérifie toutes les minutes
        except Exception as e:
            logger.error(f'Error in monitoring task: {str(e)}')

# Démarrer la tâche de monitoring dans un thread
monitoring_thread = threading.Thread(target=monitoring_task)
monitoring_thread.daemon = True
monitoring_thread.start()

# Notification de démarrage
send_notification('Application E5 monitoring en cours de démarrage')
