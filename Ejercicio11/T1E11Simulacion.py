#importar librerías
import numpy as np


#Funciones para generar variables aleatorias que simulen los tiempos de la simulación

def var_expo(media): # Generar una variable aleatorias exponencial
    return np.random.exponential(1/media)

def var_uniforme(rango_inf, rango_sup):# crear variable aleatoria uniforme para el tiempo de servicio de los clientes de tipo 2
    return np.random.uniform(rango_inf, rango_sup)

def var_discreta_tipo_cliente(prob_de_cliente_1, prob_de_cliente_2):# crear variable aleatoria discreta para determinar el tipo de cliente
    tipos_cliente = [1, 2]
    probabilidades = [prob_de_cliente_1, prob_de_cliente_2]
    return np.random.choice(tipos_cliente, p=probabilidades)


# Función que lleva el control del área de personas en cada cola
def actualiza_area_num_en_q():
    global tiempo_ultimo_evento, area_num_en_q1, area_num_en_q2

    tiempo_desde_ultimo_evento = tiempo_sim - tiempo_ultimo_evento # Se actualizan los tiempos referentes al último evento
    tiempo_ultimo_evento = tiempo_sim

    # Se actualiza el area correspondiente al número de clientes de cada tipo
    area_num_en_q1 += clientes_tipo1_en_cola * tiempo_desde_ultimo_evento 
    area_num_en_q2 += clientes_tipo2_en_cola * tiempo_desde_ultimo_evento


# Simular llegada de cliente
def llegada():
    global tiempo_siguiente_evento, servicios_disponibles_tipo_A, servicios_disponibles_tipo_B, clientes_tipo2_servidores_A_B, clientes_tipo1_en_cola, clientes_tipo2_en_cola, tiempos_llegada_clientes_tipo_1, tiempos_llegada_clientes_tipo_2, clientes_tipo1_servidor_A, clientes_tipo1_servidor_B

    tiempo_siguiente_evento[1] = tiempo_sim + var_expo(media_llegadas) # Agendar la siguiente llegada 
    tipo_cliente_actual = var_discreta_tipo_cliente(prob_de_cliente_1, prob_de_cliente_2) # Determinar el tipo cliente que llegó al sistema 
    # Simular atención al cliente
    if tipo_cliente_actual == 2:
        # Para cliente de tipo 2
        if servicios_disponibles_tipo_A > 0 and servicios_disponibles_tipo_B > 0: #Si un servidor A y el B estan libres
            # Asignar el cliente a servidor tipo A y B
            servicios_disponibles_tipo_A -= 1
            servicios_disponibles_tipo_B -= 1
            tiempo_atencion = var_uniforme(rango_inferior_servicio_clientes2, rango_superior_servicio_clientes2) # Determinar el tiempo de atención para cliente de tipo 2
            tiempo_siguiente_evento[4] = tiempo_sim + tiempo_atencion 
            # sumar tiempo de atención al cliente de tipo 2 en los servidores A y B (para calcular la proporción)
            clientes_tipo2_servidores_A_B += tiempo_atencion
        else: # servidores no disponibles
            clientes_tipo2_en_cola += 1 # Agregar a cola de clientes de tipo 2
            tiempos_llegada_clientes_tipo_2.append(tiempo_sim) # Se registra el tiempo de llegada del cliente
    else:
        # Para cliente tipo 1
        if servicios_disponibles_tipo_A > 0: # Si hay un sevidor A disponible
            servicios_disponibles_tipo_A -= 1  # Asignar a servidor tipo A
            tiempo_atencion = var_expo(media_servicio_clientes1) # Determinar el tiempo de atención para cliente de tipo 1
            tiempo_siguiente_evento[2] = tiempo_sim + tiempo_atencion
            clientes_tipo1_servidor_A += tiempo_atencion # sumar tiempo de atención al cliente de tipo 1 en el servidor A (para calcular la proporción)
        elif servicios_disponibles_tipo_B > 0: # Si solo hay sevidor B disponible
            # Asignar a servidor tipo B
            servicios_disponibles_tipo_B -= 1
            tiempo_atencion = var_expo(media_servicio_clientes1) # Determinar el tiempo de atención para cliente de tipo 1
            tiempo_siguiente_evento[3] = tiempo_sim + tiempo_atencion
            clientes_tipo1_servidor_B += tiempo_atencion  # sumar tiempo de atención al cliente de tipo 1 en el servidor B (para calcular la proporción)
        else: # Ningún servidor disponible
            clientes_tipo1_en_cola += 1 # Agregar a cola de clientes de tipo 1
            tiempos_llegada_clientes_tipo_1.append(tiempo_sim) # Se registra el tiempo de llegada del cliente


