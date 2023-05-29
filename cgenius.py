import docopt
import ffmpeg
import os
import socket
import shutil
import speech_recognition as sr

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"El archivo {file_path} ha sido eliminado.")
    except FileNotFoundError:
        print(f"No se pudo encontrar el archivo {file_path}.")
    except PermissionError:
        print(f"No se tienen los permisos necesarios para eliminar el archivo {file_path}.")
    except Exception as e:
        print(f"Ocurrió un error al intentar eliminar el archivo {file_path}: {e}")

def zip_file(input_file):
    base_name = os.path.splitext(input_file)[0]
    shutil.make_archive(base_name, 'zip', os.path.dirname(input_file), os.path.basename(input_file))


def unzip_file(input_file):
    shutil.unpack_archive(input_file)
#############################################################
def generate_and_embed_subtitles(video_file, output_file):
    # Extraer el audio del video
    audio_file = "temp_audio.wav"
    ffmpeg.input(video_file).output(audio_file, format="wav").run()

    # Generar los subtítulos
    subtitles_file = "subtitles.srt"
    generate_subtitles(audio_file, subtitles_file)

    # Incrustar los subtítulos en el video
    ffmpeg.input(video_file).output(output_file, vf="subtitles='" + subtitles_file + "'").run()

    # Eliminar los archivos temporales
    os.remove(audio_file)
    os.remove(subtitles_file)

def generate_subtitles(audio_file, output_file):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, show_all=False)

    duration = ffmpeg.probe(audio_file)['format']['duration']
    duration = float(duration)

    subtitle_text = "1\n00:00:00,000 --> {duration},000\n{text}".format(duration=to_srt_time(duration), text=text)

    with open(output_file, "w") as f:
        f.write(subtitle_text)

def to_srt_time(seconds):
    milliseconds = int((seconds - int(seconds)) * 1000)
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return "{:02d}:{:02d}:{:02d},{:03d}".format(h, m, s, milliseconds)
####################################################################
def send_file(input_file, remote_IP, port):
    port = int(port)
    base_name = os.path.splitext(input_file)[0]
    zip_file(input_file)
    input_zip = base_name +'.zip'
    # Establecer conexión con el dispositivo de destino
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET --> IPv4;   SOCK_STREAM --> Socket TCP
    sock.connect((remote_IP, port))
    print('Conectado!')
    # Abrir el archivo de video y leer los datos en bloques
    with open(input_zip, 'rb') as archivo:
        while True:
            datos = archivo.read(1024)  # Leer 1KB de datos del video
            if not datos:
                break
            sock.sendall(datos)  # Enviar los datos al dispositivo de destino

    # Cerrar la conexión
    sock.close()
    delete_file(input_zip)

def recive_file(port):
    port = int(port)
    # Crear un socket y enlazarlo a una dirección y puerto locales
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', port)) # 0.0.0.0 --> Cualquier dirección
    sock.listen(1)  # Esperar 1 sola conexion entrante

    # Aceptar la conexión entrante
    print("Esperando conexión entrante...")
    conexion, direccion = sock.accept()
    print("Conexión establecida desde:", direccion)

    # Abrir un archivo para escribir los datos recibidos
    with open('archivo_socket.zip', 'wb') as archivo:
        while True:
            datos = conexion.recv(1024)  # Recibir 1KB de datos
            if not datos:
                break
            archivo.write(datos)  # Escribir los datos en el archivo

    # Cerrar la conexión
    conexion.close()
    sock.close()
    print('conexion cerrada')
    unzip_file('archivo_socket.zip')
    print('descomprimido')
    delete_file('archivo_socket.zip')


def convert_video(input_file, output_file):
    ffmpeg.input(input_file).output(output_file).run()

def resize_video(input_file, output_file, width, height):
    ffmpeg.input(input_file).output(output_file, vf=f'scale={width}:{height}').run()

def change_framerate(input_file, output_file, framerate):
    ffmpeg.input(input_file).output(output_file, r=framerate).run()

def adjust_quality(input_file, output_file, crf):
    ffmpeg.input(input_file).output(output_file, crf=crf).run()

