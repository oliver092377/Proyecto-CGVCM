from threading import Thread
import cv2
import numpy as np
import sounddevice as sd
import random
import simpleaudio as simple

global count
count=0
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

imnote = [
	10,10,10,6,1,
	10,6,1,10,
	5,5,5,6,1,
	9,6,1,10,
	10,10,10,10,9,8,
	7,6,8,12,4,3,2,
	1,12,1,6,9,6,9,
]
imoctave = [
	4,4,4,4,5,
	4,4,5,4,
	5,5,5,5,5,
	4,4,5,4,
	5,4,4,5,5,5,
	5,5,5,4,5,5,5,
	5,4,5,4,4,4,4,
]
inlong = [
	400,400,400,200,200,
	400,200,200,1000,
	400,400,400,200,200,
	400,200,200,1000,
	400,200,200,400,200,200,
	200,200,200,200,400,200,200,
	200,200,200,200,400,200,200,
]


playSound = True
class Note(Thread):
    def frec(self, nota:int, octava:int)->int:
        expo = octava *12 + (nota-58)
        return int (440* ((2 ** (1/12)) **expo))
    
    def beep(self, nota:int, octava:int, duracion:int)->None:
        framerate = 44100
        t = np.linspace(0, duracion/1000, int (framerate*duracion/1000))
        frequency = self.frec(nota, octava)
        data = np.sin(2*np.pi*frequency*t)
        sd.play(data, framerate)
        sd.wait()
    def run(self):
        #global playSound
        #playSound = False
        self.beep(imnote[count], imoctave[count], inlong[count])
        #playSound = True
nota = None

celesteBajo = np.array([75, 185, 88], np.uint8)
celesteAlto = np.array([112, 255, 255], np.uint8)

# Colores a utilizar
colorCeleste = (255,113,82)
colorAmarillo = (89,222,255)
colorRosa = (128,0,255)
colorVerde = (0,255,36)
colorLimpiarPantalla = (29,112,246)

color = colorRosa  # Color de puntero
grosor = 3 # Grosor del marcador del puntero


x1 = None
y1 = None
imAux = None

bol=True
global inc_x
global inc_y
global inc_x2
global inc_y2

inc_x=0
inc_y=0
inc_x2=0
inc_y2=0

interfaz="menu"

# Variables para posiciones aleatorias del objetivo
showSquare = True
showSquare2 = True#agregado
rndPositions = []
rndPositions2 = []#agregado
squaresGap = 100 # Distancia minima entre cada par de posiciones
def reFillSquarePositions():
    global rndPositions
    rndPositions.clear()
    # Algoritmo que evita sobreposicion entre 2 posiciones seguidas
    for i in range(len(imnote)):
        x = random.randint(0, 490)
        if i != 0:
            xDiff = abs(rndPositions[i-1][0] - x)
        if i != 0 and xDiff < squaresGap:
            co = (squaresGap**2 - xDiff**2) ** 0.5
            co = int(co)
            yBottom = rndPositions[i-1][1] - co
            yTop = rndPositions[i-1][1] + co
            if yTop >= 280:
                y = random.randint(0, yBottom)
            elif yBottom <= 0:
                y = random.randint(yTop, 280)
            else:
                y = random.randint(0, 280 - (2*co))
                if y > yBottom: y += 2*co
        else:
            y = random.randint(0, 280)
        rndPositions.append((x, y))

#funcion agregada
def reFillSquarePositions2():
    global rndPositions2
    rndPositions2.clear()
    # Algoritmo que evita sobreposicion entre 2 posiciones seguidas
    for i in range(len(imnote)):
        x = random.randint(0, 490)
        if i != 0:
            xDiff = abs(rndPositions2[i-1][0] - x)
        if i != 0 and xDiff < squaresGap:
            co = (squaresGap**2 - xDiff**2) ** 0.5
            co = int(co)
            yBottom = rndPositions2[i-1][1] - co
            yTop = rndPositions2[i-1][1] + co
            if yTop >= 280:
                y = random.randint(0, yBottom)
            elif yBottom <= 0:
                y = random.randint(yTop, 280)
            else:
                y = random.randint(0, 280 - (2*co))
                if y > yBottom: y += 2*co
        else:
            y = random.randint(0, 280)
        rndPositions2.append((x, y))