# Simular salida de cliente tipo 1 de un servidor A (Se sabe que un servidor A está disponible)
def salida_cliente_tipo1_servidor_A():
    global servicios_disponibles_tipo_A, servicios_disponibles_tipo_B, tiempo_siguiente_evento, clientes_tipo1_en_cola, clientes_tipo2_en_cola, clientes_tipo1_servidor_A, clientes_tipo2_servidores_A_B
    if clientes_tipo2_en_cola > 0 and servicios_disponibles_tipo_B > 0: # Si hay clientes tipo 2 en espera y el servidor B está vacío
        servicios_disponibles_tipo_B -= 1 # Se ocupa el servidor B y se mantiene ocupado uno de los servidores A
        clientes_tipo2_en_cola -= 1 # Se saca un cliente de tipo 2 de la cola
        tiempos_salida_clientes_tipo_2.append(tiempo_sim) # Se registra el tiempo de llegada del cliente
        tiempo_atencion = var_uniforme(rango_inferior_servicio_clientes2, rango_superior_servicio_clientes2) # Determinar el tiempo de atención para cliente de tipo 2
        tiempo_siguiente_evento[4] = tiempo_sim + tiempo_atencion
        # sumar tiempo de atención al cliente de tipo 2 en los servidores A y B (para calcular la proporción)
        clientes_tipo2_servidores_A_B += tiempo_atencion
    elif clientes_tipo1_en_cola > 0: # Si hay clientes de tipo 1 en espera
        clientes_tipo1_en_cola -= 1 # Se saca un cliente de tipo 1 de la cola
        tiempos_salida_clientes_tipo_1.append(tiempo_sim) # Se registra el tiempo de llegada del cliente
        tiempo_atencion = var_expo(media_servicio_clientes1) # Determinar el tiempo de atención para cliente de tipo 1
        tiempo_siguiente_evento[2] = tiempo_sim + tiempo_atencion
        clientes_tipo1_servidor_A += tiempo_atencion # sumar tiempo de atención al cliente de tipo 1 en el servidor A (para calcular la proporción)
    else:
        tiempo_siguiente_evento[2] = 1.0e+30 # Se desconoce el tiempo en el que el próximo evento de tipo 2 sucederá
        servicios_disponibles_tipo_A += 1 # Se establece como libre un servidor A


