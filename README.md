# TP Big Data : Kafka, HDFS et Spark

Ce TP permet de mettre en place un environnement Big Data complet avec Apache Kafka, Hadoop HDFS et Spark pour créer un pipeline de données simple mais fonctionnel.

## Objectifs
- Configurer un cluster Hadoop avec Docker
- Démarrer et utiliser Kafka pour la messagerie
- Produire et consommer des messages avec Kafka
- Stocker des données dans HDFS
- Analyser les données avec Spark

## Prérequis
- Docker installé sur votre machine
- VS Code (ou autre éditeur de code)
- Connaissances de base en Python

## Étape 1: Configuration de l'environnement Docker

Créez un nouveau projet VS Code nommé TP1BigData, puis lancez les commandes suivantes dans le terminal:

```bash
# Télécharger l'image Hadoop/Kafka
docker pull liliasfaxi/hadoop-cluster:latest

# Créer un réseau dédié pour les conteneurs
docker network create --driver=bridge hadoop

# Lancer le nœud master
docker run -itd --net=hadoop -p 9870:9870 -p 8088:8088 -p 7077:7077 -p 16010:16010 -p 9092:9092 --name hadoop-master --hostname hadoop-master liliasfaxi/hadoop-cluster:latest

# Lancer les nœuds workers
docker run -itd -p 8040:8042 --net=hadoop --name hadoop-worker1 --hostname hadoop-worker1 liliasfaxi/hadoop-cluster:latest
docker run -itd -p 8041:8042 --net=hadoop --name hadoop-worker2 --hostname hadoop-worker2 liliasfaxi/hadoop-cluster:latest
```

> **Note**: Ajouter le port 9092 au nœud master pour exposer Kafka

![Configuration Docker](images/docker_config.png)
*Capture d'écran: Lancement des conteneurs Docker*

## Étape 2: Démarrage des services Hadoop et Kafka

Entrez dans le conteneur master et démarrez Hadoop:

```bash
# Entrer dans le conteneur master
docker exec -it hadoop-master bash

# Démarrer Hadoop
./start-hadoop.sh

# Vérifier les processus
jps
```

Démarrer Kafka:

```bash
./start-kafka-zookeeper.sh

# Vérifier les processus
jps
```

![Vérification des processus](images/jps_output.png)
*Capture d'écran: Résultat de la commande jps montrant les processus Hadoop et Kafka*

## Étape 3: Production de messages Kafka

Créez un script Python `produce.py` pour envoyer des messages à Kafka:

```python
from confluent_kafka import Producer

def delivery_callback(err, msg):
    if err:
        print(f"Failed to deliver message: {err}")
    else:
        print(f"Message delivered: {msg}")

p = Producer({'bootstrap.servers': 'localhost:9092'})

# Liste de 10 messages différents à envoyer
messages = [
    "Insérer ici votre premier message",
    "Deuxieme message: Données en temps réel",
    "Troisieme message: Traitement de flux Big Data",
    "Quatrieme message: Kafka est un système de messagerie distribué",
    "Cinquieme message: Utilisé pour les pipelines de données",
    "Sixieme message: Compatible avec Hadoop",
    "Septieme message: Haute disponibilité et tolérance aux pannes",
    "Huitieme message: Traitement de millions de messages par seconde",
    "Neuvieme message: Architecture basée sur les logs",
    "Dixieme message: Fin de la séquence de test"
]

# Production des messages
for message in messages:
    p.produce('data_stream', message, callback=delivery_callback)
    print(f"Message envoyé: {message}")

# Attendre que tous les messages soient envoyés
p.flush()
```

Exécutez le script:

```bash
# Installer confluent-kafka si nécessaire
pip install confluent-kafka

# Exécuter le script
python produce.py
```

![Production de messages](images/produce_output.png)
*Capture d'écran: Production de messages Kafka*

## Étape 4: Consommation de messages Kafka

Créez un script Python `consume.py` pour lire les messages de Kafka:

```python
from confluent_kafka import Consumer, KafkaError

# Configuration du consumer
c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my_group',
    'auto.offset.reset': 'earliest'
})

# Abonnement au topic
c.subscribe(['data_stream'])

print("Démarrage du consumer pour le topic 'data_stream'...")
print("En attente de messages...")

# Boucle de consommation
try:
    while True:
        msg = c.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print("Fin de partition atteinte")
                continue
            else:
                print(f"Erreur: {msg.error()}")
                break
        
        # Afficher le message reçu
        print('Message reçu: {}'.format(msg.value().decode('utf-8')))
except KeyboardInterrupt:
    print("Consumer arrêté par l'utilisateur")
finally:
    # Fermer le consumer
    c.close()
```

Exécutez le script:

```bash
python consume.py
```

![Consommation de messages](images/consume_output.png)
*Capture d'écran: Consommation de messages Kafka*

## Étape 5: Stockage des données dans HDFS

Créez un répertoire dans HDFS pour stocker les données:

```bash
hdfs dfs -mkdir -p /user/root/data
hdfs dfs -chmod -R 777 /user/root/data
```

