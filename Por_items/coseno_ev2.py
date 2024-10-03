import math
import pandas as pd

# Parámetros para normalización y desnormalización
Max_R = 5
Min_R = 1

# Función para normalizar
def normalize(rating, Min_R, Max_R):
    return (2 * (rating - Min_R) - (Max_R - Min_R)) / (Max_R - Min_R)

# Función para desnormalizar
def denormalize(normalized_rating, Min_R, Max_R):
    return 0.5 * ((normalized_rating + 1) * (Max_R - Min_R)) + Min_R

# Función para calcular la similitud ajustada entre dos ítems
def adjusted_cosine_similarity(item1, item2, user_ratings, averages):
    numerator = 0
    denominator1 = 0
    denominator2 = 0

    # Calcular la similitud solo para los usuarios que calificaron ambos ítems
    for user, ratings in user_ratings.items():
        if item1 in ratings and item2 in ratings:
            adj_rating1 = ratings[item1] - averages[user]
            adj_rating2 = ratings[item2] - averages[user]
            print(f"Usuario '{user}': ({item1}: {ratings[item1]}, {item2}: {ratings[item2]}) -> "
                  f"({adj_rating1:.4f}, {adj_rating2:.4f})")

            numerator += adj_rating1 * adj_rating2
            denominator1 += adj_rating1 ** 2
            denominator2 += adj_rating2 ** 2

    if denominator1 == 0 or denominator2 == 0:
        return 0  # Para manejar la división por cero

    return numerator / (math.sqrt(denominator1) * math.sqrt(denominator2))

# Función para predecir las valoraciones sin calcular toda la matriz de similitud
def predict_rating_dynamic(user, target_item, user_ratings, averages):
    numerator = 0
    denominator = 0
    
    print(f"\nCalculando predicción para {user} con el ítem '{target_item}':")
    print(f"Promedio del usuario '{user}': {averages[user]:.4f}")

    # Usamos los ítems que ya calificó el usuario
    for item, rating in user_ratings[user].items():
        if item != target_item:
            # Calcular la similitud dinámicamente solo cuando sea necesario
            similarity = adjusted_cosine_similarity(item, target_item, user_ratings, averages)
            normalized_rating = normalize(rating, Min_R, Max_R)
            print(f"Comparando {target_item} con {item}: Similitud = {similarity:.4f}, "
                  f"Rating {user} sobre {item} = {rating}, "
                  f"Rating normalizado = {normalized_rating:.4f}")
            numerator += similarity * normalized_rating  # Usamos la calificación normalizada
            denominator += abs(similarity)

    if denominator == 0:
        return None  # No se puede predecir

    # Imprimir el numerador y denominador antes de desnormalizar
    print(f"Numerador antes de desnormalizar: {numerator:.4f}")
    print(f"Denominador: {denominator:.4f}")

    # Calculamos la predicción normalizada
    prediction_normalized = numerator / denominator
    # Desnormalizamos la predicción
    prediction = denormalize(prediction_normalized, Min_R, Max_R)
    
    print(f"Predicción normalizada antes de desnormalizar: {prediction_normalized:.4f}")
    print(f"Predicción final desnormalizada: {prediction:.4f}")
    
    return prediction

# Función para cargar datos desde un CSV y convertirlos en una matriz dispersa
def load_ratings_from_csv(file_path):
    df = pd.read_csv(file_path)
    user_ratings = {}
    
    # Crear un diccionario donde cada usuario tiene un diccionario de calificaciones
    for _, row in df.iterrows():
        user_id = f'{row["userId"]}'  # Opcional: agregar un prefijo para identificar usuarios
        movie_id = f'{row["movieId"]}'  # Opcional: agregar un prefijo para identificar películas
        rating = row["rating"]
        
        if user_id not in user_ratings:
            user_ratings[user_id] = {}
        user_ratings[user_id][movie_id] = rating

    return user_ratings

# Función para calcular la similitud entre dos películas
def calculate_similarity_between_items(item1, item2, user_ratings, averages):
    similarity = adjusted_cosine_similarity(item1, item2, user_ratings, averages)
    print(f"\nSimilitud ajustada entre '{item1}' y '{item2}': {similarity:.4f}")
    return similarity

# Definir el nombre del archivo CSV
file_path = "ratings.csv"  # Cambia esto al nombre de tu archivo CSV

# Cargar los datos del CSV
user_ratings = load_ratings_from_csv(file_path)

# Cálculo del promedio de cada usuario
averages = {user: sum(ratings.values()) / len(ratings.values()) for user, ratings in user_ratings.items()}

# Menú para que el usuario elija entre predicción y similitud
print("\nSeleccione una opción:")
print("1. Predecir una calificación para un ítem")
print("2. Calcular la similitud entre dos ítems")

opcion = input("\nIngrese el número de la opción deseada: ")

if opcion == "1":
    # Pedir entrada al usuario para la predicción
    input_user = input("\nIngrese el nombre del usuario: ")
    input_item = input("Ingrese el nombre del ítem para predecir su valoración: ")

    # Verificar si el usuario y el ítem existen en los datos
    items = list(set(item for ratings in user_ratings.values() for item in ratings))  # Lista de todos los ítems
    if input_user in user_ratings and input_item in items:
        prediction = predict_rating_dynamic(input_user, input_item, user_ratings, averages)
        
        if prediction is not None:
            print(f"\nPredicción: {input_user} probablemente le dará a {input_item} una calificación de {prediction:.4f}")
        else:
            print(f"\nNo se puede predecir la calificación de {input_user} para {input_item}")
    else:
        print("\nUsuario o ítem no encontrados en los datos.")
elif opcion == "2":
    # Pedir entrada al usuario para calcular la similitud entre dos ítems
    input_item1 = input("\nIngrese el nombre del primer ítem: ")
    input_item2 = input("Ingrese el nombre del segundo ítem: ")

    # Verificar si ambos ítems existen en los datos
    items = list(set(item for ratings in user_ratings.values() for item in ratings))  # Lista de todos los ítems
    if input_item1 in items and input_item2 in items:
        similarity = calculate_similarity_between_items(input_item1, input_item2, user_ratings, averages)
    else:
        print("\nUno o ambos ítems no se encontraron en los datos.")
else:
    print("\nOpción no válida.")
