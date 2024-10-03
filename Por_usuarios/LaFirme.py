import numpy as np
import pandas as pd
import os
from scipy.sparse import csr_matrix, coo_matrix, save_npz, load_npz

def distancia_manhattan_np(user1, user2):
    mask = (user1 != 0) & (user2 != 0)
    dist = np.sum(np.abs(user1[mask] - user2[mask]))
    return dist if not np.isnan(dist) else float('nan')

def distancia_euclidiana_np(user1, user2):
    mask = (user1 != 0) & (user2 != 0)
    dist = np.sqrt(np.sum((user1[mask] - user2[mask]) ** 2))
    return dist if not np.isnan(dist) else float('nan')

def similitud_coseno_np(user1, user2):
    mask = (user1 != 0) & (user2 != 0)
    user1 = user1[mask]
    user2 = user2[mask]
    dot_product = np.dot(user1, user2)
    norm_user1 = np.linalg.norm(user1)
    norm_user2 = np.linalg.norm(user2)
    cos_sim = dot_product / (norm_user1 * norm_user2) if norm_user1 != 0 and norm_user2 != 0 else float('nan')
    return cos_sim if not np.isnan(cos_sim) else float('nan')

def similitud_pearson_np(user1, user2):
    mask = (user1 != 0) & (user2 != 0)
    if np.sum(mask) == 0:
        return float('nan')
    user1 = user1[mask]
    user2 = user2[mask]
    num = np.sum((user1 - np.mean(user1)) * (user2 - np.mean(user2)))
    den = np.sqrt(np.sum((user1 - np.mean(user1)) ** 2)) * np.sqrt(np.sum((user2 - np.mean(user2)) ** 2))
    pearson_corr = num / den if den != 0 else float('nan')
    return pearson_corr if not np.isnan(pearson_corr) else float('nan')

# Algoritmo KNN modificado para agregar la restricción de mínimo 5 películas calificadas en común
def algoritmoknn(k, distancia, usuario_comparado, ratings_matrix):
    k = int(k)
    usuario_idx = usuario_comparado - 1  # Índice del usuario
    usuario_data = ratings_matrix[usuario_idx].toarray().flatten()  # Convertir sparse a dense array

    distancias = []

    for i in range(ratings_matrix.shape[0]):
        if i != usuario_idx:
            usuario2_data = ratings_matrix[i].toarray().flatten()  # Convertir sparse a dense array

            # Calcular cuántas películas en común ha calificado el vecino y el usuario
            calificaciones_en_comun = np.sum((usuario_data != 0) & (usuario2_data != 0))

            # Verificar si el vecino ha calificado al menos 5 películas que el usuario ha calificado
            if calificaciones_en_comun < 5:
                continue  # Ignorar este vecino si tiene menos de 5 calificaciones en común

            # Calcular la distancia/similitud según la métrica seleccionada
            if distancia == 'manhattan':
                dist = float(distancia_manhattan_np(usuario_data, usuario2_data))
            elif distancia == 'euclidiana':
                dist = float(distancia_euclidiana_np(usuario_data, usuario2_data))
            elif distancia == 'pearson':
                dist = float(similitud_pearson_np(usuario_data, usuario2_data))
            elif distancia == 'coseno':
                dist = float(similitud_coseno_np(usuario_data, usuario2_data))
            else:
                print("Métrica de distancia no reconocida. Por favor, use 'manhattan', 'euclidiana', 'pearson' o 'coseno'.")
                return

            if not np.isnan(dist):
                dist = round(dist, 10)
                distancias.append((i + 1, dist))  # Agregar a la lista si no es NaN

    if distancia in ['manhattan', 'euclidiana']:
        distancias.sort(key=lambda x: x[1])  # Ordenar de menor a mayor
    else:
        distancias.sort(key=lambda x: -x[1])  # Ordenar de mayor a menor para Pearson y Coseno

    return distancias[:k]

# Función para leer archivos .dat y crear matriz dispersa
def leer_dat(filepath):
    df = pd.read_csv(filepath, sep='::', engine='python', names=['userId', 'movieId', 'rating', 'timestamp'])
    return df

# Función para leer archivo de películas
def leer_peliculas(filepath):
    df = pd.read_csv(filepath, sep=',', names=['movieId', 'title', 'genres'], skiprows=1)
    peliculas = dict(zip(df['movieId'], df['title']))
    return peliculas

