from web3 import Web3, HTTPProvider
from ethtoken.abi import EIP20_ABI
from time import sleep
import time
from decimal import Decimal
import Datos
from db.models import Usuario_acceso, Lista_de_espera
import math

# Reducir el numero sin redondear
def truncate(number, digits) -> float:
    stepper = pow(18.0, digits)
    return math.trunc(stepper * number) / stepper

# Funciona para escanear la lista de espera
def escanear_lista_de_espera():
    try:
        # Miramos si hay plazas disponible
        hora_actual = time.strftime("%Y:%m:%d %H:%M")
        if Datos.total_nodos - (Datos.total_nodos_ocupados[0] - Datos.total_nodos_penalizados[0]) > 0:
            # Cargamos la lista de espera
            lista_espera = Lista_de_espera.objects.all()
            # Recorremos la lista de espera
            for a in lista_espera:
                # Guardamos en la variable las plazas disponible
                Datos.total_nodos_libres[0] = Datos.total_nodos - (Datos.total_nodos_ocupados[0] - Datos.total_nodos_penalizados[0])
                # Le damos un poco de tiempo entre usuario y usuario
                sleep(0.5)
                # Cargamos la DB del usuario
                lista = Usuario_acceso.objects.filter(usuario=a.usuario)
                # Restamos una plaza disponible
                Datos.total_nodos_libres[0] -= 1
                # Registramos una plaza menos disponible
                Datos.total_nodos_ocupados[0] += 1
                # Recorremos la informacion de la DB del usuario
                for r in lista:
                    # Registramos al usuario como activado, por que hay plazas disponibles
                    r.status_holder = 'Activado'
                    # Registramos la wallet que el usuario puso en el formulario
                    r.wallet = a.wallet
                    # Guardamos los cambios
                    r.save()

                    try:
                        # Reformamos la lista del registro de paoos
                        dic = eval(r.registro_pagos)
                        # Agregamos un nuevo dato a la lista de pagos con la fecha actual de su incorporacion
                        dic.append({'fecha_inicio': str(hora_actual), 'fecha_penalizacion' : '', 'fecha_envio': '', 'estado': 'Activado', 'pago': '0', 'porcentaje_nodo': '0', 'wallet': r.wallet, 'usuario': r.usuario})
                    except:
                        # Si no hay datos en la lista de registro de pagos, creamos una lista vacia
                        dic = []
                        # Agregamos un nuevo dato a la lista de pagos con la fecha actual de su incorporacion
                        dic.append({'fecha_inicio': str(hora_actual), 'fecha_penalizacion' : '', 'fecha_envio': '', 'estado': 'Activado', 'pago': '0', 'porcentaje_nodo': '0', 'wallet': r.wallet, 'usuario': r.usuario})
                    # Agregamos la nueva lista a la DB
                    r.registro_pagos = dic
                    # Guardamos los cambios realizados
                    r.save()
                    # Borramos el usuario de la lista de espera
                    a.delete()
    except:
        pass


