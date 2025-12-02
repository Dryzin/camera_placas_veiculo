import cv2
import time
import easyocr
import numpy as np
from ultralytics import YOLO
from banco_dados import BancoDeDados 

# --- CONFIGURAÇÕES GERAIS ---
LARGURA_TELA = 1280
ALTURA_TELA = 720
COR_FUNDO = (30, 30, 30)
COR_PAINEL = (50, 50, 50)
COR_TEXTO = (200, 200, 200)
VERDE = (0, 255, 0)
VERMELHO = (0, 0, 255)
AZUL = (255, 0, 0)
AMARELO = (0, 255, 255)

# --- INICIALIZAÇÃO ---
print(">>> Inicializando Banco de Dados...")
db = BancoDeDados()

print(">>> Carregando IA (YOLO)...")
model = YOLO('yolov8n.pt') 

print(">>> Carregando Leitor de Placas (OCR)...")
reader = easyocr.Reader(['pt'], gpu=False) # Mude gpu=True se tiver placa de vídeo NVIDIA

cap = cv2.VideoCapture(0)

# Variáveis de Controle
tempo_ref = time.time()
tempo_espera_ocr = 2.0  
info_veiculo_db = None 
placa_lida_texto = "--"
tipo_veiculo_visual = "--"
ultimo_acesso_status = "AGUARDANDO"

def criar_interface_base():
    """Cria o canvas preto HD para desenharmos em cima"""
    img = np.zeros((ALTURA_TELA, LARGURA_TELA, 3), dtype=np.uint8)
    img[:] = COR_FUNDO
    # Desenha a área do painel lateral
    cv2.rectangle(img, (800, 0), (LARGURA_TELA, ALTURA_TELA), COR_PAINEL, -1)
    return img

def processar_ocr_inteligente(img_recorte):
    """
    Tenta ler a placa. Se for moto, tenta juntar linhas quebradas.
    """
    gray = cv2.cvtColor(img_recorte, cv2.COLOR_BGR2GRAY)
    
    # Aumenta contraste para ajudar na leitura
    gray = cv2.equalizeHist(gray) 

    result = reader.readtext(gray)
    
    canditatos = []
    
    # 1. Tenta achar placa em uma linha só (Padrão Carro)
    for detection in result:
        texto = detection[1]
        limpo = ''.join(e for e in texto if e.isalnum()).upper()
        if len(limpo) == 7:
            return limpo # Achou perfeito
        canditatos.append(limpo)

    # 2. Estratégia Moto (Placa Mercosul Quadrada):
    # O OCR pode ler 'BRA' depois '2E19'. Vamos tentar juntar pedaços.
    texto_completo = "".join(canditatos)
    if len(texto_completo) >= 7:
        # Pega apenas os ultimos 7 caracteres (caso tenha lido sujeira antes)
        # ou tenta achar padrao LLLNLNN
        possivel_placa = texto_completo[-7:] 
        # Validação simples: 3 primeiros letras, 4º numero (Mercosul Antigo) ou Letra (Mercosul Novo)
        if possivel_placa[0].isalpha() and possivel_placa[1].isalpha():
            return possivel_placa

    return None