# Simular salida de cliente tipo 1 de un servidor B (Se sabe que el servidor B está disponible)
def salida_cliente_tipo1_servidor_B():
    global servicios_disponibles_tipo_A, servicios_disponibles_tipo_B, tiempo_siguiente_evento, clientes_tipo1_en_cola, clientes_tipo2_en_cola, clientes_tipo1_servidor_A, clientes_tipo1_servidor_B, clientes_tipo2_servidores_A_B
    if clientes_tipo2_en_cola > 0 and servicios_disponibles_tipo_A > 0: # Si hay clientes tipo 2 en espera y un servidor A está vacío
        servicios_disponibles_tipo_A -= 1 # Se ocupa un servidor A y se mantiene ocupado el servidor B
        clientes_tipo2_en_cola -= 1 # Se saca un cliente de tipo 2 de la cola
        tiempos_salida_clientes_tipo_2.append(tiempo_sim) # Se registra el tiempo de llegada del cliente
        tiempo_atencion = var_uniforme(rango_inferior_servicio_clientes2, rango_superior_servicio_clientes2) # Determinar el tiempo de atención para cliente de tipo 2
        tiempo_siguiente_evento[4] = tiempo_sim + tiempo_atencion
        # sumar tiempo de atención al cliente de tipo 2 en los servidores A y B (para calcular la proporción)
        clientes_tipo2_servidores_A_B += tiempo_atencion
    elif clientes_tipo1_en_cola > 0:  # Si hay clientes de tipo 1 en espera
        if servicios_disponibles_tipo_A > 0: # Si hay servidor de tipo A disponible
            servicios_disponibles_tipo_A -= 1 # Se ocupa el servidor tipo A
            servicios_disponibles_tipo_B += 1 # Se desocupa el servidor tipo B
            clientes_tipo1_en_cola -= 1 # Se saca un cliente de tipo 1 de la cola
            tiempos_salida_clientes_tipo_1.append(tiempo_sim) # Se registra el tiempo de llegada del cliente
            tiempo_atencion = var_expo(media_servicio_clientes1) # Determinar el tiempo de atención para cliente de tipo 1
            tiempo_siguiente_evento[2] = tiempo_sim + tiempo_atencion
            clientes_tipo1_servidor_A += tiempo_atencion # sumar tiempo de atención al cliente de tipo 1 en el servidor A (para calcular la proporción)
        else: # Si solo servidor B está disponible
           clientes_tipo1_en_cola -= 1 # Se saca un cliente de tipo 1 de la cola
           tiempos_salida_clientes_tipo_1.append(tiempo_sim) # Se registra el tiempo de llegada del cliente
           tiempo_atencion = var_expo(media_servicio_clientes1) # Determinar el tiempo de atención para cliente de tipo 1
           tiempo_siguiente_evento[3] = tiempo_sim + tiempo_atencion
           clientes_tipo1_servidor_B += tiempo_atencion # sumar tiempo de atención al cliente de tipo 1 en el servidor B (para calcular la proporción)
    else:
        tiempo_siguiente_evento[3] = 1.0e+30 # Se desconoce el tiempo en el que el próximo evento de tipo 3 sucederá
        servicios_disponibles_tipo_B += 1 # Se establece como libre un servidor B


# Simular salida de cliente tipo 2 (Se sabe que un servidor A y el servido B están disponibles)
def salida_cliente_tipo2():
    global servicios_disponibles_tipo_A, servicios_disponibles_tipo_B, tiempo_siguiente_evento, clientes_tipo1_en_cola, clientes_tipo2_en_cola, clientes_tipo1_servidor_A, clientes_tipo2_servidores_A_B
    if clientes_tipo2_en_cola > 0: # Si hay clientes de tipo 2 en cola se atienden directamente
        clientes_tipo2_en_cola -= 1 # Se saca un cliente de tipo 2 de la cola
        tiempos_salida_clientes_tipo_2.append(tiempo_sim) # Se registra el tiempo de llegada del cliente
        tiempo_atencion = var_uniforme(rango_inferior_servicio_clientes2, rango_superior_servicio_clientes2) # Determinar el tiempo de atención para cliente de tipo 2
        tiempo_siguiente_evento[4] = tiempo_sim + tiempo_atencion
        # sumar tiempo de atención al cliente de tipo 2 en los servidores A y B (para calcular la proporción)
        clientes_tipo2_servidores_A_B += tiempo_atencion
    elif clientes_tipo1_en_cola > 0: # Si hay clientes de tipo 1 en cola
        servicios_disponibles_tipo_B += 1 # El servidor B se establece como vacío
        tiempo_siguiente_evento[4] = 1.0e+30 # Se desconoce el tiempo en el que el próximo evento de tipo 4 sucederá
        clientes_tipo1_en_cola -= 1 # Se saca un cliente de tipo 1 de la cola
        tiempos_salida_clientes_tipo_1.append(tiempo_sim) # Se registra el tiempo de llegada del cliente
        tiempo_atencion = var_expo(media_servicio_clientes1) # Determinar el tiempo de atención para cliente de tipo 1
        tiempo_siguiente_evento[2] = tiempo_sim + tiempo_atencion
        clientes_tipo1_servidor_A += tiempo_atencion # sumar tiempo de atención al cliente de tipo 1 en el servidor A (para calcular la proporción)
    else: # Si no hay clientes en cola se establece un servidor A y el servidor B como vacío
        tiempo_siguiente_evento[4] = 1.0e+30 # Se desconoce el tiempo en el que el próximo evento de tipo 4 sucederá
        servicios_disponibles_tipo_A += 1
        servicios_disponibles_tipo_B += 1