# Función para predecir calificación
def predecir_calificacion(usuario, pelicula, k, distancia, ratings_matrix, puntaje_minimo=3):
    # Ejecutar el algoritmo K-NN para encontrar los k vecinos más cercanos
    vecinos = algoritmoknn(k, distancia, usuario, ratings_matrix)
    
    # Obtener las calificaciones del usuario
    usuario_idx = usuario - 1
    usuario_data = ratings_matrix[usuario_idx].toarray().flatten()

    if usuario_data[pelicula - 1] != 0:
        print(f"El usuario {usuario} ya ha calificado la película {pelicula}.")
        return None

    # Variables para acumular la suma ponderada de las calificaciones y las distancias
    suma_ponderada = 0
    suma_distancias = 0
    vecinos_validos = 0  # Contar cuántos vecinos cumplen con la restricción

    for vecino, dist in vecinos:
        vecino_data = ratings_matrix[vecino - 1].toarray().flatten()

        if vecino_data[pelicula - 1] != 0:  # Solo considerar si el vecino ha calificado la película
            calificacion_vecino = vecino_data[pelicula - 1]
            if calificacion_vecino >= puntaje_minimo:  # Aplicar la restricción de calificación mínima
                peso = 1 / dist if dist != 0 else 0  # Evitar división por cero
                suma_ponderada += calificacion_vecino * peso
                suma_distancias += peso
                vecinos_validos += 1

    if suma_distancias == 0:
        print(f"Ninguno de los vecinos válidos ha calificado la película {pelicula}.")
        return None

    # Calcular la predicción
    calificacion_predicha = suma_ponderada / suma_distancias
    return round(calificacion_predicha, 2), vecinos_validos

sparse_file = 'matriz_creada.npz'

# Verificar si el archivo disperso existe
if os.path.exists(sparse_file):
    ratings_matrix = load_npz(sparse_file)
    print("Matriz dispersa cargada desde el archivo .npz")
else:
    #df = leer_dat('ratings1.dat')
    df = pd.read_csv('ratings100.csv')
    
    # Crear una matriz dispersa directamente
    matriz_dispersa = coo_matrix((df['rating'], (df['userId'] - 1, df['movieId'] - 1)))

    # Convertir a formato CSR para mayor eficiencia
    ratings_matrix = matriz_dispersa.tocsr()

    # Guardar la matriz dispersa en un archivo .npz
    save_npz(sparse_file, ratings_matrix)
    print("Matriz dispersa generada y guardada en archivo .npz")

# Cargar archivo de películas
peliculas_file = 'movies100.csv'
peliculas = leer_peliculas(peliculas_file)

#Menu
print("\nSeleccione una opción:")
print("1. Comparar dos usuarios específicos")
print("2. Comparar un usuario con todos los demás")
print("3. Algoritmo K-NN")
print("4. Predecir calificación de una película no calificada por el usuario usando K-NN")

opcion = input("\nIngrese el número de la opción seleccionada: ")

if opcion == "1":
    usuario1 = int(input("Ingrese el ID del primer usuario: "))
    usuario2 = int(input("Ingrese el ID del segundo usuario: "))

    user_data1 = ratings_matrix[usuario1 - 1].toarray().flatten()  
    user_data2 = ratings_matrix[usuario2 - 1].toarray().flatten()

    dist_manhattan = round(distancia_manhattan_np(user_data1, user_data2), 10)
    dist_euclidiana = round(distancia_euclidiana_np(user_data1, user_data2), 10)
    pearson = round(similitud_pearson_np(user_data1, user_data2), 10)
    coseno = round(similitud_coseno_np(user_data1, user_data2), 10)

    print(f"\nResultados de la comparación entre {usuario1} y {usuario2}:")
    print(f"Manhattan: {dist_manhattan}")
    print(f"Euclidiana: {dist_euclidiana}")
    print(f"Pearson: {pearson}")
    print(f"Coseno: {coseno}")

elif opcion == "2":
    usuario = int(input("Ingrese el ID del usuario a comparar: "))
    distancia = input("Seleccione la distancia ('manhattan', 'euclidiana', 'pearson', 'coseno'): ")

    resultados = algoritmoknn(10, distancia, usuario, ratings_matrix)

    print(f"\nResultados de la comparación con el usuario {usuario}:")
    for vecino, dist in resultados:
        print(f"Usuario {vecino}, Distancia: {dist}")

elif opcion == "3":
    usuario = int(input("Ingrese el ID del usuario a comparar: "))
    distancia = input("Seleccione la distancia ('manhattan', 'euclidiana', 'pearson', 'coseno'): ")
    k = int(input("Ingrese el valor de k: "))

    resultados = algoritmoknn(k, distancia, usuario, ratings_matrix)

    print(f"\n{k} vecinos más cercanos al usuario {usuario}:")
    for vecino, dist in resultados:
        print(f"Usuario {vecino}, Distancia: {dist}")

elif opcion == "4":
    usuario = int(input("Ingrese el ID del usuario: "))
    pelicula = int(input("Ingrese el ID de la película: "))
    distancia = input("Seleccione la distancia ('manhattan', 'euclidiana', 'pearson', 'coseno'): ")
    k = int(input("Ingrese el valor de k: "))
    puntaje_minimo = int(input("Ingrese el puntaje mínimo para considerar las calificaciones de los vecinos: "))

    prediccion, vecinos_validos = predecir_calificacion(usuario, pelicula, k, distancia, ratings_matrix, puntaje_minimo)

    if prediccion is not None:
        print(f"\nPredicción de calificación para la película {pelicula} por el usuario {usuario}: {prediccion}")
        print(f"Vecinos válidos considerados: {vecinos_validos}")
    else:
        print(f"No se pudo realizar la predicción para la película {pelicula}.")