def extract_video_segment(input_file, output_file, start_time, duration):
    ffmpeg.input(input_file, ss=start_time, t=duration).output(output_file).run()

def extract_audio(input_file):
    base_name = os.path.splitext(input_file)[0]
    ffmpeg.input(input_file).output(base_name+'.wav', format="wav").run()




USAGE = '''
 
 
    
Oriol Garcia Vila | Pol Sedo i Mota                                                                                                        
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████╗
╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╝
     ██████╗     ██████╗     ██████╗     ███████╗     ██████╗     ██████╗     ███████╗    ███╗   ██╗    ██╗    ██╗   ██╗    ███████╗    
    ██╔════╝    ██╔═══██╗    ██╔══██╗    ██╔════╝    ██╔════╝    ██╔════╝     ██╔════╝    ████╗  ██║    ██║    ██║   ██║    ██╔════╝    
    ██║         ██║   ██║    ██║  ██║    █████╗      ██║         ██║  ███╗    █████╗      ██╔██╗ ██║    ██║    ██║   ██║    ███████╗    
    ██║         ██║   ██║    ██║  ██║    ██╔══╝      ██║         ██║   ██║    ██╔══╝      ██║╚██╗██║    ██║    ██║   ██║    ╚════██║    
    ╚██████╗    ╚██████╔╝    ██████╔╝    ███████╗    ╚██████╗    ╚██████╔╝    ███████╗    ██║ ╚████║    ██║    ╚██████╔╝    ███████║    
     ╚═════╝     ╚═════╝     ╚═════╝     ╚══════╝     ╚═════╝     ╚═════╝     ╚══════╝    ╚═╝  ╚═══╝    ╚═╝     ╚═════╝     ╚══════╝    
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████╗
╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╚════╝
                                                NETWORK MULTIMEDIA CODING TOOLS                                                                                                                                                                    
Usage:
  programa.py convert <input_file> <output_file>
  programa.py resize <input_file> <output_file> --width <width> --height <height>
  programa.py framerate <input_file> <output_file> --framerate <framerate>
  programa.py quality <input_file> <output_file> --crf <crf>
  programa.py extract <input_file> <output_file> --start_time <start_time> --duration <duration>
  programa.py audio <input_file>
  programa.py send <input_file> <remote_IP> <port>
  programa.py recive <port>
  programa.py zip <input_file>
  programa.py unzip <input_file>
  programa.py delete <input_file>
  programa.py subtitles <input_file> <output_file>


  

Options:
  --width <width>             Width for resizing
  --height <height>           Height for resizing
  --framerate <framerate>     New framerate
  --crf <crf>                 Constant Rate Factor for quality adjustment
  --start_time <start_time>   Start time for video segment extraction
  --duration <duration>       Duration of video segment extraction
'''

def main():
    args = docopt.docopt(USAGE)

    if args['convert']:
        convert_video(args['<input_file>'], args['<output_file>'])
    elif args['resize']:
        resize_video(args['<input_file>'], args['<output_file>'], int(args['--width']), int(args['--height']))
    elif args['framerate']:
        change_framerate(args['<input_file>'], args['<output_file>'], int(args['--framerate']))
    elif args['quality']:
        adjust_quality(args['<input_file>'], args['<output_file>'], int(args['--crf']))
    elif args['extract']:
        extract_video_segment(args['<input_file>'], args['<output_file>'], args['--start_time'], args['--duration'])
    elif args['audio']:
        extract_audio(args['<input_file>'])
    elif args['send']:
        send_file(args['<input_file>'], args['<remote_IP>'], args['<port>'])
    elif args['recive']:
        recive_file(args['<port>'])
    elif args['zip']:
        zip_file(args['<input_file>'])
    elif args['unzip']:
        unzip_file(args['<input_file>'])
    elif args['delete']:
        delete_file(args['<input_file>'])
    elif args['subtitles']:
        generate_and_embed_subtitles(args['<input_file>'], args['<output_file>'])


    



if __name__ == "__main__":
    os.environ['FFMPEG_PATH'] = 'C:/ffmpeg.exe'
    main()