import cv2
import time
import easyocr

cap = cv2.VideoCapture(0)
reader = easyocr.Reader(['pt'])
tempo = time.time()

BRANCO = (255,255,255)
VERDE = (0,255,0)
VERMELHO  =(0,0,255)  

placas =['BRA2E19']
tempo_espera = 2

passou = False
placa = ''

def Desenha_Interface(img, passou, placa):
    cv2.rectangle(img, (0, 0), (600, 110), (0, 0, 0, 0.5), -1)
    cv2.putText(img, f"Placa_Permitidas : {placas}", (20, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, BRANCO, 2)
    
    cv2.putText(img, f"Placa_Detectada : {placa}", (20, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, VERDE if passou else VERMELHO, 2)
    
    cv2.putText(img, f"PASSAGEM {"LIBERADA" if passou else "NEGADA"}", (20, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, VERDE if passou else VERMELHO, 2)

def Verifica_Placa():
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = reader.readtext(gray)

    for detection in result:

        print("Texto detectado:", detection[1])
        placa =''

        for x in detection[1].upper():
            if(x!= " "):
                placa += x

        if(placa in placas):
            return True, placa
        else:
            return False, placa
    
    return False, 'NENHUMA'

while True:
    ret, frame = cap.read()


    if(time.time() - tempo > tempo_espera):
        passou, placa = Verifica_Placa() 
        tempo = time.time()

    Desenha_Interface(frame, passou, placa)

    cv2.imshow("Camera", frame)

    if cv2.getWindowProperty("Camera", cv2.WND_PROP_VISIBLE) < 1:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