Créez un script Python `consumeinhdfs.py` pour lire les messages Kafka et les écrire dans HDFS:

```python
from confluent_kafka import Consumer, KafkaError
import subprocess
import os

# Chemin du fichier temporaire local
temp_file = '/tmp/kafka_message.txt'

# Chemin du fichier HDFS
hdfs_path = '/user/root/data/data_stream.txt'

# Configuration du consumer Kafka
c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my_group',
    'auto.offset.reset': 'earliest'
})

# Abonnement au topic
c.subscribe(['data_stream'])

print(f"Démarrage du consumer et écriture dans HDFS à {hdfs_path}...")
messages_count = 0

try:
    while True:
        msg = c.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Erreur: {msg.error()}")
                break

        # Récupérer le message
        message = msg.value().decode('utf-8')
        print(f'Message reçu: {message}')
        
        # Écrire d'abord dans un fichier temporaire local
        with open(temp_file, 'w') as f:
            f.write(message + '\n')
        
        # Ajouter au fichier dans HDFS
        try:
            # Vérifier si le fichier existe déjà
            check_cmd = f"hdfs dfs -test -e {hdfs_path}; echo $?"
            result = subprocess.check_output(check_cmd, shell=True).decode().strip()
            
            if result == "0":
                # Le fichier existe, ajouter le contenu
                append_cmd = f"hdfs dfs -appendToFile {temp_file} {hdfs_path}"
                subprocess.run(append_cmd, shell=True, check=True)
            else:
                # Le fichier n'existe pas, le créer
                put_cmd = f"hdfs dfs -put {temp_file} {hdfs_path}"
                subprocess.run(put_cmd, shell=True, check=True)
            
            messages_count += 1
            print(f"Message écrit dans HDFS - Total: {messages_count}")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'écriture dans HDFS: {e}")
            
except KeyboardInterrupt:
    print("Programme arrêté par l'utilisateur")
finally:
    # Fermer le consumer
    c.close()
    print("Consumer fermé")
    # Supprimer le fichier temporaire
    if os.path.exists(temp_file):
        os.remove(temp_file)
```

Exécutez le script et produisez de nouveaux messages:

```bash
# Dans un terminal
python consumeinhdfs.py

# Dans un autre terminal
python produce.py
```

Vérifiez que les données ont bien été écrites dans HDFS:

```bash
hdfs dfs -cat /user/root/data/data_stream.txt
```

![Stockage HDFS](images/hdfs_output.png)
*Capture d'écran: Contenu du fichier dans HDFS*

## Étape 6: Analyse des données avec Spark

Créez un script Python `countmessagespark.py` pour analyser les données avec Spark:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, col

# Création de la session Spark
spark = SparkSession.builder \
    .appName("Analyse de données Kafka") \
    .getOrCreate()

# Utilisation du chemin correct
df = spark.read.text("hdfs://hadoop-master:9000/user/root/data/data_stream.txt")

# Afficher les premières lignes pour vérification
print("Aperçu des données:")
df.show(5, truncate=False)

# Effectuer un comptage simple
word_count = df.count()
print("Nombre total de messages:", word_count)

# Pour un comptage de mots plus détaillé
words_df = df.select(explode(split(col("value"), " ")).alias("word"))
word_counts = words_df.groupBy("word").count().orderBy("count", ascending=False)

print("Top 10 des mots les plus fréquents:")
word_counts.show(10)

# Arrêter la session Spark
spark.stop()
```

Exécutez le script:

```bash
python countmessagespark.py
```

![Analyse Spark](images/spark_output.png)
*Capture d'écran: Résultat de l'analyse Spark*

## Résolution de problèmes courants

### Problème: Échec de connexion à Kafka
- Vérifiez que le port 9092 est bien exposé dans Docker
- Utilisez `localhost:9092` à l'intérieur du conteneur, mais l'adresse IP ou le nom d'hôte approprié depuis l'extérieur

### Problème: Échec d'écriture dans HDFS
- Vérifiez les chemins HDFS (ils ne correspondent pas aux chemins du système de fichiers local)
- Vérifiez les permissions des répertoires dans HDFS
- Utilisez les commandes HDFS pour créer des répertoires et vérifier les permissions

### Problème: Erreurs de taille avec Spark
Si vous rencontrez des erreurs de taille avec Spark, modifiez le fichier hdfs-site.xml:

```bash
nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```

Ajoutez cette configuration:

```xml
<property>
  <name>dfs.blocksize</name>
  <value>1m</value>
  <description>Block size for HDFS</description>
</property>
```

## Conclusion

Ce TP vous a permis de mettre en place un pipeline de données complet avec les technologies Big Data les plus courantes. Vous avez appris à :
- Configurer et utiliser un cluster Hadoop via Docker
- Produire et consommer des messages avec Kafka
- Stocker des données dans HDFS
- Analyser des données avec Spark

Ces compétences sont essentielles pour travailler sur des projets Big Data dans des environnements professionnels.