# función que controla el tiempo y determina el tipo del evento que está por ocurrir
def tiempo():
    global tiempo_sim, tipo_evento_siguiente
    tiempo_sim = min(tiempo_siguiente_evento) # Se establece el contador del tiempo en el momento de inicio del evento más cercano
    tipo_evento_siguiente = tiempo_siguiente_evento.index(min(tiempo_siguiente_evento)) # Se determina qué tipo de evento es el más cercano


# Función que extrae la información del archivo in.txt para el desarrollo de la simulación       
def lectura_in():
    global  media_llegadas, media_servicio_clientes1, rango_inferior_servicio_clientes2, rango_superior_servicio_clientes2, prob_de_cliente_1, prob_de_cliente_2, TIEMPO_FINALIZACION
    # Leer los parámetros de la simulación contenidos en el archivo in.txt
    with open ('in.txt','r') as infile:
        linea = infile.readline() # Se almacena el renglón 
        partes = linea.split() # Se divide el renglón por espacios y se almacenann en una lista 
        media_llegadas = int(partes[0])
        media_servicio_clientes1 = float(partes[1])
        rango_inferior_servicio_clientes2 = float(partes[2])
        rango_superior_servicio_clientes2 = float(partes[3])
        prob_de_cliente_1 = float(partes[4])
        prob_de_cliente_2 = float(partes[5])
        TIEMPO_FINALIZACION = int(partes[6]) # Tiempo de la simulación


# Función que escribe los resultados obtenidos tras realizar las simulaciones en un archivo de nombre out.txt para la lectura del usuario
def escritura_out(iteracion):
    global outfile
    
    #Escribir en el archivo Out.txt la respuesta al ejercicio
    outfile = open("out.txt", "w") # Se crea el archivo out.txt
    outfile.write("Tiempo medio de llegada de clientes: {:11.1f} minutos\n".format(media_llegadas))
    outfile.write("Tiempo medio de servicio a clientes de tipo 1: {:11.1f} minutos\n".format(media_servicio_clientes1))
    outfile.write("Rango de servicio a clientes de tipo 2: {:11.1f}     a {:7.1f} minutos\n".format(rango_inferior_servicio_clientes2,  rango_superior_servicio_clientes2))
    outfile.write("Probabilidad de que un cliente sea de tipo 1: {:11.1f} \n".format(prob_de_cliente_1))
    outfile.write("Probabilidad de que un cliente sea de tipo 2: {:11.1f} \n".format(prob_de_cliente_2))
    outfile.write("Duracion de cada simulacion: {:11.1f} minutos\n\n".format(TIEMPO_FINALIZACION))

    outfile.write("\n\nPromedio total del tiempo en la cola 1: {:5.3f} minutos\n".format((tiempo_avg_en_cola_1_total / iteracion)))
    outfile.write("\n\nPromedio total del tiempo en la cola 2: {:5.3f} minutos\n".format((tiempo_avg_en_cola_2_total / iteracion)))
    outfile.write("\n\nNumero promedio de clientes de tipo 1 en cola: {:5.3f} personas\n".format((num_en_q1_avg_total / iteracion)))
    outfile.write("\n\nNumero promedio de clientes de tipo 2 en cola: {:5.3f} personas\n".format((num_en_q2_avg_total / iteracion)))
    outfile.write("\n\nProporcion de tiempo que los clientes de tipo 1 utilizaron los servidor A: {:5.3f}".format((porcion_tiempo_clientes1_servidores_A_total / iteracion)))
    outfile.write("\n\nProporcion de tiempo que los clientes de tipo 2 utilizaron los servidor A: {:5.3f}".format((porcion_tiempo_clientes2_servidores_A_total / iteracion)))
    outfile.write("\n\nProporcion de tiempo que los clientes de tipo 1 utilizaron los servidor B: {:5.3f}".format((porcion_tiempo_clientes1_servidores_B_total / iteracion)))
    outfile.write("\n\nProporcion de tiempo que los clientes de tipo 2 utilizaron los servidor B: {:5.3f}".format((porcion_tiempo_clientes2_servidores_B_total / iteracion)))
    outfile.write("\n\nTotal de simulaciones realizadas: {:5.0f}".format((iteracion)))
    outfile.close()


