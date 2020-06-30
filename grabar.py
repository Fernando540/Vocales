import sounddevice as sd
from scipy.io.wavfile import write, read
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
nombre_carpeta_audios = 'audioVocales'
carpeta_audios = dir_path + "\\" + nombre_carpeta_audios



def grabarAudio():
    vocales = ['a', 'e', 'i', 'o', 'u']
    nombre_persona = input("Ingrese su nombre: ")
    fs = 32768  # Sample rate
    seconds = 1  # Duration of recording
    for i in range(5):
        try:
            os.makedirs(carpeta_audios + '\\' + vocales[i])
        except FileExistsError:
            pass
        print(f'Grabando {vocales[i]}...')
        file_name = f'{vocales[i] + nombre_persona}.wav'
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        write(carpeta_audios + '\\' + vocales[i]+ '\\' + file_name, fs, myrecording)  # Save as WAV file
        print('Finalizado!')

grabarAudio()