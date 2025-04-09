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
            
            # Afficher le contenu actuel du fichier HDFS pour vérification
            print("Contenu actuel du fichier HDFS:")
            cat_cmd = f"hdfs dfs -cat {hdfs_path}"
            output = subprocess.check_output(cat_cmd, shell=True).decode()
            print(output)
            
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
        print(f"Fichier temporaire {temp_file} supprimé")