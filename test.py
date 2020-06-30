import sounddevice as sd
from scipy.io.wavfile import write,read
import os
import numpy as np
import matplotlib.pyplot as plt 
import cmath

CHUNK = 40
MUESTRAS = 32768
vocales = ['a', 'e', 'i', 'o', 'u']
dir_path = os.path.dirname(os.path.realpath(__file__))
file_name = dir_path + '\\\\' + 'vocalTest.wav'
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
#Funcion para grabar una muestra de sonido
#Arumentos: 
#   guardar(Booleano):indica si se desea guardar los rangos calculados en su correspondiente vocal así como recalcular lospromedios
def grabar(guardar,useMic):
    #fs = 44100  # Sample rate
    fs = MUESTRAS
    seconds = 1  # Duration of recording
    
    if useMic:
        print('Grabando...')
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()
        write(file_name, fs, myrecording)  # Save as WAV file 
    print('Finalizado!')

    fs, data = read(file_name)
    arr = np.array(data) # numpy array con la informacion del audio
    #plt.plot(arr,'r-',alpha=1.0)
    #fft = np.fft.fft(arr)
    bitI,maxBit = bitInverso(arr)
    fft = FFT(arr,maxBit,bitI)
    secuencia = abs(fft)

    rangos = []
    ini, fin = 0,0
    for i in range(CHUNK):
        ini = int((4000/CHUNK)*i)
        fin = int(ini+((4000/CHUNK)-1))
        rangos.append(np.mean(secuencia[ini:fin]))
    """r1 = np.max(secuencia[:59])
    r2 = np.max(secuencia[61:8000])
    r = max(r1,r2)
    freq = np.where(secuencia[:8000] == r)"""
    #plt.plot(fft,'b-',alpha=0.8)
    plt.plot(secuencia[:8000],'r-',alpha=0.9)
    
    if(guardar):
        vocal = input('Qué vocal es?\n')
        f = open(f'{vocal}.txt','a')
        #f.write(f'{r}\t{freq}\n')
        f.write(f'{rangos}\n')
        f.close()
        promediar()

    #print(f"Magnitud Max = {r} en posición {freq}")
    print(f'La vocal es: {reconocer(rangos)}')
    plt.show()

def promediar():
    fproms = open('proms.txt','w')
    for vocal in vocales:
        filepath = dir_path + '\\\\' + f'{vocal}.txt'
        if os.path.isfile(filepath):
            f = open(f'{vocal}.txt','r')
        else:
            f = open(f'{vocal}.txt','w')
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

def reconocer(rangos):
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
    return vowel

def grabaVocales():
    nombre_persona = input("Ingrese su nombre: ")
    seconds = 1  # Duration of recording
    for i in range(5):
        try:
            os.makedirs(carpeta_audios + '\\' + vocales[i])
        except FileExistsError:
            pass
        print(f'Grabando {vocales[i]}...')
        file_name = f'{vocales[i] + nombre_persona}.wav'
        myrecording = sd.rec(int(seconds * MUESTRAS), samplerate=MUESTRAS, channels=1)
        sd.wait()  # Wait until recording is finished
        write(carpeta_audios + '\\' + vocales[i]+ '\\' + file_name, MUESTRAS, myrecording)  # Save as WAV file
        print('Finalizado!')

def menu():
    print('\n*************************RECONOCIMIENTO DE VOCALES A PARTIR DE ESPECTOGRAMA************************************')
    print("Selecciona una opción\n0: Grabar vocales\n1: Agregar muestra de vocal\n2: Reconocer desde archivo\n3: Reconocer con microfono\n4: Recalcular Promedios\nOtro: Salir")
    opc = input()
    if(opc == '0'):
        grabaVocales()
        menu()
    elif(opc == '1'):
        grabar(True,True)
        menu()
    elif(opc== '2'):
        grabar(False,False)
        menu()
    elif(opc== '3'):
        grabar(False,True)
        menu()
    elif(opc== '4'):
        promediar()
        menu()
    else:
        print('Adios mundo :v')
        pass

menu()