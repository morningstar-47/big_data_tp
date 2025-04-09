from confluent_kafka import Producer

def delivery_callback(err, msg):
    if err:
        print(f"Failed to deliver message: {err}")
    else:
        print(f"Message delivered: {msg}")

p = Producer({'bootstrap.servers': 'localhost:9092'})
p.produce('data_stream', 'Premier message - Introduction à Kafka', callback=delivery_callback)
p.produce('data_stream', 'Deuxième message - Kafka est un système de messagerie distribué', callback=delivery_callback)
p.produce('data_stream', 'Troisième message - Utilisé pour le traitement de flux de données', callback=delivery_callback)
p.produce('data_stream', 'Quatrième message - Offre une haute disponibilité', callback=delivery_callback)
p.produce('data_stream', 'Cinquième message - Permet le traitement en temps réel', callback=delivery_callback)
p.produce('data_stream', 'Sixième message - S\'intègre bien avec Hadoop et Spark', callback=delivery_callback)
p.produce('data_stream', 'Septième message - Utilisé pour les pipelines de données', callback=delivery_callback)
p.produce('data_stream', 'Huitième message - Conçu pour la scalabilité horizontale', callback=delivery_callback)
p.produce('data_stream', 'Neuvième message - Les données sont organisées en topics', callback=delivery_callback)
p.produce('data_stream', 'Dixième message - Fin de la démonstration', callback=delivery_callback)
p.flush()