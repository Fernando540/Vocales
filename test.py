import sounddevice as sd
from scipy.io.wavfile import write,read
import os
import numpy as np
import matplotlib.pyplot as plt 
import cmath
import pathlib

CHUNK = 40
SECONDS = 1         # Duracion de la grabación
MUESTRAS = 32768    # Rate de muestreo
vocales = ['a', 'e', 'i', 'o', 'u']
dir_path = os.path.dirname(os.path.realpath(__file__))
file_name = dir_path + '\\\\' + 'entrada.wav'
nombre_carpeta_audios = 'audioVocales'
carpeta_audios = dir_path + "\\" + nombre_carpeta_audios

"""*************************FUNCIONES PARA CALCULAR LA FFT************************************"""
def bitInverso(sec):
    diccionario = {}
    longitud = len(sec)
    max_bits = len(np.binary_repr(longitud - 1))
    for indice in range(longitud):
        diccionario[indice] = int((np.binary_repr(indice, max_bits))[::-1], 2)
    return diccionario, max_bits

#Funcion para obtener w
def obtenerW(k,N):
    w = complex(cmath.e**complex(0,-2*k*cmath.pi/N))
    if str(w.real).count('e') == 1 :
        w = complex(0,w.imag)
    if str(w.imag).count('e') == 1 :
        w = complex(w.real,0)
    return w

def unificar(partes):
    registro = []
    for parte in partes:
        registro.extend(parte)
    return registro

def FFT(sec,maxBit,bitI):
    registro = [ sec[bitI[indice]] for indice in bitI.keys() ]
    #print(f'\nregistro = {registro}')
    for etapa in range(maxBit):
        pares = 2**(etapa+1)
        #print(f'pares = {pares}')
        partes = [ registro[indice:(indice+pares)] for indice in range(0,len(registro),pares) ]
        #print(f"partes = {partes}\n\n")
        for parte in partes:
            i = 0
            j = int(len(parte)/2)
            for indice in range(int(len(parte)/2)):
                w = obtenerW(indice,pares)
                temp1 = parte[i] + w*parte[j]
                temp2 = parte[i] - w*parte[j]
                parte[i] = temp1
                parte[j] = temp2
                i+=1
                j+=1
        #print(f'Partes: {partes}')
        registro = unificar(partes)
        #print(f'registro {etapa}: {registro}')
    return np.array(registro)

"""*************************FUNCIONES DE GRABACION/RECONOCIMIENTO************************************"""

#Funcion para agregar una muestra de sonido individual
def agregar():
    choice = input('Desea agregar desde archivo de entrada?\ty: SI\totro: NO\n')
    nombre_persona = input("Ingrese su nombre: ")
    vocal_ingresada = input("Qué vocal? ")
    if choice != 'y':
        file_name = grabar(nombre_persona,vocal_ingresada)

    rangos,secuencia = analizaWAV(file_name)
    plt.plot(secuencia[:8000],'r-')
    f = open(f'{vocal_ingresada}.txt','a')
    f.write(f'{rangos}\n')
    f.close()
    promediar()
    reconocer(rangos,False)
    plt.show()

def grabar(nombre_persona, vocal):
    try:
        os.makedirs(carpeta_audios + '\\' + vocal)
    except FileExistsError:
        pass
    
    existe=True
    numero = 0
    while existe:
        filepath = carpeta_audios + '\\' + vocal + '\\' + vocal + nombre_persona + str(numero)+'.wav'
        if os.path.isfile(filepath):
            numero+=1
        else:
            file_name = f'{vocal + nombre_persona+str(numero)}.wav'
            existe = False

    print(f'Grabando {vocal}...')
    myrecording = sd.rec(int(SECONDS * MUESTRAS), samplerate=MUESTRAS, channels=1)
    sd.wait()  # Wait until recording is finished
    recordPath = carpeta_audios + '\\' + vocal + '\\' + file_name
    write(recordPath, MUESTRAS, myrecording)  # Save as WAV file
    print('Finalizado!')

    return recordPath

