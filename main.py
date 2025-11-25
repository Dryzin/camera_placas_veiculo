import cv2
import time
import easyocr
from ultralytics import YOLO
from banco_dados import BancoDeDados

# Inicializa o banco
db = BancoDeDados()

# modelo YOLO - Ler moto e carro
model = YOLO('yolov8n.pt') 

# Inicializa OCR
print("Carregando OCR...")
reader = easyocr.Reader(['pt'])

# Inicializa Câmera
cap = cv2.VideoCapture(0)

# Variáveis de Controle
tempo_ref = time.time()
tempo_espera_ocr = 2  # Executa OCR a cada 2 segundos para não travar o PC
info_veiculo_db = None 
placa_lida_texto = "Aguardando..."
tipo_veiculo_visual = "Nenhum"

# Cores (B, G, R)
BRANCO = (255, 255, 255)
VERDE = (0, 255, 0)
VERMELHO = (0, 0, 255)
AZUL = (255, 0, 0)
AMARELO = (0, 255, 255)

def Processar_Visao_IA(frame):
    """
    Usa YOLO para detectar veículos e desenhar caixas.
    Retorna o frame desenhado e o tipo de veículo principal detectado.
    """
    # classes do COCO dataset: 2=carro, 3=moto, 5=ônibus, 7=caminhão
    classes_interesse = [2, 3, 5, 7]
    tipo_detectado = None

    # Roda a YODO (conf=0.5 significa que só mostra se tiver 50% de certeza)
    results = model(frame, stream=True, verbose=False, conf=0.5)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls = int(box.cls[0])
            
            if cls in classes_interesse:
                # Define o nome
                if cls == 2: nome = "CARRO"
                elif cls == 3: nome = "MOTO"
                elif cls == 5: nome = "ONIBUS"
                else: nome = "CAMINHAO"
                
                tipo_detectado = nome

                # Coordenadas do retângulo
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Desenha o retângulo AZUL ao redor do veículo
                cv2.rectangle(frame, (x1, y1), (x2, y2), AZUL, 2)
                cv2.putText(frame, nome, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, AZUL, 2)

    return tipo_detectado

def Tentar_Ler_Placa(frame):
    """
    Função pesada: Roda o OCR para tentar ler texto
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Otimização: ler apenas uma faixa central da imagem se possível
    # Mas aqui vamos ler tudo
    result = reader.readtext(gray)
    
    placa_encontrada = ""
    
    for detection in result:
        texto = detection[1]
        # Limpa o texto (tira espaços e simbolos)
        temp = ''.join(e for e in texto if e.isalnum()).upper()
        
        # Filtro básico de placa (tem que ter 7 digitos)
        if len(temp) == 7:
            placa_encontrada = temp
            break 
            
    return placa_encontrada

def Desenha_Interface(img, info_db, placa_ocr, tipo_visual):
    # Cria uma barra lateral ou superior para as informações
    # Retângulo de Fundo
    cv2.rectangle(img, (0, 0), (300, 250), (0, 0, 0), -1)
    
    # Visao da IA
    cv2.putText(img, f"Visual: {tipo_visual}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, AZUL, 2)

    # Leitura do OCR
    cv2.putText(img, f"Placa: {placa_ocr}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, BRANCO, 2)

    cv2.line(img, (10, 75), (290, 75), BRANCO, 1)

    # Informações do Banco de Dados
    if info_db:
        cor_status = VERDE if info_db['status'] == 'AUTORIZADO' else VERMELHO
        
        cv2.putText(img, f"Dono: {info_db['proprietario']}", (10, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, BRANCO, 1)
        
        cv2.putText(img, f"Cadastro: {info_db['tipo']}", (10, 125), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, AMARELO, 1)
        
        # Alerta se o visual não bater com o cadastro (Ex: Placa de carro em uma moto)
        if tipo_visual and tipo_visual != "Nenhum" and info_db['tipo'] != tipo_visual:
             cv2.putText(img, "DIVERGENCIA DE TIPO!", (10, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, VERMELHO, 2)
        
        # Status
        cv2.putText(img, info_db['status'], (10, 200), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, cor_status, 3)
    else:
        if placa_ocr not in ["Aguardando...", "NENHUMA", ""]:
             cv2.putText(img, "NAO CADASTRADO", (10, 200), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, VERMELHO, 2)

# --- LOOP PRINCIPAL ---
while True:
    ret, frame = cap.read()
    if not ret: break

    # PRocesso do YODO
    tipo_detectado = Processar_Visao_IA(frame)
    if tipo_detectado:
        tipo_veiculo_visual = tipo_detectado

    # Processamento TEXTUAL (OCR) - roda a cada X segundos
    if time.time() - tempo_ref > tempo_espera_ocr:
        placa_temp = Tentar_Ler_Placa(frame)
        
        if placa_temp:
            placa_lida_texto = placa_temp
            # consulta no banco
            info_veiculo_db = db.buscar_veiculo(placa_lida_texto)
            
            if info_veiculo_db:
                # se achou e é autorizado, registra acesso
                if info_veiculo_db['status'] == 'AUTORIZADO':
                    db.registrar_acesso(placa_lida_texto)
        else:
            # se não leu nada claro, reseta ou mantem o ultimo (opcional)
            pass
            
        tempo_ref = time.time()

    # atualiza Interface
    Desenha_Interface(frame, info_veiculo_db, placa_lida_texto, tipo_veiculo_visual)

    cv2.imshow("Sistema de Controle de Acesso Inteligente", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
db.fechar()