#Inicializa todas las variables necesarias para el control de una simulación
def inicializar():
    global tiempo_sim, tipo_evento_siguiente, tiempo_ultimo_evento, clientes_tipo1_en_cola, clientes_tipo2_en_cola, servicios_disponibles_tipo_A, servicios_disponibles_tipo_B, tiempo_siguiente_evento, tiempos_llegada_clientes_tipo_1, tiempos_salida_clientes_tipo_1, tiempos_llegada_clientes_tipo_2, tiempos_salida_clientes_tipo_2, area_num_en_q1, area_num_en_q2, clientes_tipo1_servidor_A, clientes_tipo1_servidor_B, clientes_tipo2_servidores_A_B

    #inicializar el reloj de la simulación y tipo de siguiente evento
    tiempo_sim = 0 #reloj de la simulación
    tipo_evento_siguiente = 0 # 1 = llegada, 2 = salida_cliente_tipo1_servidor_A, 3 = salida_cliente_tipo1_servidor_B, 4= salida_cliente_tipo2, 5 = fin de la simulación
    tiempo_ultimo_evento = 0 # Tiempo transcurrido durante el último evento

    #Inicializar variables de clientes en colas
    clientes_tipo1_en_cola = 0 #cola de clientes tipo 1
    clientes_tipo2_en_cola = 0 #cola de clientes tipo 2

    #inicializar el estado de los servidores
    servicios_disponibles_tipo_A = 2 # Número de servicios disponibles de tipo A
    servicios_disponibles_tipo_B = 1 # Número de servicios disponibles de tipo B

    #inicializar la lista de eventos
    tiempo_siguiente_evento = [None, None, None, None, None, None]
    tiempo_siguiente_evento[0] = 1.0e+30
    tiempo_siguiente_evento[1] = var_expo(media_llegadas) #se calcula el tiempo de la primera llegada
    tiempo_siguiente_evento[2] = 1.0e+30 # Se desconoce el tiempo en el que el próximo evento de tipo 2 sucederá
    tiempo_siguiente_evento[3] = 1.0e+30 # Se desconoce el tiempo en el que el próximo evento de tipo 3 sucederá
    tiempo_siguiente_evento[4] = 1.0e+30 # Se desconoce el tiempo en el que el próximo evento de tipo 4 sucederá
    tiempo_siguiente_evento[5] = TIEMPO_FINALIZACION


    # variables para calcular las medidas de desempeño del sistema

    # Tiempo promedio de espera en cada cola
    tiempos_llegada_clientes_tipo_1 = []
    tiempos_salida_clientes_tipo_1 = []

    tiempos_llegada_clientes_tipo_2 = []
    tiempos_salida_clientes_tipo_2 = []

    # Número de personas promedio en cada cola
    area_num_en_q1 = 0
    area_num_en_q2 = 0

    # Proporción del tiempo que cada tipo de servidor utiliza en cada tipo de cliente
    clientes_tipo1_servidor_A = 0
    clientes_tipo1_servidor_B = 0
    clientes_tipo2_servidores_A_B = 0


# Función que calcula las medidas de desempeño de una simulación
def medidas_desempeño():
    global tiempo_avg_en_cola_1, tiempo_avg_en_cola_2, num_en_q1_avg, num_en_q2_avg, porcion_tiempo_clientes1_servidores_A, porcion_tiempo_clientes2_servidores_A, porcion_tiempo_clientes1_servidores_B, porcion_tiempo_clientes2_servidores_B
    # Cálculo del promedio del tiempo en cada cola
    tiempo_avg_en_cola_1 = sum([tiempos_salida_clientes_tipo_1[i] - tiempos_llegada_clientes_tipo_1[i] for i in range(len(tiempos_salida_clientes_tipo_1))]) / len(tiempos_salida_clientes_tipo_1)
    tiempo_avg_en_cola_2 = sum([tiempos_salida_clientes_tipo_2[i] - tiempos_llegada_clientes_tipo_2[i] for i in range(len(tiempos_salida_clientes_tipo_2))]) / len(tiempos_salida_clientes_tipo_2)


    # Cálculo de número promedio en cola para cada tipo de cliente
    num_en_q1_avg = area_num_en_q1 / TIEMPO_FINALIZACION
    num_en_q2_avg = area_num_en_q2 / TIEMPO_FINALIZACION


    # Cálculo de la proporción de tiempo de cada tipo de cliente en cada tipo de servidor
    # Servidores de tipo A
    atencion_total_en_servidor_A = clientes_tipo1_servidor_A + clientes_tipo2_servidores_A_B # Tiempo total en el que los servidores A estuvieron atendiendo clientes
    porcion_tiempo_clientes1_servidores_A = clientes_tipo1_servidor_A/atencion_total_en_servidor_A
    porcion_tiempo_clientes2_servidores_A = clientes_tipo2_servidores_A_B/atencion_total_en_servidor_A
    # Servidores de tipo B
    atencion_total_en_servidor_B = clientes_tipo1_servidor_B + clientes_tipo2_servidores_A_B # Tiempo total en el que los servidores B estuvieron atendiendo clientes
    porcion_tiempo_clientes1_servidores_B = clientes_tipo1_servidor_B/atencion_total_en_servidor_B
    porcion_tiempo_clientes2_servidores_B = clientes_tipo2_servidores_A_B/atencion_total_en_servidor_B