# Algoritmo de verificacion de condiciones
def scan_wallet():
    try:
        # Conectamos por API
        web3 = Web3(HTTPProvider("https://mainnet.infura.io/v3/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"))
        # Le enviamos el contrato del token
        erc20 = web3.eth.contract(address='0x00000000000000000000000000000000000000', abi=EIP20_ABI)
        # Pedimos los decimales del token
        decimals = erc20.functions.decimals().call()
    except:
        sleep(2)
        scan_wallet()

    try:
        while True:
            sleep(2)
            # Pedimos la lista de usuarios
            lista_usuarios = Usuario_acceso.objects.all()
            # Creamos variable a 0 de usuarios activados
            temp_usuarios_activado = 0
            # Creamos variable a 0 de usuarios penalizados
            temp_usuarios_penalizado = 0

            hora_actual = time.strftime("%Y:%m:%d %H:%M")
            min_actual = time.strftime("%M")
            for usuarios_L in lista_usuarios:
                ### ========= Solo los usuarios que esten activados en WalletHold ============ ###
                # Buscamos los usuario que tengan activo el WalletHold
                if usuarios_L.status_holder == 'Activado':
                    # Miramos cuantos tokens tiene la wallet del usuario
                    balance = erc20.functions.balanceOf(usuarios_L.wallet).call()
                    # Convertimos el balance a los decimales del token
                    total = balance / Decimal(10 ** decimals)
                    # Cogemos el registro de pagos
                    dic_registro_pagos = eval(usuarios_L.registro_pagos)

                    ### ========= Penalizar ============ ###
                    # Si tiene menos tokens de los requeridos se le PENALIZA
                    if total < Datos.token_requeridos and dic_registro_pagos[-1]['estado'] != 'Penalizado':
                        dic_registro_pagos[-1]['estado'] = 'Penalizado'
                        dic_registro_pagos[-1]['pago'] = '0'
                        dic_registro_pagos[-1]['porcentaje_nodo'] = '0'
                        dic_registro_pagos[-1]['fecha_penalizado'] = str(hora_actual)
                        usuarios_L.registro_pagos = dic_registro_pagos
                        usuarios_L.save()

                    ### ========= Eliminar si llega la fecha de pagos ============
                    if str(min_actual) in Datos.dias_recompensa:
                        if dic_registro_pagos[-1]['estado'] == 'Penalizado':
                            usuarios_L.status_holder = 'Desactivado'
                            usuarios_L.save()

                    ### ========= Contar usuarios estado ============ ###
                    temp_usuarios_activado += 1
                    if dic_registro_pagos[-1]['estado'] == 'Penalizado':
                        temp_usuarios_penalizado += 1

            ### ========= Guardar en Lista de Datos.py ============ ###
            Datos.total_nodos_ocupados[0] = temp_usuarios_activado
            Datos.total_nodos_penalizados[0] = temp_usuarios_penalizado

            ### ========= Repartimos recompensa ============ ###
            if str(min_actual) in Datos.dias_recompensa:
                for usuarios_L in lista_usuarios:
                    if usuarios_L.status_holder == 'Activado':
                        # Cogemos el registro de pagos
                        dic_registro_pagos = eval(usuarios_L.registro_pagos)
                        # Verificamos que el ultimo estado en el registro de pagos es Activo
                        if dic_registro_pagos[-1]['estado'] == 'Activado':
                            # Confirmamos que la fecha es distinta para no crear registro duplicados
                            if dic_registro_pagos[-1]['fecha_inicio'] != str(hora_actual):
                                # Miramos cuantos tokens tiene la wallet del usuario
                                balance = erc20.functions.balanceOf(usuarios_L.wallet).call()
                                # Convertimos el balance a los decimales del token
                                total = balance / Decimal(10 ** decimals)
                                # Verificamos que dispone de los tokens requeridos
                                if total >= Datos.token_requeridos:
                                    # Creamos variable para saber cuantas plazas hay disponibles
                                    total_usuarios = Datos.total_nodos_ocupados[0] - Datos.total_nodos_penalizados[0]
                                    # Dividimos la recompensa total entre los usuario Activos
                                    recompensa = int(Datos.recompensa / total_usuarios)
                                    # Registramos la cantidad a pagar al usuario
                                    dic_registro_pagos[-1]['pago'] = recompensa
                                    # Registramos la fecha de la verificacion
                                    dic_registro_pagos[-1]['fecha_envio'] = str(hora_actual)
                                    # Registramos el estado como Correcto
                                    dic_registro_pagos[-1]['estado'] = 'Correcto'
                                    # Registramos el % que recibiran los usuarios
                                    dic_registro_pagos[-1]['porcentaje_nodo'] = 100 / total_usuarios
                                    # Creamos un nuevo dato en la lista para el siguiente pago
                                    dic_registro_pagos.append(
                                        {'fecha_inicio': str(hora_actual), 'fecha_penalizacion': '',
                                         'fecha_envio': '', 'estado': 'Activado', 'pago': '0', 'porcentaje_nodo': '0',
                                         'wallet': usuarios_L.wallet, 'usuario': usuarios_L.usuario})

                                    # Registramos la lista nueva en el registro de pagos
                                    usuarios_L.registro_pagos = dic_registro_pagos
                                    # Guardamos los cambios en la DB
                                    usuarios_L.save()

                # Llama a la funcion para ver si hay plazas disponibles y agregar a los usuarios en lista de espera
                escanear_lista_de_espera()

    except:
        sleep(2)
        scan_wallet()
