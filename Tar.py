import math
import pandas as pd

#isna= si es un Nan
#zip= union, combinacion, etc
def distanciaManhattan(user1, user2):
    distancia = 0
    for val1, val2 in zip(user1, user2):
        if not pd.isna(val1) and not pd.isna(val2):
            distancia += abs(val1 - val2)
    return distancia

def idstanciaEucleriana(user1, user2):
    distancia = 0
    for val1, val2 in zip(user1, user2):
        if not pd.isna(val1) and not pd.isna(val2):
            distancia += (val1 - val2) ** 2
    return math.sqrt(distancia)

def aproximacionPearson(user1, user2):
    filtroNan = [(r1, r2) for r1, r2 in zip(user1, user2) if not pd.isna(r1) and not pd.isna(r2)]


    n = len(filtroNan)
    if n == 0:
        return 0
    
    #sumatoria de x, y
    sum1 = sum(r1 for r1, r2 in filtroNan)
    sum2 = sum(r2 for r1, r2 in filtroNan)
    
    #sumatoria de los cuadrados de x, y
    sum1Sq = sum(pow(r1, 2) for r1, r2 in filtroNan)
    sum2Sq = sum(pow(r2, 2) for r1, r2 in filtroNan)
    
    #sumatoria del producto de x,y
    pSum = sum(r1 * r2 for r1, r2 in filtroNan)
    
    #numerador
    num = pSum - (sum1 * sum2 / n)
    #deniminador
    den = math.sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    
    if den == 0:
        return 0
    #resultado
    return num / den

def similitudCoseno(user1, user2):
    sum_xy = sum(r1 * r2 for r1, r2 in zip(user1, user2) if not pd.isna(r1) and not pd.isna(r2))
    sum_x2 = math.sqrt(sum(pow(r1, 2) for r1 in user1 if not pd.isna(r1)))
    sum_y2 = math.sqrt(sum(pow(r2, 2) for r2 in user2 if not pd.isna(r2)))
    
    if sum_x2 == 0 or sum_y2 == 0:
        return 0
    
    return sum_xy / (sum_x2 * sum_y2)


df = pd.read_csv('ratings.csv', index_col=0, delimiter=',', decimal=',')
#df = pd.read_csv('Movie_Ratings.csv', index_col=0, delimiter=',', decimal=',')

print(df)

print("\nSeleccione una opción:")
print("1. Comparar dos usuarios específicos")
print("2. Comparar un usuario con todos los demás")

opcion = input("\nIngrese el número de la opción seleccionada: ")
if opcion == "1":

    usuario1 = input("Ingrese el nombre del primer usuario: ")
    usuario2 = input("Ingrese el nombre del segundo usuario: ")

    if usuario1 not in df.columns or usuario2 not in df.columns:
        print("Uno o ambos usuarios no existen.")
    else:
        user_data1 = df[usuario1].astype(float)
        user_data2 = df[usuario2].astype(float)

        dist_manhattan = distanciaManhattan(user_data1, user_data2)
        dist_euclidiana = idstanciaEucleriana(user_data1, user_data2)
        pearson = aproximacionPearson(user_data1, user_data2)
        coseno = similitudCoseno(user_data1, user_data2)

        print(f"\nResultados de la comparación entre {usuario1} y {usuario2}:")
        print(f"Distancia Manhattan: {dist_manhattan}")
        print(f"Distancia Euclidiana: {dist_euclidiana}")
        print(f"Correlación de Pearson: {pearson}")
        print(f"Similitud del Coseno: {coseno}")


elif opcion == "2":
    
    usuario_comparado = input("Ingrese el nombre del usuario a comparar: ") 

    if usuario_comparado not in df.columns:
        print("El usuario ingresado no existe.")
    else:
        menor_distancia_manhattan = float('inf')
        menor_distancia_euclidiana = float('inf')
        mayor_pearson = float('-inf')
        mayor_coseno = float('-inf')
        
        usuario_manhattan = None
        usuario_euclidiana = None
        usuario_pearson = None
        usuario_coseno = None

        usuario_data = df[usuario_comparado].astype(float)

        for nombre in df.columns:
            if nombre != usuario_comparado:
                usuario2_data = df[nombre].astype(float)
                
                dist_manhattan = distanciaManhattan(usuario_data, usuario2_data)
                dist_euclidiana = idstanciaEucleriana(usuario_data, usuario2_data)
                pearson = aproximacionPearson(usuario_data, usuario2_data)
                coseno = similitudCoseno(usuario_data, usuario2_data)
                
                if dist_manhattan < menor_distancia_manhattan:
                    menor_distancia_manhattan = dist_manhattan
                    usuario_manhattan = nombre
                    
                if dist_euclidiana < menor_distancia_euclidiana:
                    menor_distancia_euclidiana = dist_euclidiana
                    usuario_euclidiana = nombre
                    
                if pearson > mayor_pearson:
                    mayor_pearson = pearson
                    usuario_pearson = nombre
                    
                if coseno > mayor_coseno:
                    mayor_coseno = coseno
                    usuario_coseno = nombre

        print(f"\nResultados para {usuario_comparado}:")
        print(f"Distancia de Manhattan más pequeña: {menor_distancia_manhattan} con {usuario_manhattan}")
        print(f"Distancia Euclidiana más pequeña: {menor_distancia_euclidiana} con {usuario_euclidiana}")
        print(f"Mayor correlación de Pearson: {mayor_pearson} con {usuario_pearson}")
        print(f"Mayor similitud de coseno: {mayor_coseno} con {usuario_coseno}")
