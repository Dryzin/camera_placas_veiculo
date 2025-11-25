from banco_dados import BancoDeDados

db = BancoDeDados()

# Insert Base
sucesso = db.cadastrar_veiculo(
    placa="BRA2E19", 
    proprietario="João da Silva", 
    tipo="CARRO", 
    categoria="OFICIAL",
    status="AUTORIZADO"
)

if sucesso:
    print("Veículo BRA2E19 cadastrado com sucesso!")
else:
    print("Erro: Veículo já cadastrado.")

db.fechar()