def analizaWAV(ruta):
    data = read(ruta)[1]
    arr = np.array(data)
    bitI,maxBit = bitInverso(arr)
    fft = FFT(arr,maxBit,bitI)
    secuencia = abs(fft)
    rangos = []
    ini, fin = 0,0
    for i in range(CHUNK):
        ini = int((4000/CHUNK)*i)
        fin = int(ini+((4000/CHUNK)-1))
        rangos.append(np.mean(secuencia[ini:fin]))
    return rangos, secuencia

def cargarAudios():
    for vocal in vocales:
        ruta = carpeta_audios+'\\'+vocal
        directorio = pathlib.Path(ruta)
        ruta+='\\'
        f = open(f'{vocal}.txt','w')
        for fichero in directorio.iterdir():
            print(f'Analizando {ruta+fichero.name}')
            f.write(f'{analizaWAV(ruta+fichero.name)[0]}\n')
        f.close()
    promediar()

def promediar():
    fproms = open('proms.txt','w')
    for vocal in vocales:
        filepath = dir_path + '\\' + f'{vocal}.txt'
        if os.path.isfile(filepath):
            f = open(f'{vocal}.txt','r')
        else:
            f = open(f'{vocal}.txt','w+')
        lineas = []
        prom = np.zeros(CHUNK)
        lines = f.readlines()
        #print(f'Lineas de {vocal}= {len(lines)}')
        if  len(lines) != 0:
            for line in lines:
                linea = line[1:-2].split(',')
                linea = [float(i) for i in linea]
                lineas.append(linea)
            for linea in lineas:
                for i in range(CHUNK):
                    prom[i] += linea[i]
            prom = [valor/len(lineas) for valor in prom]
        else:
            prom = [0.0 for valor in prom]
        fproms.write(f'{vocal}:{prom}\n')
        f.close()
    fproms.close()
    print('Promedios actualizados correctamente')

def reconocer(rangos,grabar):
    if grabar:
        print('Grabando...')
        myrecording = sd.rec(int(SECONDS * MUESTRAS), samplerate=MUESTRAS, channels=1)
        sd.wait()
        write(file_name, MUESTRAS, myrecording)  # Save as WAV file 
        print('Finalizado!')
        rangos,secuencia = analizaWAV(file_name)
        plt.plot(secuencia[:8000],'r-')
    
    vowel = 'X'
    f = open('proms.txt','r')
    promRanges = []
    for line in f:
        linea = line[3:-2].split(',')
        linea = [float(i) for i in linea]
        promRanges.append(linea)
    f.close()

    difMedia = np.zeros(5)
    for i,vocal in enumerate(promRanges):
        errorAcum = 0
        for j in range(CHUNK):
            errorAcum += abs(vocal[j]-rangos[j])
        difMedia[i] = errorAcum
        print(f'Error de {vocales[i]}: {errorAcum}')

    errorMin = np.min(difMedia)
    indice = 0
    for i in range(5):
        if difMedia[i] == errorMin:
            indice=i
            break
    vowel = vocales[indice]
    print(f'La vocal es: {vowel}')
    return vowel

def menu():
    print('\n*************************RECONOCIMIENTO DE VOCALES A PARTIR DE ESPECTOGRAMA************************************')
    print("Selecciona una opción\n0: Grabar todas las vocales\n1: Agregar muestra de vocal\n2: Reconocer vocal\n3: Recargar todos los audios\nOtro: Salir")
    opc = input()
    if(opc == '0'):
        nombre_persona = input("Ingrese su nombre: ")
        for vocal in vocales:
            file_name = grabar(nombre_persona,vocal)
            rangos = analizaWAV(file_name)[0]
            f = open(f'{vocal}.txt','a')
            f.write(f'{rangos}\n')
            f.close()
        promediar()
        menu()
    elif(opc == '1'):
        agregar()
        menu()
    elif(opc== '2'):
        filepath = dir_path + '\\' + 'proms.txt'
        if os.path.isfile(filepath):
            reconocer(0,True)
            plt.show()
        else:
            print('\n**ERROR: Aun no se han agregado muestras, favor de agregar algunas')
        menu()
    elif(opc== '3'):
        if os.path.isfile(carpeta_audios+'\\'):
            cargarAudios()
        else:
            print('\n**ERROR: No se han encontrado audios')
        menu()
    else:
        print('Adios mundo :v')
        pass

menu()