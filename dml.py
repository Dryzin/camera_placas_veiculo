from banco_dados import BancoDeDados

def popular_banco():
    db = BancoDeDados()
    
    dados_mock = [
        ("RIO2A19", "Ricardo Alves", "CARRO", "PARTICULAR", "AUTORIZADO"),
        ("BRA2E19", "Fernanda Torres", "CARRO", "PARTICULAR", "AUTORIZADO"),
        ("PRF1A03", "Claudio Santos", "MOTO", "PARTICULAR", "AUTORIZADO"),
        ("PRF1A04", "Beatriz Lima", "CARRO", "OFICIAL", "AUTORIZADO"),
        ("PRF1A05", "Jorge Mendes", "CARRO", "PARTICULAR", "AUTORIZADO"),
        ("PRF1A06", "Juliana Costa", "MOTO", "PARTICULAR", "AUTORIZADO"),
        ("PRF1A07", "Eduardo Silva", "CARRO", "PARTICULAR", "AUTORIZADO"),
        ("POX4G21", "Mariana Dias", "CARRO", "PARTICULAR", "BLOQUEADO"),

        ("SEG2B01", "Paulo Roberto", "MOTO", "OFICIAL", "AUTORIZADO"),
        ("SEG2B02", "Carlos Eduardo", "CARRO", "OFICIAL", "AUTORIZADO"),
        ("SEG2B03", "Andre Gomes", "MOTO", "PARTICULAR", "AUTORIZADO"),
        ("SEG2B04", "Rafael Nunes", "MOTO", "OFICIAL", "AUTORIZADO"),

        ("COZ3C01", "Maria Helena", "CARRO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C02", "Joao Batista", "MOTO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C03", "Ana Paula", "CARRO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C04", "Antonio Carlos", "MOTO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C05", "Francisca Silva", "CARRO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C06", "Luiz Felipe", "MOTO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C07", "Adriana Pereira", "CARRO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C08", "Marcia Santos", "MOTO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C09", "Jose Roberto", "CARRO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C10", "Patricia Gomes", "MOTO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C11", "Sandra Ferreira", "CARRO", "PARTICULAR", "AUTORIZADO"),
        ("COZ3C12", "Lucas Martins", "MOTO", "PARTICULAR", "BLOQUEADO")
    ]

    print(f"Iniciando carga de {len(dados_mock)} registros...")
    
    sucessos = 0
    erros = 0

    for item in dados_mock:
        # Desempacota os dados da tupla
        placa, nome, tipo, cat, status = item
        
        # Chama a função de cadastro
        resultado = db.cadastrar_veiculo(
            placa=placa,
            proprietario=nome,
            tipo=tipo,
            categoria=cat,
            status=status
        )

        if resultado:
            print(f"[OK] {placa} - {nome}")
            sucessos += 1
        else:
            print(f"[X]  {placa} já existe no banco.")
            erros += 1

    db.fechar()
    print("-" * 30)
    print(f"Concluído! Inseridos: {sucessos} | Duplicados: {erros}")

if __name__ == "__main__":
    popular_banco()