# Sistema de recompensas WalletHold
Es un ejemplo del sisetma WalletHold, pudiendolo adaptar a distintas fechas y recompensas.
El sistema esta desarrollado en Django 2.2.4 y Python 3.6.6 .


# Explicación

- **¿Qué es WalletHold?**
A diferencia de la adquisición de TOKEN en las rondas de la ICO, CRESIO ha decidido crear un novedoso sistema para recibir TOKEN sin contraprestación económica: “**WalletHold**”. Se trata de un sistema independiente de código abierto, que se encarga de revisar y detectar de manera continua los wallets que tengan más de **X TOKEN**. Dichos wallets recibirán TOKEN gratuitos de forma diaria, hasta que el usuario deje su wallet por debajo de los **X TOKEN**. Aquellos wallets que cumplan estos requisitos se denominarán Cuentas WalletHold y en su panel de control podrán ir observando los CRES recibidos diariamente.


- **Funcionamiento del sistema WalletHold**
Para que los TOKEN recibidos puedan ser transferidos al wallet, la Cuenta WalletHold debe haber recibido TOKEN gratuitos durante al menos **X días consecutivos**. En el caso no mantenerse un mínimo de **X TOKEN** en el wallet durante los **X días consecutivos** el usuario perderá los TOKEN acumulados en la ronda actual.


### Gráfico de funcionamiento

![](https://cresio.io/wallethold_cresio.jpg)

### Tranferencias
Las transferencias a los wallets de cada Cuenta WalletHold de los TOKEN acumulados se realizarán 2 veces al mes.
Por tanto, para poder transferir los TOKEN recibidos a un wallet, se deberá haber recibido la recompensa durante al menos 15 días consecutivos, y esperar al próximo periodo de pago. 

Para la entrega de estos CRES se ha asignado el **X% de los TOKEN creados (X millones de TOKEN)** para repartir entre las Cuentas WalletHold durante X años.
Lo que supone la entrega de **X TOKEN diarios**, que serán repartidos a partes iguales entre las Cuentas WalletHold, lo que supone que cuantas más Cuentas WalletHold haya, menos recibirá cada una de ellas.


### Ejemplo de recompensas
![](https://cresio.io/ejemplo_wallethold.jpg)

### Inscritos y lista de espera
No todas aquellos wallets que tengan más de **X TOKEN** tendrán la consideración de Cuenta WalletHold, **ya que solo habrá X Cuentas WalletHold y X cuentas en la lista de espera**, que se asignarán por estricto orden del cumplimiento de los requisitos.

Pueden quedar plazas disponibles en las Cuentas WalletHold si alguno de los **X usuarios dejara su wallet con menos de X TOKEN**, dando así paso al primer usuario de la lista de espera. Aquellos usuarios que pierdan la condición de Cuenta WalletHold serán penalizados por el sistema, y durante los siguientes X días no podrán ser miembros de la lista de espera.


# Instalacion
Estas instrucciones le proporcionarán una copia del proyecto en funcionamiento en su máquina local para fines de desarrollo y prueba. 

##### Instale las dependencias requeridas 
`pip install -r requirements.txt`

##### Aplicar migraciones
`python manage.py migrate`

##### Inicie la aplicación django
`python manage.py runserver`

##### Ver la aplicación en el navegador
Navegue hasta [http://127.0.0.1:8000](http://127.0.0.1:8000) para verlo en funcionamiento.

# Como usarlo

## Modificacion de datos básicos
	En el archivo /wallethold/views/usuario.py tiene que modificar la linea 29, 30, 73, 75
	En el archivo /wallethold/views/scan.py tiene que modificar la linea 68 y 70
	En el archivo Datos.py puede modificar los datos basicos.
	
## Crear registro nuevo
	Registra un usuario nuevo 
	Loguese con el usuario y contraseña creadas anterior mente.
	Arriba a la derecha ponga su wallet ERC20
	Click a registrar y se agregara a la lista de espera
	En proxima recompensa si hay plazas disponibles se le activara el sistema
	En la proxima recompensa ya se le mostrara en la tabla la recompensa y su estado

# Recursos utilizados de terceros
· Template gratuito de: https://startbootstrap.com/themes/sb-admin-2/

· Login y registro de: https://platzi.com/tutoriales/1378-python/1406-creando-registro-de-usuario-e-inicio-de-sesion-con-django/

· Nodo de Blockchain de Ethereum: https://infura.io