# Función que contiene el bucle principal de ejecución donde se llama a la función correspondiente al siguiente evento
def simulacion():
    
    inicializar()
    
    while tipo_evento_siguiente != 5 : # Seguir la simulación hasta que el evento más proximo sea el fin de la simulación
        
        tiempo() # Función que determina el siguiente evento 
        actualiza_area_num_en_q() # Función que lleva el control del área de personas en cada cola

        # se llama a la función del siguiente evento
        if tipo_evento_siguiente == 1:
            llegada()
        elif tipo_evento_siguiente == 2:
            salida_cliente_tipo1_servidor_A()
        elif tipo_evento_siguiente == 3:
            salida_cliente_tipo1_servidor_B()
        elif tipo_evento_siguiente == 4:
            salida_cliente_tipo2()

    medidas_desempeño()


# Función principal que controla todas las iteraciones y registra sus medidas de desempeño para calcular un promedio fiable
def main(iteracion):
    global tiempo_avg_en_cola_1_total, tiempo_avg_en_cola_2_total, num_en_q1_avg_total, num_en_q2_avg_total, porcion_tiempo_clientes1_servidores_A_total, porcion_tiempo_clientes2_servidores_A_total, porcion_tiempo_clientes1_servidores_B_total, porcion_tiempo_clientes2_servidores_B_total

    lectura_in() # Se hace lectura de los parametros contenidos en el archivo in.txt


    # Se declaran variables para hallar el promedio tras múltiples iteraciones

    # Cálculo del promedio total del tiempo en cada cola
    tiempo_avg_en_cola_1_total = 0
    tiempo_avg_en_cola_2_total = 0

    # Cálculo de número promedio en cola para cada tipo de cliente
    num_en_q1_avg_total = 0
    num_en_q2_avg_total = 0

    # Cálculo de la proporción de tiempo de cada tipo de cliente en cada tipo de servidor
    # Servidores de tipo A
    porcion_tiempo_clientes1_servidores_A_total = 0
    porcion_tiempo_clientes2_servidores_A_total = 0
    # Servidores de tipo B
    porcion_tiempo_clientes1_servidores_B_total = 0
    porcion_tiempo_clientes2_servidores_B_total = 0


    #repetir la simulación el numero de veces determinado por el usuario
    for i in range (iteracion):
        simulacion() # Se lleva a cabo una simulación

        # Cálculo del promedio total del tiempo en cada cola
        tiempo_avg_en_cola_1_total += tiempo_avg_en_cola_1
        tiempo_avg_en_cola_2_total += tiempo_avg_en_cola_2

        # Cálculo de número promedio en cola para cada tipo de cliente
        num_en_q1_avg_total += num_en_q1_avg
        num_en_q2_avg_total += num_en_q2_avg

        # Cálculo de la proporción de tiempo de cada tipo de cliente en cada tipo de servidor
        # Servidores de tipo A
        porcion_tiempo_clientes1_servidores_A_total += porcion_tiempo_clientes1_servidores_A
        porcion_tiempo_clientes2_servidores_A_total += porcion_tiempo_clientes2_servidores_A
        # Servidores de tipo B
        porcion_tiempo_clientes1_servidores_B_total += porcion_tiempo_clientes1_servidores_B
        porcion_tiempo_clientes2_servidores_B_total += porcion_tiempo_clientes2_servidores_B

    escritura_out(iteracion) # Se escribe el archivo out.txt con las medidas de desempeñó totales obtenidas



main(1000)