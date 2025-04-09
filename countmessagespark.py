from pyspark.sql import SparkSession

# Création de la session Spark
spark = SparkSession.builder \
    .appName("Analyse de données Kafka") \
    .getOrCreate()

# Utilisation du chemin correct où nous savons que le fichier existe
# Remarque: nous utilisons le chemin complet avec hdfs:// et le port 9000 (port HDFS standard)
df = spark.read.text("hdfs://hadoop-master:9000/user/root/data/data_stream.txt")

# Afficher les premières lignes pour vérification
print("Aperçu des données:")
df.show(5, truncate=False)

# Effectuer un comptage simple
word_count = df.count()
print("Nombre total de messages:", word_count)

# Pour un comptage de mots plus détaillé (optionnel)
from pyspark.sql.functions import explode, split, col

# Diviser le texte en mots et compter chaque mot
words_df = df.select(explode(split(col("value"), " ")).alias("word"))
word_counts = words_df.groupBy("word").count().orderBy("count", ascending=False)

print("Top 10 des mots les plus fréquents:")
word_counts.show(10)

# Arrêter la session Spark
spark.stop()