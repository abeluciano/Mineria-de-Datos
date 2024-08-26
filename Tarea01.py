import math

def manhattan(user1, user2):
    distance = 0
    for artista in user1:
        if artista in user2 and user1[artista] != "-" and user2[artista] != "-":
            distance += abs(user1[artista] - user2[artista])
    return distance

def euclidean(user1, user2):
    distance = 0
    for artista in user1:
        if artista in user2 and user1[artista] != "-" and user2[artista] != "-":
            distance += (user1[artista] - user2[artista]) ** 2
    return math.sqrt(distance)

angelica = {
    "Blues Traveler": 3.5, "Broken Bells": 2, "Deadmau5": "-", 
    "Norah Jones": 4.5, "Phoenix": 5, "Slightly Stoopid": 1.5, 
    "The Strokes": 2.5, "Vampire Weekend": 2
}

bill = {
    "Blues Traveler": 2, "Broken Bells": 3.5, "Deadmau5": 4, 
    "Norah Jones": "-", "Phoenix": 2, "Slightly Stoopid": 3.5, 
    "The Strokes": "-", "Vampire Weekend": 3
}

chan = {
    "Blues Traveler": 5, "Broken Bells": 1, "Deadmau5": 1, 
    "Norah Jones": "-", "Phoenix": 3, "Slightly Stoopid": 5, 
    "The Strokes": "-", "Vampire Weekend": "-"
}

dan = {
    "Blues Traveler": 3, "Broken Bells": 4, "Deadmau5": 4.5, 
    "Norah Jones": "-", "Phoenix": 3, "Slightly Stoopid": 4.5, 
    "The Strokes": 4, "Vampire Weekend": 2
}

hailey = {
    "Blues Traveler": "-", "Broken Bells": 4, "Deadmau5": 4, 
    "Norah Jones": 4, "Phoenix": 5, "Slightly Stoopid": "-", 
    "The Strokes": 4, "Vampire Weekend": 1
}

jordyn = {
    "Blues Traveler": "-", "Broken Bells": 4.5, "Deadmau5": 4, 
    "Norah Jones": 5, "Phoenix": 5, "Slightly Stoopid": 4.5, 
    "The Strokes": 4, "Vampire Weekend": 4
}

sam = {
    "Blues Traveler": 5, "Broken Bells": 2, "Deadmau5": "-", 
    "Norah Jones": 3, "Phoenix": 5, "Slightly Stoopid": 4.5, 
    "The Strokes": 4, "Vampire Weekend": "-"
}

veronica = {
    "Blues Traveler": 3, "Broken Bells": "-", "Deadmau5": "-", 
    "Norah Jones": 5, "Phoenix": 4, "Slightly Stoopid": 2.5, 
    "The Strokes": 3, "Vampire Weekend": "-"
}

usuarios = {
    "Angelica": angelica,
    "Bill": bill,
    "Chan": chan,
    "Dan": dan,
    "Hailey": hailey,
    "Jordyn": jordyn,
    "Sam": sam,
    "Veronica": veronica
}


usuario_comparado = input("Ingrese el nombre del usuario a comparar: ")


if usuario_comparado not in usuarios:
    print("El usuario ingresado no existe.")
else:
    menor_distancia_manhattan = float('inf')
    menor_distancia_euclidiana = float('inf')
    usuario_manhattan = None
    usuario_euclidiana = None

    for nombre, usuario in usuarios.items():
        if nombre != usuario_comparado: 
            dist_manhattan = manhattan(usuarios[usuario_comparado], usuario)
            dist_euclidiana = euclidean(usuarios[usuario_comparado], usuario)

            if dist_manhattan < menor_distancia_manhattan:
                menor_distancia_manhattan = dist_manhattan
                usuario_manhattan = nombre

            if dist_euclidiana < menor_distancia_euclidiana:
                menor_distancia_euclidiana = dist_euclidiana
                usuario_euclidiana = nombre

    print(f"Para {usuario_comparado}:")
    print(f"Distancia de Manhattan más pequeña: {menor_distancia_manhattan} con {usuario_manhattan}")
    print(f"Distancia Euclidiana más pequeña: {menor_distancia_euclidiana} con {usuario_euclidiana}")