# Calcula a modo de cuadrado si un pointCoords está dentro del circulo
def coordsInCircle(circleCoords, radius, pointCoords):
    radius *= 0.8667 # Constante que asemeja un cuadrado a un circulo
    return circleCoords[0] + radius > pointCoords[0] and\
        circleCoords[0] - radius < pointCoords[0] and\
        circleCoords[1] + radius > pointCoords[1] and\
        circleCoords[1] - radius < pointCoords[1]
reFillSquarePositions()
reFillSquarePositions2()
indexRndPosition = 0
reproducirUno=-1

while True:
    ret,frame = cap.read()
    if ret==False: break
    frame = cv2.flip(frame,1)
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if imAux is None: imAux = np.zeros(frame.shape,dtype=np.uint8)

    # Detección del color celeste
    maskCeleste = cv2.inRange(frameHSV, celesteBajo, celesteAlto)
    maskCeleste = cv2.erode(maskCeleste,None,iterations = 1)
    maskCeleste = cv2.dilate(maskCeleste,None,iterations = 2)
    maskCeleste = cv2.medianBlur(maskCeleste, 13)
    cnts,_ = cv2.findContours(maskCeleste, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1]
    if interfaz == "menu":
        cv2.rectangle(frame,(130,120),(430,220),colorAmarillo,2)
        cv2.rectangle(frame,(430,120),(530,220),colorAmarillo,3)
        cv2.putText(frame,"TUTORIAL",(160,190),4,1.5,colorVerde,3,cv2.LINE_AA)
        cv2.rectangle(frame,(130,230),(430,330),colorAmarillo,2)
        cv2.rectangle(frame,(430,230),(530,330),colorAmarillo,3)
        cv2.putText(frame,"JUGAR",(200,300),4,1.5,colorVerde,3,cv2.LINE_AA)
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 1000:
                x,y2,w,h = cv2.boundingRect(c)
                x2 = x + w//2
                if x1 is not None:
                    if 430 < x2 < 530 and 230 < y2 < 330:
                        interfaz="seleccion"
                        playingBGMusic = False
                    if 430 < x2 < 530 and 120 < y2 < 220:
                        interfaz="tutorial"
                        playingBGMusic = False
                cv2.circle(frame,(x2,y2),grosor,color,5)
                x1 = x2
                y1 = y2
            else:
                x1, y1 = None, None
    elif interfaz == "seleccion":
        #dsfgsdgsdg
        # Bloque "Canción 1"
        cv2.rectangle(frame, (130, 120), (430, 220), colorAmarillo, 2)
        cv2.rectangle(frame, (500, 120), (600, 220), colorAmarillo, 3)#rectangulo pequeño
        cv2.putText(frame, "Cancion 1", (160, 190), 4, 1.5, colorVerde, 3, cv2.LINE_AA)
        
        # Bloque "Canción 2"
        cv2.rectangle(frame, (130, 230), (430, 330), colorVerde, 2)
        cv2.rectangle(frame, (500, 230), (600, 330), colorAmarillo, 3)#rectangulo pequeño
        cv2.putText(frame, "Cancion 2", (160, 300), 4, 1.5, colorVerde, 3, cv2.LINE_AA)

        # Bloque "Canción 3"
        cv2.rectangle(frame, (130, 340), (430, 440), colorAmarillo, 2)
        cv2.rectangle(frame, (500, 340), (600, 440), colorAmarillo, 3)#rectangulo pequeño
        cv2.putText(frame, "Cancion 3", (160, 410), 4, 1.5, colorVerde, 3, cv2.LINE_AA)
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 1000:
                x,y2,w,h = cv2.boundingRect(c)
                x2 = x + w//2
                if x1 is not None:
                    if 500 < x2 < 600 and 120 < y2 < 220:
                        interfaz="Cancion_1"
                        print(interfaz)
                        playingBGMusic = False
                    if 500 < x2 < 600 and 230 < y2 < 330:
                        interfaz="Cancion_2"
                        print(interfaz)
                        playingBGMusic = False
                    if 500 < x2 < 600 and 340 < y2 < 440:
                        interfaz="Cancion_3"
                        print(interfaz)
                        playingBGMusic = False    
                cv2.circle(frame,(x2,y2),grosor,color,5)
                x1 = x2
                y1 = y2
            else:
                x1, y1 = None, None  
    elif interfaz == "Cancion_1":  
        #sajsfnkas
        if indexRndPosition == len(rndPositions):
            print("Ganaste :D")
            indexRndPosition = 0
            break
        if showSquare: # bol
            inc_x = rndPositions[indexRndPosition][0]
            inc_y = rndPositions[indexRndPosition][1]
            showSquare=False
        if showSquare2: # bol
            inc_x2 = rndPositions2[indexRndPosition][0]
            inc_y2 = rndPositions2[indexRndPosition][1]
            showSquare2=False
        cv2.rectangle(frame,(50,100), (590, 430), colorRosa, 2)
        sa=str(count)
        cv2.putText(frame,sa,(570,50),6,2,colorLimpiarPantalla,3,cv2.LINE_AA)
        cv2.putText(frame,"SCORE",(550,80),6,0.8,colorCeleste,2,cv2.LINE_AA)
        cv2.putText(frame,"Imperial March",(40,40),4,0.8,colorVerde,2,cv2.LINE_AA)
        cv2.putText(frame,"Imperial March",(43,43),4,0.8,colorCeleste,2,cv2.LINE_AA)
        cv2.putText(frame,"Darth Vader Theme",(40,80),4,0.8,colorVerde,2,cv2.LINE_AA)
        cv2.putText(frame,"Darth Vader Theme",(43,83),4,0.8,colorCeleste,2,cv2.LINE_AA)

        # Dibujo de la nota en pantalla
        cv2.circle(frame,(75+inc_x,125+inc_y),25,colorAmarillo,2)
        #Segundo circulo
        cv2.circle(frame,(75+inc_x2,125+inc_y2),25,colorAmarillo,2)
        #sjnfkjasnfsak

        # Definir las frecuencias de las notas (en Hz)
        frequencies = {
            'Mi': 659.25, 'La': 440.00, 'Sol#': 415.30, 'Si': 493.88, 'do°': 523.25, 're°': 587.33, 'mi°': 659.25, 
            'sol°': 783.99, 'la°': 880.00, 'do°': 523.25, 're°': 587.33, 'do°': 523.25, 'Mi': 659.25, 'mi°': 659.25,
            'Sol': 392.00, 'Sol#': 415.30, 'la°': 880.00, 're°': 587.33, 'La': 440.00, 'do°': 523.25
        }

        # Crear una función para generar la onda de sonido para una nota
        def generate_wave(note, duration=0.5):
            global playSound 
            playSound = False
            global reproducirUno
            reproducirUno=reproducirUno+1
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = 0.5 * np.sin(2 * np.pi * frequencies[note] * t)
            wave = (wave * 32767).astype(np.int16)
            return wave

        # Lista de notas y sus duraciones en segundos
        notes = [
            ('Mi', 0.5), ('La', 0.5), ('Sol#', 0.5), ('La', 0.5), ('Si', 0.5), ('do°', 0.5), ('Si', 0.5), ('do°', 0.5),
            ('re°', 0.5), ('mi°', 0.5), ('sol°', 0.5), ('mi°', 0.5), ('la°', 0.5), ('sol°', 0.5), ('mi°', 0.5),
            ('mi°', 0.5), ('re°', 0.5), ('do°', 0.5), ('re°', 0.5), ('do°', 0.5), ('La', 0.5),
            ('Mi', 0.5), ('La', 0.5), ('Sol#', 0.5), ('La', 0.5), ('Si', 0.5), ('do°', 0.5), ('Si', 0.5), ('do°', 0.5),
            ('re°', 0.5), ('mi°', 0.5), ('sol°', 0.5), ('mi°', 0.5), ('la°', 0.5), ('sol°', 0.5), ('mi°', 0.5),
            ('mi°', 0.5), ('re°', 0.5), ('do°', 0.5), ('re°', 0.5), ('do°', 0.5), ('La', 0.5),
            ('Mi', 0.5), ('La', 0.5), ('Sol#', 0.5), ('La', 0.5), ('Sol#', 0.5), ('La', 0.5), ('Sol#', 0.5), ('La', 0.5),
            ('Si', 0.5), ('do°', 0.5), ('do°', 0.5), ('La', 0.5), ('Sol', 0.5), ('La', 0.5), ('Sol', 0.5),
            ('Mi', 0.5), ('Mi', 0.5), ('La', 0.5), ('Sol#', 0.5), ('La', 0.5), ('Sol#', 0.5), ('La', 0.5),
            ('Sol#', 0.5), ('La', 0.5), ('Si', 0.5), ('do°', 0.5), ('do°', 0.5), ('La', 0.5), ('Sol', 0.5), ('La', 0.5), ('Sol', 0.5),
            ('Mi', 0.5), ('mi°', 0.5), ('re°', 0.5), ('do°', 0.5), ('re°', 0.5), ('do°', 0.5), ('La', 0.5),
        ]
        #sakdnñaslkfn
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 1000:
                x,y2,w,h = cv2.boundingRect(c)
                x2 = x + w//2
                if x1 is not None:
                    if coordsInCircle((75+inc_x, 125+inc_y), 25, (x2, y2)):
                        print("reproducirUno: ",reproducirUno)  
                        if playSound: 
                            playSound = False
                            wave = generate_wave(notes[reproducirUno][0], notes[reproducirUno][1])
                            print("note: ",notes[reproducirUno][0])
                            play_obj = simple.play_buffer(wave, 1, 2, 44100)
                            #play_obj.wait_done()
                            playSound = True
                        showSquare=True
                        indexRndPosition = (indexRndPosition + 1)
                        count += 1
                        break
                    if coordsInCircle((75+inc_x2, 125+inc_y2), 25, (x2, y2)):
                        print("reproducirUno: ",reproducirUno)  
                        if playSound: 
                            playSound = False
                            wave = generate_wave(notes[reproducirUno][0], notes[reproducirUno][1])
                            print("note: ",notes[reproducirUno][0])
                            play_obj = simple.play_buffer(wave, 1, 2, 44100)
                            #play_obj.wait_done()
                            playSound = True
                        showSquare2=True
                        indexRndPosition = (indexRndPosition + 1)
                        count += 1
                        break
                    if 0 < y2 < 60 or 0 < y1 < 60 :
                        imAux = imAux
                cv2.circle(frame,(x2,y2),grosor,color,3)
                x1 = x2
                y1 = y2
            else:
                x1, y1 = None, None
    elif interfaz == "Cancion_2": 
        #sajsfnkas
        if indexRndPosition == len(rndPositions):
            print("Ganaste :D")
            indexRndPosition = 0
            break
        if showSquare: # bol
            inc_x = rndPositions[indexRndPosition][0]
            inc_y = rndPositions[indexRndPosition][1]
            showSquare=False
        if showSquare2: # bol
            inc_x2 = rndPositions2[indexRndPosition][0]
            inc_y2 = rndPositions2[indexRndPosition][1]
            showSquare2=False
        cv2.rectangle(frame,(50,100), (590, 430), colorRosa, 2)
        sa=str(count)
        cv2.putText(frame,sa,(570,50),6,2,colorLimpiarPantalla,3,cv2.LINE_AA)
        cv2.putText(frame,"SCORE",(550,80),6,0.8,colorCeleste,2,cv2.LINE_AA)
        cv2.putText(frame,"Imperial March",(40,40),4,0.8,colorVerde,2,cv2.LINE_AA)
        cv2.putText(frame,"Imperial March",(43,43),4,0.8,colorCeleste,2,cv2.LINE_AA)
        cv2.putText(frame,"Darth Vader Theme",(40,80),4,0.8,colorVerde,2,cv2.LINE_AA)
        cv2.putText(frame,"Darth Vader Theme",(43,83),4,0.8,colorCeleste,2,cv2.LINE_AA)

        # Dibujo de la nota en pantalla
        cv2.circle(frame,(75+inc_x,125+inc_y),25,colorAmarillo,2)
        #Segundo circulo
        cv2.circle(frame,(75+inc_x2,125+inc_y2),25,colorAmarillo,2)
        #sjnfkjasnfsak

        # Definir las frecuencias de las notas (en Hz)
        frequencies = {
            'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00,
            'A4': 440.00, 'B4': 493.88, 'C5': 523.25
        }

        # Crear una función para generar la onda de sonido para una nota
        def generate_wave(note, duration=0.5):
            global playSound 
            playSound = False
            global reproducirUno
            reproducirUno=reproducirUno+1
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = 0.5 * np.sin(2 * np.pi * frequencies[note] * t)
            wave = (wave * 32767).astype(np.int16)
            return wave

        # "Jingle Bells" simplificado
        notes = [
            ('E4', 0.25), ('E4', 0.25), ('E4', 0.5), 
            ('E4', 0.25), ('E4', 0.25), ('E4', 0.5), 
            ('E4', 0.25), ('G4', 0.25), ('C4', 0.25), ('D4', 0.25), ('E4', 1.0), 
            ('F4', 0.25), ('F4', 0.25), ('F4', 0.25), ('F4', 0.25), 
            ('F4', 0.25), ('E4', 0.25), ('E4', 0.25), 
            ('E4', 0.25), ('E4', 0.25), ('D4', 0.25), ('D4', 0.25), 
            ('E4', 0.25), ('D4', 0.25), ('G4', 1.0)
        ]

        # Reproducir la canción
        fs = 44100  # Frecuencia de muestreo
        #sakdnñaslkfn
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 1000:
                x,y2,w,h = cv2.boundingRect(c)
                x2 = x + w//2
                if x1 is not None:
                    if coordsInCircle((75+inc_x, 125+inc_y), 25, (x2, y2)):
                        print("reproducirUno: ",reproducirUno)  
                        if playSound: 
                            playSound = False
                            wave = generate_wave(notes[reproducirUno][0], notes[reproducirUno][1])
                            print("note: ",notes[reproducirUno][0])
                            play_obj = simple.play_buffer(wave, 1, 2, 44100)
                            #play_obj.wait_done()
                            playSound = True
                        showSquare=True
                        indexRndPosition = (indexRndPosition + 1)
                        count += 1
                        break
                    if coordsInCircle((75+inc_x2, 125+inc_y2), 25, (x2, y2)):
                        print("reproducirUno: ",reproducirUno)  
                        if playSound: 
                            playSound = False
                            wave = generate_wave(notes[reproducirUno][0], notes[reproducirUno][1])
                            print("note: ",notes[reproducirUno][0])
                            play_obj = simple.play_buffer(wave, 1, 2, 44100)
                            #play_obj.wait_done()
                            playSound = True
                        showSquare2=True
                        indexRndPosition = (indexRndPosition + 1)
                        count += 1
                        break
                    if 0 < y2 < 60 or 0 < y1 < 60 :
                        imAux = imAux
                cv2.circle(frame,(x2,y2),grosor,color,3)
                x1 = x2
                y1 = y2
            else:
                x1, y1 = None, None
    elif interfaz == "Cancion_3":
        #sajsfnkas
        if indexRndPosition == len(rndPositions):
            print("Ganaste :D")
            indexRndPosition = 0
            break
        if showSquare: # bol
            inc_x = rndPositions[indexRndPosition][0]
            inc_y = rndPositions[indexRndPosition][1]
            showSquare=False
        if showSquare2: # bol
            inc_x2 = rndPositions2[indexRndPosition][0]
            inc_y2 = rndPositions2[indexRndPosition][1]
            showSquare2=False
        cv2.rectangle(frame,(50,100), (590, 430), colorRosa, 2)
        sa=str(count)
        cv2.putText(frame,sa,(570,50),6,2,colorLimpiarPantalla,3,cv2.LINE_AA)
        cv2.putText(frame,"SCORE",(550,80),6,0.8,colorCeleste,2,cv2.LINE_AA)
        cv2.putText(frame,"Imperial March",(40,40),4,0.8,colorVerde,2,cv2.LINE_AA)
        cv2.putText(frame,"Imperial March",(43,43),4,0.8,colorCeleste,2,cv2.LINE_AA)
        cv2.putText(frame,"Darth Vader Theme",(40,80),4,0.8,colorVerde,2,cv2.LINE_AA)
        cv2.putText(frame,"Darth Vader Theme",(43,83),4,0.8,colorCeleste,2,cv2.LINE_AA)

        # Dibujo de la nota en pantalla
        cv2.circle(frame,(75+inc_x,125+inc_y),25,colorAmarillo,2)
        #Segundo circulo
        cv2.circle(frame,(75+inc_x2,125+inc_y2),25,colorAmarillo,2)
        #sjnfkjasnfsak

        # Definir las frecuencias de las notas (en Hz)
        frequencies = {
            'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63,
            'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00,
            'A#4': 466.16, 'B4': 493.88, 'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 
            'D#5': 622.25, 'E5': 659.25, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99,
            'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77
        }

        # Crear una función para generar la onda de sonido para una nota
        def generate_wave(note, duration=0.5):
            global playSound 
            playSound = False
            global reproducirUno
            reproducirUno=reproducirUno+1
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = 0.5 * np.sin(2 * np.pi * frequencies[note] * t)
            wave = (wave * 32767).astype(np.int16)
            return wave
        # "Jingle Bells" simplificado
        # Notas proporcionadas
        notes = [
            # Primera secuencia
            ('D4', 0.5), ('D4', 0.5), ('G4', 0.5),
            ('G4', 0.5), ('F#4', 0.5), ('G4', 0.5), ('A4', 0.5),
            ('F#4', 0.5), ('G4', 0.5), ('A4', 0.5), ('B4', 0.5),
            ('G4', 0.5), ('A4', 0.5), ('B4', 0.5), ('C5', 0.5),
            ('C5', 0.5), ('C5', 0.5), ('B4', 0.5),
            ('A4', 0.5), ('G4', 0.5), ('F#4', 0.5), ('A4', 0.5), ('G4', 0.5),
            ('F#4', 0.5), ('G4', 0.5), ('A4', 0.5), ('B4', 0.5), ('C5', 0.5), ('A4', 0.5), ('G4', 0.5),

            # Segunda secuencia
            ('B4', 0.5), ('A4', 0.5), ('F#4', 0.5), ('F#4', 0.5), ('G4', 0.5), ('A4', 0.5), ('B4', 0.5), ('G4', 0.5),
            ('B4', 0.5), ('A4', 0.5), ('F#4', 0.5), ('F#4', 0.5), ('G4', 0.5), ('A4', 0.5), ('B4', 0.5),
            ('G4', 0.5), ('G4', 0.5), ('C5', 0.5), ('C5', 0.5), ('C5', 0.5), ('C5', 0.5), ('B4', 0.5), ('G4', 0.5),
            ('F#4', 0.5), ('G4', 0.5), ('A4', 0.5), ('B4', 0.5), ('C5', 0.5), ('A4', 0.5), ('G4', 0.5),

            # Tercera secuencia
            ('D4', 0.5), ('G4', 0.5), 
            ('F#4', 0.5), ('G4', 0.5), ('G4', 0.5), 
            ('F#4', 0.5), ('G4', 0.5), ('G4', 0.5),
            ('G4', 0.5), ('B4', 0.5), ('A4', 0.5), ('G4', 0.5),
            ('F#4', 0.5), ('G4', 0.5), ('A4', 0.5), ('A4', 0.5),
            ('D4', 0.5), ('D4', 0.5), ('G4', 0.5), ('A4', 0.5), ('A4', 0.5), ('G4', 0.5), ('A4', 0.5), ('A4', 0.5),
            ('B4', 0.5), ('C5', 0.5), ('B4', 0.5), ('B4', 0.5), ('A4', 0.5), ('A4', 0.5), ('F#4', 0.5), ('G4', 0.5),

            # Cuarta secuencia
            ('A4', 0.5), ('G4', 0.5), ('F#4', 0.5), ('E4', 0.5), ('F#4', 0.5), ('G4', 0.5), ('A4', 0.5),
            ('G4', 0.5), ('A4', 0.5), ('B4', 0.5), ('C5', 0.5),
            ('B4', 0.5), ('C5', 0.5), ('C5', 0.5), ('B4', 0.5), ('C5', 0.5),
            ('B4', 0.5), ('A4', 0.5), ('G4', 0.5), ('F#4', 0.5), ('G4', 0.5), ('A4', 0.5), ('B4', 0.5), ('B4', 0.5),
            ('B4', 0.5), ('C5', 0.5), ('B4', 0.5), ('B4', 0.5), ('A4', 0.5), ('A4', 0.5), ('F#4', 0.5), ('G4', 0.5)
        ]

        # Reproducir la canción
        fs = 44100  # Frecuencia de muestreo
        #sakdnñaslkfn
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 1000:
                x,y2,w,h = cv2.boundingRect(c)
                x2 = x + w//2
                if x1 is not None:
                    if coordsInCircle((75+inc_x, 125+inc_y), 25, (x2, y2)):
                        print("reproducirUno: ",reproducirUno)  
                        if playSound: 
                            playSound = False
                            wave = generate_wave(notes[reproducirUno][0], notes[reproducirUno][1])
                            print("note: ",notes[reproducirUno][0])
                            play_obj = simple.play_buffer(wave, 1, 2, 44100)
                            #play_obj.wait_done()
                            playSound = True
                        showSquare=True
                        indexRndPosition = (indexRndPosition + 1)
                        count += 1
                        break
                    if coordsInCircle((75+inc_x2, 125+inc_y2), 25, (x2, y2)):
                        print("reproducirUno: ",reproducirUno)  
                        if playSound: 
                            playSound = False
                            wave = generate_wave(notes[reproducirUno][0], notes[reproducirUno][1])
                            print("note: ",notes[reproducirUno][0])
                            play_obj = simple.play_buffer(wave, 1, 2, 44100)
                            #play_obj.wait_done()
                            playSound = True
                        showSquare2=True
                        indexRndPosition = (indexRndPosition + 1)
                        count += 1
                        break
                    if 0 < y2 < 60 or 0 < y1 < 60 :
                        imAux = imAux
                cv2.circle(frame,(x2,y2),grosor,color,3)
                x1 = x2
                y1 = y2
            else:
                x1, y1 = None, None
    elif interfaz == "tutorial":
        tutorialImg = cv2.imread("./TutorialInteraccion.png")
        frame = tutorialImg
        cv2.rectangle(frame, (6, 6), (42, 42), colorRosa, 2)
        cv2.line(frame, (14, 14), (34, 34), colorRosa, 2)
        cv2.line(frame, (14, 34), (34, 14), colorRosa, 2)
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 1000:
                x,y2,w,h = cv2.boundingRect(c)
                x2 = x + w//2
                if x1 is not None:
                    if 6 < x2 < 42 and 6 < y1 < 42:
                        interfaz = "menu"
                cv2.circle(frame,(x2,y2),grosor,color,3)
                x1 = x2
                y1 = y2
            else:
                x1, y1 = None, None
    

    imAuxGray = cv2.cvtColor(imAux,cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(imAuxGray,10,255,cv2.THRESH_BINARY)
    thInv = cv2.bitwise_not(th)
    frame = cv2.bitwise_and(frame,frame,mask=thInv)
    frame = cv2.add(frame,imAux)

    cv2.imshow('Game', frame)

    k = cv2.waitKey(1)
    if k == 27:
        break


cap.release()
cv2.destroyAllWindows()