def main():
    global tempo_ref, info_veiculo_db, placa_lida_texto, tipo_veiculo_visual, ultimo_acesso_status

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Redimensiona o frame da câmera para caber na nossa interface (800x600)
        frame_resized = cv2.resize(frame, (800, 600))
        
        # Cria o fundo da aplicação
        interface = criar_interface_base()
        
        # --- DETECÇÃO VISUAL (YOLO) ---
        # Detecta apenas na imagem da camera
        results = model(frame_resized, stream=True, verbose=False, conf=0.5)
        
        roi_veiculo = None # Região de Interesse (Recorte do veiculo)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                
                # 2=Carro, 3=Moto, 5=Onibus, 7=Caminhao
                if cls in [2, 3, 5, 7]:
                    # Identifica tipo
                    if cls == 2: tipo_veiculo_visual = "CARRO"
                    elif cls == 3: tipo_veiculo_visual = "MOTO"
                    elif cls == 5: tipo_veiculo_visual = "ONIBUS"
                    else: tipo_veiculo_visual = "CAMINHAO"

                    # Desenha Box no Vídeo
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cor_box = AZUL
                    if tipo_veiculo_visual == "MOTO": cor_box = AMARELO # Destaca moto
                    
                    cv2.rectangle(frame_resized, (x1, y1), (x2, y2), cor_box, 2)
                    cv2.putText(frame_resized, tipo_veiculo_visual, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_box, 2)

                    # --- LOGICA DE CORTE (ROI) PARA OCR ---
                    # Recortamos a imagem do veículo para o OCR focar só nele
                    # Adicionamos uma margem de segurança
                    h, w, _ = frame_resized.shape
                    y1_c = max(0, y1)
                    y2_c = min(h, y2)
                    x1_c = max(0, x1)
                    x2_c = min(w, x2)
                    
                    roi_veiculo = frame_resized[y1_c:y2_c, x1_c:x2_c]

        # --- RECONHECIMENTO DE PLACA (OCR) ---
        # Só roda se passou o tempo E se existe um veículo detectado para focar
        if (time.time() - tempo_ref > tempo_espera_ocr) and roi_veiculo is not None:
            
            # Tenta ler no recorte (Zoom no veiculo) - Muito melhor para motos
            placa_detectada = processar_ocr_inteligente(roi_veiculo)
            
            if not placa_detectada:
                # Se falhar no recorte, tenta na imagem inteira (backup)
                placa_detectada = processar_ocr_inteligente(frame_resized)

            if placa_detectada:
                placa_lida_texto = placa_detectada
                
                # Busca no Banco
                info = db.buscar_veiculo(placa_lida_texto)
                
                if info:
                    info_veiculo_db = info
                    if info['status'] == 'AUTORIZADO':
                        ultimo_acesso_status = "AUTORIZADO"
                        db.registrar_acesso(placa_lida_texto)
                    else:
                        ultimo_acesso_status = "BLOQUEADO"
                else:
                    info_veiculo_db = None
                    ultimo_acesso_status = "NAO CADASTRADO"
            
            tempo_ref = time.time()

        # --- MONTAGEM DA INTERFACE ---
        
        # 1. Cola o vídeo da câmera na esquerda
        # Centraliza verticalmente (720 - 600) / 2 = 60
        y_offset = 60
        interface[y_offset:y_offset+600, 0:800] = frame_resized

        # 2. Desenha o Painel de Informações (Direita)
        col_x = 830 # Margem esquerda do painel
        
        # Cabeçalho
        cv2.putText(interface, "SISTEMA DE ACESSO", (col_x, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, COR_TEXTO, 2)
        cv2.line(interface, (col_x, 60), (LARGURA_TELA - 30, 60), COR_TEXTO, 1)

        # Status Visual da IA
        cv2.putText(interface, "Veiculo Detectado:", (col_x, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COR_TEXTO, 1)
        cv2.putText(interface, tipo_veiculo_visual, (col_x, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.2, AMARELO, 3)

        # Placa Lida
        cv2.putText(interface, "Placa Lida (OCR):", (col_x, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COR_TEXTO, 1)
        cv2.rectangle(interface, (col_x, 260), (LARGURA_TELA-30, 340), (255,255,255), 2) # Caixa da placa
        cv2.putText(interface, placa_lida_texto, (col_x + 20, 320), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 4)

        # Dados do Banco
        if info_veiculo_db:
            cv2.putText(interface, f"Proprietario: {info_veiculo_db['proprietario']}", (col_x, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COR_TEXTO, 1)
            cv2.putText(interface, f"Tipo Cadastrado: {info_veiculo_db['tipo']}", (col_x, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COR_TEXTO, 1)
            
            # Alerta de divergência (Carro vs Moto)
            if tipo_veiculo_visual not in ["--", "Nenhum"] and info_veiculo_db['tipo'] != tipo_veiculo_visual:
                cv2.rectangle(interface, (col_x, 450), (LARGURA_TELA-30, 480), VERMELHO, -1)
                cv2.putText(interface, "ALERTA: TIPO DIVERGENTE", (col_x + 10, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
        else:
             cv2.putText(interface, "Aguardando leitura válida...", (col_x, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100,100,100), 1)

        # Resultado Final (Status Grande)
        cor_status = VERDE
        if ultimo_acesso_status == "BLOQUEADO": cor_status = VERMELHO
        elif ultimo_acesso_status == "NAO CADASTRADO": cor_status = AZUL
        elif ultimo_acesso_status == "AGUARDANDO": cor_status = (100,100,100)

        cv2.rectangle(interface, (col_x, 550), (LARGURA_TELA-30, 650), cor_status, -1)
        # Centraliza texto do status
        texto_status = ultimo_acesso_status
        (w_text, h_text), _ = cv2.getTextSize(texto_status, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)
        centro_x = col_x + (LARGURA_TELA - 30 - col_x - w_text) // 2
        cv2.putText(interface, texto_status, (centro_x, 615), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)

        # Rodapé
        cv2.putText(interface, "Pressione 'Q' para sair", (col_x, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 1)

        # Mostra a Interface Final
        cv2.imshow("Sistema de Controle de Acesso - IF Machado", interface)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    db.fechar()

if __name__ == "__main__":
    main()