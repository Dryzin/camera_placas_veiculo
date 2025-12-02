import cv2
import time
import easyocr
from ultralytics import YOLO
from banco_dados import BancoDeDados

# Inicializa o banco
db = BancoDeDados()

# YOLO - Modelo para detecção de veículos
model = YOLO('yolov8n.pt')

# Inicializa OCR
reader = easyocr.Reader(['pt'])

# Inicializa Câmera
cap = cv2.VideoCapture(0)

# Variáveis de Controle
tempo_ref = time.time()
tempo_espera_ocr = 2
info_veiculo_db = None
placa_lida_texto = "Aguardando..."
tipo_veiculo_visual = "Nenhum"

# Cores (B, G, R)
CORES = {
    "BRANCO": (255, 255, 255),
    "VERDE": (0, 255, 0),
    "VERMELHO": (0, 0, 255),
    "AZUL": (255, 0, 0),
    "AMARELO": (0, 255, 255),
}

CLASSES_INTERESSE = {2: "CARRO", 3: "MOTO", 5: "ONIBUS", 7: "CAMINHAO"}

def processar_visao_ia(frame):
    """
    Usa YOLO para detectar veículos e desenhar caixas.
    Retorna o frame desenhado e o tipo de veículo principal detectado.
    """
    tipo_detectado = None
    results = model(frame, stream=True, verbose=False, conf=0.5)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if cls in CLASSES_INTERESSE:
                tipo_detectado = CLASSES_INTERESSE[cls]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), CORES["AZUL"], 2)
                cv2.putText(frame, tipo_detectado, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, CORES["AZUL"], 2)
    return tipo_detectado

def tentar_ler_placa(frame):
    """
    Roda o OCR para tentar ler texto.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = reader.readtext(gray)
    for detection in result:
        texto = ''.join(e for e in detection[1] if e.isalnum()).upper()
        if len(texto) == 7:  # Filtro básico de placa
            return texto
    return ""

def desenha_interface(img, info_db, placa_ocr, tipo_visual):
    """
    Desenha a interface com informações no frame.
    """
    cv2.rectangle(img, (0, 0), (300, 250), (0, 0, 0), -1)
    cv2.putText(img, f"Visual: {tipo_visual}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, CORES["AZUL"], 2)
    cv2.putText(img, f"Placa: {placa_ocr}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, CORES["BRANCO"], 2)
    cv2.line(img, (10, 75), (290, 75), CORES["BRANCO"], 1)

    if info_db:
        cor_status = CORES["VERDE"] if info_db['status'] == 'AUTORIZADO' else CORES["VERMELHO"]
        cv2.putText(img, f"Dono: {info_db['proprietario']}", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, CORES["BRANCO"], 1)
        cv2.putText(img, f"Cadastro: {info_db['tipo']}", (10, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, CORES["AMARELO"], 1)
        if tipo_visual and tipo_visual != "Nenhum" and info_db['tipo'] != tipo_visual:
            cv2.putText(img, "DIVERGENCIA DE TIPO!", (10, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, CORES["VERMELHO"], 2)
        cv2.putText(img, info_db['status'], (10, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, cor_status, 3)
    else:
        if placa_ocr not in ["Aguardando...", "NENHUMA", ""]:
            cv2.putText(img, "NAO CADASTRADO", (10, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, CORES["VERMELHO"], 2)

# --- LOOP PRINCIPAL ---
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao acessar a câmera.")
            break

        tipo_detectado = processar_visao_ia(frame)
        if tipo_detectado:
            tipo_veiculo_visual = tipo_detectado

        if time.time() - tempo_ref > tempo_espera_ocr:
            placa_temp = tentar_ler_placa(frame)
            if placa_temp:
                placa_lida_texto = placa_temp
                info_veiculo_db = db.buscar_veiculo(placa_lida_texto)
                if info_veiculo_db and info_veiculo_db['status'] == 'AUTORIZADO':
                    db.registrar_acesso(placa_lida_texto)
            tempo_ref = time.time()

        desenha_interface(frame, info_veiculo_db, placa_lida_texto, tipo_veiculo_visual)
        cv2.imshow("Sistema de Controle de Acesso Inteligente", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except Exception as e:
    print(f"Erro: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    db.fechar()