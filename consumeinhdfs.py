from confluent_kafka import Consumer, KafkaError
from hdfs import InsecureClient

# Création du client HDFS
client = InsecureClient('http://localhost:9870')

# Création du répertoire dans HDFS
try:
    client.makedirs('/root/data')
    print("Répertoire HDFS '/root/data' créé ou déjà existant")
except Exception as e:
    print(f"Erreur lors de la création du répertoire: {e}")

# Configuration du consumer Kafka
c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my_group',
    'auto.offset.reset': 'earliest'
})

# Abonnement au topic
c.subscribe(['data_stream'])

print("Démarrage du consumer et écriture dans HDFS...")
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

        # Afficher le message reçu
        message = msg.value().decode('utf-8')
        print(f'Message reçu et écrit dans HDFS: {message}')
        
        # Écrire les données dans un fichier sur HDFS
        # Utiliser append=True pour ajouter au fichier plutôt que de l'écraser à chaque message
        try:
            with client.write('/root/data/data_stream.txt', append=True) as writer:
                writer.write(message + '\n')
            messages_count += 1
            print(f"Total des messages écrits: {messages_count}")
        except Exception as e:
            print(f"Erreur lors de l'écriture dans HDFS: {e}")
            
except KeyboardInterrupt:
    print("Programme arrêté par l'utilisateur")
finally:
    # Fermer le consumer
    c.close()
    print("Consumer fermé")