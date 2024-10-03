import csv
from collections import defaultdict

# Función para leer el CSV y crear la matriz de calificaciones
def load_ratings_from_csv(file_path):
    data = defaultdict(dict)
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            user_id = int(row['userId'])
            movie_id = int(row['movieId'])
            rating = float(row['rating'])
            data[user_id][movie_id] = rating
    return data

# Función para leer el archivo de películas y crear un diccionario {movieId: title}
def load_movies_from_csv(file_path):
    movies = {}
    with open(file_path, 'r', encoding='utf-8') as file:  # Especificamos utf-8
        reader = csv.DictReader(file)
        for row in reader:
            movie_id = int(row['movieId'])
            title = row['title']
            movies[movie_id] = title
    return movies

# Función para calcular las desviaciones y frecuencias
def compute_deviations(data):
    deviations = defaultdict(lambda: defaultdict(float))
    frequencies = defaultdict(lambda: defaultdict(int))
    
    # Recorremos las calificaciones de cada usuario
    for user, ratings in data.items():
        # Para cada par de ítems en las calificaciones del usuario
        for (item1, rating1) in ratings.items():
            for (item2, rating2) in ratings.items():
                if item1 != item2:
                    # Sumar la diferencia de las calificaciones
                    frequencies[item1][item2] += 1
                    deviations[item1][item2] += (rating1 - rating2)

    # Promediar las desviaciones dividiendo por las frecuencias
    for item1, related_ratings in deviations.items():
        for item2 in related_ratings:
            deviations[item1][item2] /= frequencies[item1][item2]

    return deviations, frequencies

# Función para hacer predicciones usando Slope One
def slope_one_prediction(user_ratings, deviations, frequencies, movies, specific_item=None):
    recommendations = defaultdict(float)
    freqs = defaultdict(int)

    # Para almacenar los detalles del numerador y denominador
    details = {}

    # Para cada ítem calificado por el usuario
    for (item, rating) in user_ratings.items():
        # Consideramos todos los ítems que tienen desviación calculada con respecto al ítem actual
        for (diff_item, dev) in deviations.items():
            # Si estamos prediciendo un ítem específico, solo calculamos para ese
            if specific_item is not None:
                if diff_item != specific_item or item not in dev:
                    continue  # Saltamos si no es el ítem específico o no hay desviación calculada
            if item in dev and (diff_item not in user_ratings or diff_item == specific_item):
                # Calcular contribución al numerador
                contrib_numerator = (dev[item] + rating) * frequencies[diff_item][item]
                contrib_frequency = frequencies[diff_item][item]

                # Sumar contribución al numerador y al denominador
                recommendations[diff_item] += contrib_numerator
                freqs[diff_item] += contrib_frequency

                # Guardar los detalles
                if diff_item not in details:
                    details[diff_item] = {'numerator': 0, 'denominator': 0}
                details[diff_item]['numerator'] += contrib_numerator
                details[diff_item]['denominator'] += contrib_frequency

                # Imprimir detalles de la contribución
                print(f"\nContribución para el ítem '{movies.get(diff_item, diff_item)}' desde '{movies.get(item, item)}':")
                print(f"  dev({diff_item}, {item}) = {dev[item]}")
                print(f"  Calificación del usuario para {movies.get(item, item)} = {rating}")
                print(f"  Frecuencia de {item} y {diff_item} = {frequencies[diff_item][item]}")
                print(f"  Contribución al numerador: ({dev[item]} + {rating}) * {frequencies[diff_item][item]} = {contrib_numerator}")

    # Calcular el promedio ponderado y mostrar el resultado final
    final_recommendations = {}
    for item in recommendations:
        if specific_item is None or item == specific_item:  # Predicción general o específica
            final_recommendations[item] = recommendations[item] / freqs[item]
            # Imprimir los detalles del numerador y denominador
            print(f"\nResultado final para '{movies.get(item, item)}':")
            print(f"  Numerador total: {details[item]['numerator']}")
            print(f"  Denominador total: {details[item]['denominator']}")
            print(f"  Predicción final: {final_recommendations[item]}")
    
    return final_recommendations

# Función para calcular la similitud entre dos ítems
def item_similarity(item1, item2, deviations, frequencies, movies):
    if item1 in deviations and item2 in deviations[item1]:
        deviation = deviations[item1][item2]
        freq = frequencies[item1][item2]
        
        print(f"\nSimilitud entre '{movies.get(item1, item1)}' y '{movies.get(item2, item2)}':")
        print(f"  Desviación promedio: {deviation:.4f}")
        print(f"  Frecuencia de comparación: {freq}")
        return deviation, freq
    else:
        print(f"No hay suficientes datos para calcular la similitud entre '{movies.get(item1, item1)}' y '{movies.get(item2, item2)}'.")
        return None, None

# Leer los CSV
ratings_file = 'ratings.csv'  
movies_file = 'movies100.csv'  

data = load_ratings_from_csv(ratings_file)
movies = load_movies_from_csv(movies_file)

# Calcular las desviaciones y frecuencias
deviations, frequencies = compute_deviations(data)

# Menú 
print("\nSeleccione una opción:")
print("1. Hacer predicciones para un usuario")
print("2. Calcular la similitud entre dos ítems")

opcion = input("\nIngrese el número de la opción deseada: ")

if opcion == "1":
    user_id = int(input("\nIngresa el ID del usuario para el cual deseas hacer predicciones: "))

    # Verificar si el usuario tiene calificaciones registradas
    if user_id in data:
        user_ratings = data[user_id]
        
        # Opción para predicciones
        option = input("\n¿Deseas hacer predicciones para todos los ítems no calificados? (S/N): ").lower()
        
        if option == 's':
            recommendations = slope_one_prediction(user_ratings, deviations, frequencies, movies)

            
            print(f"\nPredicciones para el usuario {user_id}:")
            for item, rating in recommendations.items():
                print(f"Película {movies.get(item, item)}: {rating:.2f}")
        
        else:
            item_id = int(input("Ingresa el ID del ítem (película) para el cual deseas hacer la predicción: "))
            
            if item_id in user_ratings:
                print(f"El usuario {user_id} ya ha calificado la película '{movies.get(item_id, item_id)}' con un puntaje de {user_ratings[item_id]}")
            else:
                recommendations = slope_one_prediction(user_ratings, deviations, frequencies, movies, specific_item=item_id)

                # Imprimir la predicción final para el ítem especificado
                if item_id in recommendations:
                    print(f"\nPredicción para '{movies.get(item_id, item_id)}': {recommendations[item_id]:.2f}")
                else:
                    print(f"No hay suficientes datos para hacer una predicción para el ítem '{movies.get(item_id, item_id)}'.")
    else:
        print(f"El usuario {user_id} no tiene calificaciones registradas.")

elif opcion == "2":
    item1 = int(input("\nIngresa el ID del primer ítem (película): "))
    item2 = int(input("Ingresa el ID del segundo ítem (película): "))

    # Calcular la similitud entre los dos ítems
    item_similarity(item1, item2, deviations, frequencies, movies)

else:
    print("\nOpción no válida.")
