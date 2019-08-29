from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from web3 import Web3, HTTPProvider
from ethtoken.abi import EIP20_ABI
from threading import Thread
from decimal import Decimal
import datetime
import Datos
from db.models import Usuario_acceso, Lista_de_espera
from wallethold.utils import class_view_decorator
from django.views.generic import TemplateView
import math
from django.utils.html import escape
from wallethold.views import scan_wallet

# Reducir el numero sin redondear
def truncate(number, digits) -> float:
    stepper = pow(18.0, digits)
    return math.trunc(stepper * number) / stepper

# Variable para evitar mas de 1 bucle
start = 0
@class_view_decorator(login_required(login_url='sign_in'))
class Usuario_View(TemplateView):
    template_name = 'user/index.html'

    def post(self, request, *args, **kwargs):
        # Conectamos por API
        web3 = Web3(HTTPProvider("https://mainnet.infura.io/v3/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"))
        # Le enviamos el contrato del token
        erc20 = web3.eth.contract(address='0x00000000000000000000000000000000000000', abi=EIP20_ABI)
        # Cargamos la DB del usuario
        lista = Usuario_acceso.objects.filter(usuario=request.user)
        # Recorremos los campos
        for i in lista:
            # Buscamos si esta en la lista de espera
            filtrado = Lista_de_espera.objects.filter(wallet=escape(request.POST['wallet_wallethold']))
            # Miramos que contenga informacion y que el estado de WalletHold lo tenga activado
            if len(filtrado) != 0 or i.status_holder == 'Activado' :
                # Si esta Activado lo enviamos a la pagina de inicio
                return redirect('index_user')
            # Si no esta en lista de espera o tiene el estado de WalletHold activo, lo registramos en la lista de espera
            else:
                # Comprobamos que la wallet que pone el usuario es correcta y registramos los datos
                try:
                    balance = erc20.functions.balanceOf(escape(request.POST['wallet_wallethold'])).call()
                    i.wallet = escape(request.POST['wallet_wallethold'])
                    i.fecha_peticion_holder = datetime.datetime.now()
                    i.status_holder = 'Pendiente'
                    i.save()

                    lista_espera = Lista_de_espera.objects.create()
                    lista_espera.usuario = i.usuario
                    lista_espera.fecha_peticion = i.fecha_peticion_holder
                    lista_espera.wallet = escape(request.POST['wallet_wallethold'])
                    lista_espera.save()
                    return redirect('index_user')

                # Si la wallet que puso el usuario es incorrecta lo enviamos a la pagina de inicio
                except:
                    return redirect('index_user')

    def get_context_data(self, *args, **kwargs):
        global start
        if start == 0:
            Thread(target=scan_wallet, args=()).start()
            start += 1


        # Cargamos la DB del usuario logueado
        lista = Usuario_acceso.objects.filter(usuario=self.request.user)
        # Conectamos por API
        web3 = Web3(HTTPProvider("https://mainnet.infura.io/v3/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"))
        # Le enviamos el contrato del token
        erc20 = web3.eth.contract(address='0x00000000000000000000000000000000000000', abi=EIP20_ABI)
        # Pedimos los decimales del token
        decimals = erc20.functions.decimals().call()
        # Creamos una tabla vacia para la lista de pagos
        tabla = []
        # Creamos una variable para saber cuando a ganado el usuario
        ganancias_CRS = 0
        # Creamos una variable para saber cuantos pagos pendientes tiene el usuario
        numero_pagos_pendientes = 0
        # Creamos una variable para saber cuantos pagos completados tiene el usuario
        numero_pagos_completados = 0
        # Creamos una variable para saber cuantos pagos penalizados tiene el usuario
        numero_pagos_penalizado = 0
        # Creamos una variable para saber cuantas recompensas acumula el usuario
        numero_recompensas = 0
        # Creamos una variable para saber el porcentaje de ganancias
        porcentaje_ganancias = 0
        # Creamos una variable para saber el total de token que tiene el usuario
        total = 0
        # Creamos una variable definida como Desactivado
        estado_wallethold = 'Desactivado'
        # Creamos variable para mostrar la ultima wallet registrada por el usuario
        wallet_user = ''
        # Cargamos la lista de espera de la DB
        lista_espera = Lista_de_espera.objects.all()
        # Creamos unaa lista para la lista de espera
        dic_list = []
        # Recorremos la lista de espera y la guardamos en la lista dic_list
        for a in lista_espera:
            dic_list.append({'usuario': a.usuario, 'fecha': a.fecha_peticion, 'wallet': a.wallet})

        # Recorremos la DB del usuario
        for i in lista:
            # Registramos el ultimo estado de la inscripcion de WalletHold
            estado_wallethold = i.status_holder
            wallet_user = i.wallet

            # Creamos una variable por si existen registros de pagos y la guardamos en la lista llamada tabla
            try:
                dict = eval(i.registro_pagos)
                for a in dict:
                    tabla.append(a)
            except:
                pass
                #print('Error al leer el registro de pagos')


            try:
                # Pedimos el balance del usuario
                balance = erc20.functions.balanceOf(i.wallet).call()
                # Sumamos el balance con los decimales del token
                total += balance / Decimal(10 ** decimals)

                # Recorremos la lista de pagos echas al usuario y agregamos +1 al estado de pago correspondiente
                for t in tabla:
                    numero_recompensas += 1
                    ganancias_CRS += float(t['pago'])
                    if t['estado'] == 'Activado':
                        numero_pagos_pendientes += 1
                    if t['estado'] == 'Correcto':
                        numero_pagos_completados += 1
                    if t['estado'] == 'Penalizado':
                        numero_pagos_penalizado += 1

                # Creamos una variable y guardamos el porcentaje de ganancias
                porcentaje_ganancias = '{0:.2f}'.format(ganancias_CRS / Datos.token_requeridos * 100)
            except:
                pass

        try:
            # Creamos una variable para el % que recibira cada usuario actual mente
            porcentaje_actual = int(100 / Datos.total_nodos_ocupados[0])
        except:
            # Si da error es por que no hay ningun usuario registrado en WalletHold, no se puede dividir entre 0
            porcentaje_actual = 100

        context = {
            'total_nodos': Datos.total_nodos,
            'total_nodos_libres': Datos.total_nodos - (Datos.total_nodos_ocupados[0] - Datos.total_nodos_penalizados[0]),
            'total_nodos_ocupados': Datos.total_nodos_ocupados[0],
            'total_supply_nodos': Datos.total_supply_nodos,
            'tabla': tabla,
            'balance': total,
            'estado_WalletHold': estado_wallethold,
            'dic_list': dic_list,
            'wallet_user': wallet_user,
            'ganancias_CRS': truncate(float(ganancias_CRS), decimals),
            'porcentaje_ganancias': '{0:.2f}'.format(Decimal(porcentaje_ganancias)),
            'numero_recompensas': numero_recompensas,
            'numero_pagos_pendientes': numero_pagos_pendientes,
            'numero_pagos_completados': numero_pagos_completados,
            'numero_pagos_penalizado': numero_pagos_penalizado,
            'porcentaje_actual': porcentaje_actual,
        }
        return (context)

@login_required(login_url='sign_in')
def index(request):
    global start
    if start == 0:
        Thread(target=scan_wallet, args=()).start()
        start += 1
    return render(request, 'user/index.html')
