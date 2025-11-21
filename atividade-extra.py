import json
import os
from datetime import datetime, timedelta

# ==============================================================================
# DECLARAÇÃO DE VARIÁVEIS GLOBAIS (Requisitos 3, 5, 11)
# ==============================================================================

# Lista principal que armazena todas as tarefas ativas (Pendente, Fazendo, Concluída)
LISTA_TAREFAS = []

# Variável de controle do sistema para o ID único de cada tarefa
PROXIMO_ID = 1

# Constantes para validação e regras de negócio
OPCOES_PRIORIDADE = ["Urgente", "Alta", "Média", "Baixa"]
OPCOES_STATUS = ["Pendente", "Fazendo", "Concluída", "Arquivado", "Excluída"]
OPCOES_ORIGEM = ["E-mail", "Telefone", "Chamado do Sistema"]
ARQUIVO_PRINCIPAL = 'tarefas.json'
ARQUIVO_ARQUIVADAS = 'tarefas_arquivadas.json'

# ==============================================================================
# FUNÇÕES DE PERSISTÊNCIA E ARQUIVOS (Requisitos 13, 14, 15)
# ==============================================================================

def criar_arquivos_se_nao_existirem():
    """
    Item Extra (15): Verifica e cria os arquivos JSON obrigatórios
    (tarefas.json e tarefas_arquivadas.json) com estrutura inicial vazia '[]'
    se eles não existirem na pasta de execução.
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função criar_arquivos_se_nao_existirem")
    for arquivo in [ARQUIVO_PRINCIPAL, ARQUIVO_ARQUIVADAS]:
        if not os.path.exists(arquivo):
            try:
                with open(arquivo, 'w') as f:
                    json.dump([], f)
                print(f"Arquivo '{arquivo}' criado automaticamente com sucesso.")
            except IOError as e:
                print(f"Erro ao criar o arquivo {arquivo}: {e}")

def carregar_dados_iniciais():
    """
    Carrega os dados do arquivo tarefas.json para a LISTA_TAREFAS global no
    início da execução. Também atualiza o PROXIMO_ID. (Requisito 13)
    Parâmetros: nenhum
    Retorno: nenhum
    """
    global LISTA_TAREFAS
    global PROXIMO_ID
    print("Executando a função carregar_dados_iniciais")

    criar_arquivos_se_nao_existirem()

    try:
        with open(ARQUIVO_PRINCIPAL, 'r') as f:
            LISTA_TAREFAS = json.load(f)
            if LISTA_TAREFAS:
                # Encontra o ID máximo e incrementa para definir o próximo ID
                PROXIMO_ID = max(tarefa.get('ID', 0) for tarefa in LISTA_TAREFAS) + 1
            print(f"Dados carregados de {ARQUIVO_PRINCIPAL}. Total de tarefas: {len(LISTA_TAREFAS)}")
    except FileNotFoundError:
        # Se o arquivo não existir (embora a criação automática ajude)
        print(f"Arquivo '{ARQUIVO_PRINCIPAL}' não encontrado. Iniciando com lista vazia.")
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON em '{ARQUIVO_PRINCIPAL}'. Iniciando com lista vazia.")

def salvar_tarefas(lista_para_salvar=LISTA_TAREFAS, nome_arquivo=ARQUIVO_PRINCIPAL):
    """
    Salva a lista de tarefas no arquivo JSON especificado. (Requisito 13)
    Parâmetros:
        lista_para_salvar (list): A lista de dicionários (tarefas) a ser salva.
        nome_arquivo (str): O nome do arquivo JSON.
    Retorno: nenhum
    """
    print(f"Executando a função salvar_tarefas no arquivo {nome_arquivo}")
    try:
        with open(nome_arquivo, 'w') as f:
            json.dump(lista_para_salvar, f, indent=4)
    except IOError as e:
        print(f"ERRO: Não foi possível salvar no arquivo {nome_arquivo}: {e}")

def arquivar_tarefas(tarefas_a_arquivar):
    """
    Salva tarefas em tarefas_arquivadas.json (acumulativo) antes de remover da 
    lista principal. (Requisito 14)
    Parâmetros:
        tarefas_a_arquivar (list): Lista de tarefas a serem movidas para o histórico.
    Retorno: nenhum
    """
    print("Executando a função arquivar_tarefas")
    if not tarefas_a_arquivar:
        print("Nenhuma tarefa para arquivar.")
        return

    # 1. Carregar tarefas arquivadas existentes
    tarefas_historico = []
    try:
        with open(ARQUIVO_ARQUIVADAS, 'r') as f:
            tarefas_historico = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver vazio, começa com lista vazia
        pass

    # 2. Adicionar as novas tarefas a arquivar
    tarefas_historico.extend(tarefas_a_arquivar)

    # 3. Salvar o histórico atualizado
    salvar_tarefas(tarefas_historico, ARQUIVO_ARQUIVADAS)
    print(f"{len(tarefas_a_arquivar)} tarefa(s) movida(s) para {ARQUIVO_ARQUIVADAS}.")

# ==============================================================================
# FUNÇÕES DE VALIDAÇÃO E UTILIDADE (Requisitos 8, 9, 10)
# ==============================================================================

def valida_string_nao_vazia(prompt):
    """
    Função de Validação (8): Garante que a entrada do usuário não seja vazia.
    Parâmetros:
        prompt (str): Mensagem a ser exibida para o usuário.
    Retorno:
        str: A string de entrada validada.
    """
    print("Executando a função valida_string_nao_vazia")
    while True:
        entrada = input(prompt).strip()
        if entrada:
            return entrada
        else:
            print("Campo obrigatório. Por favor, insira uma informação válida.")

def valida_opcao_menu(mensagem, opcoes_validas):
    """
    Função de Validação (8) e Tratamento de Exceções (9):
    Valida a opção do menu e trata erros de conversão de tipo.
    Parâmetros:
        mensagem (str): Mensagem a ser exibida para o usuário.
        opcoes_validas (dict_keys): Chaves válidas do menu.
    Retorno:
        int: O número da opção válida.
    """
    print("Executando a função valida_opcao_menu")
    while True:
        try:
            opcao_str = input(mensagem).strip()
            opcao = int(opcao_str)
            if opcao in opcoes_validas:
                return opcao
            else:
                print(f"Opção inválida. Escolha um número válido.")
        except ValueError:
            print("Entrada inválida. Por favor, digite apenas o número da opção desejada.")

def valida_escolha_lista(prompt, opcoes_validas):
    """
    Função de Validação (8): Garante que a escolha do usuário esteja
    em uma lista predefinida de opções (Prioridade, Origem, etc.).
    Parâmetros:
        prompt (str): Mensagem a ser exibida.
        opcoes_validas (list): Lista de opções aceitas.
    Retorno:
        str: A opção escolhida validada.
    """
    print("Executando a função valida_escolha_lista")
    opcoes_formatadas = ", ".join(opcoes_validas)
    print(f"Opções disponíveis: {opcoes_formatadas}")
    while True:
        escolha = input(prompt).strip()
        if escolha in opcoes_validas:
            return escolha
        else:
            print(f"Escolha inválida. Por favor, escolha uma das seguintes opções: {opcoes_formatadas}")

def buscar_tarefa_por_id(id_tarefa):
    """
    Busca uma tarefa na lista principal pelo ID.
    Parâmetros:
        id_tarefa (int): O ID da tarefa a ser buscada.
    Retorno:
        dict/None: O dicionário da tarefa encontrada ou None.
    """
    print("Executando a função buscar_tarefa_por_id")
    for tarefa in LISTA_TAREFAS:
        if tarefa.get('ID') == id_tarefa:
            return tarefa
    return None

def solicitar_id_valido():
    """
    Tratamento de Exceções (9): Solicita um ID de tarefa e trata a entrada não numérica.
    Parâmetros: nenhum
    Retorno:
        dict/None: O dicionário da tarefa encontrada ou None se não existir.
    """
    print("Executando a função solicitar_id_valido")
    while True:
        try:
            id_str = input("Digite o ID da tarefa: ").strip()
            id_tarefa = int(id_str)
            tarefa = buscar_tarefa_por_id(id_tarefa)
            if tarefa:
                return tarefa
            else:
                print(f"ERRO: Tarefa com ID {id_tarefa} não encontrada na lista ativa.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número para o ID da tarefa.")

def calcular_tempo_execucao(data_criacao_str, data_conclusao_str):
    """
    Calcula o tempo decorrido entre a criação e a conclusão. (Requisito 7)
    Parâmetros:
        data_criacao_str (str): Data e hora de criação no formato ISO.
        data_conclusao_str (str): Data e hora de conclusão no formato ISO.
    Retorno:
        str: Tempo formatado em dias, horas e minutos.
    """
    print("Executando a função calcular_tempo_execucao")
    try:
        data_criacao = datetime.fromisoformat(data_criacao_str)
        data_conclusao = datetime.fromisoformat(data_conclusao_str)
        delta = data_conclusao - data_criacao
        
        # Formata o delta em Dias, Horas, Minutos
        dias = delta.days
        horas, resto = divmod(delta.seconds, 3600)
        minutos, segundos = divmod(resto, 60)
        
        return f"{dias} dias, {horas}h{minutos}m"
    except ValueError:
        return "Erro no cálculo (formato de data inválido)"

# ==============================================================================
# FUNÇÕES DO CICLO DE VIDA DA TAREFA (Requisitos 1 a 8)
# ==============================================================================

def criar_tarefa():
    """
    Cria uma nova tarefa, solicitando informações ao usuário, validando os dados
    e adicionando a tarefa à LISTA_TAREFAS global. (Requisito 1)
    Parâmetros: nenhum
    Retorno: nenhum
    """
    global PROXIMO_ID
    print("Executando a função criar_tarefa")

    # Coleta e validação de dados
    titulo = valida_string_nao_vazia("Título da Tarefa (Obrigatório): ")
    descricao = input("Descrição detalhada (Opcional): ")
    prioridade = valida_escolha_lista("Prioridade (Urgente, Alta, Média, Baixa): ", OPCOES_PRIORIDADE)
    origem = valida_escolha_lista("Origem da Tarefa (E-mail, Telefone, Chamado do Sistema): ", OPCOES_ORIGEM)
    data_criacao = datetime.now().isoformat()

    nova_tarefa = {
        'ID': PROXIMO_ID,
        'Título': titulo,
        'Descrição': descricao,
        'Prioridade': prioridade,
        'Status': 'Pendente',  # Deve começar como Pendente (Requisito 1)
        'Origem': origem,
        'Data de Criação': data_criacao,
        'Data de Conclusão': None
    }

    # Edição de Variáveis Globais (6) e ID Único (11)
    LISTA_TAREFAS.append(nova_tarefa)
    PROXIMO_ID += 1
    print(f"\n✅ Tarefa '{titulo}' (ID: {nova_tarefa['ID']}) criada e adicionada à lista como 'Pendente'.")

def verificar_urgencia():
    """
    Verifica se há tarefas com prioridade máxima e atualiza a primeira
    encontrada para 'Fazendo'. (Requisito 2)
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função verificar_urgencia")

    # 1. Verificar se alguma tarefa já está "Fazendo" (Regra de Negócio: Somente uma tarefa em execução)
    for tarefa in LISTA_TAREFAS:
        if tarefa['Status'] == 'Fazendo':
            print(f"⚠️ A tarefa (ID: {tarefa['ID']}) '{tarefa['Título']}' já está em execução ('Fazendo').")
            return

    tarefa_selecionada = None

    # 2. Iterar sobre as prioridades em ordem decrescente de urgência
    for prioridade in OPCOES_PRIORIDADE:
        # Tenta encontrar a primeira tarefa 'Pendente' com a prioridade atual
        for tarefa in LISTA_TAREFAS:
            if tarefa['Prioridade'] == prioridade and tarefa['Status'] == 'Pendente':
                tarefa_selecionada = tarefa
                break
        if tarefa_selecionada:
            break # Tarefa de maior prioridade encontrada

    if tarefa_selecionada:
        tarefa_selecionada['Status'] = 'Fazendo'
        print("--------------------------------------------------")
        print(f"🏆 Tarefa selecionada por Urgência/Prioridade:")
        print(f"ID: {tarefa_selecionada['ID']} | Prioridade: {tarefa_selecionada['Prioridade']} | Status: Fazendo")
        print(f"Título: {tarefa_selecionada['Título']}")
        print("--------------------------------------------------")
    else:
        print("Nenhuma tarefa 'Pendente' encontrada na lista.")

def atualizar_prioridade():
    """
    Permite ao usuário alterar a prioridade de uma tarefa existente, validando
    a nova prioridade. (Requisito 3)
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função atualizar_prioridade")
    if not LISTA_TAREFAS:
        print("Não há tarefas na lista para atualizar.")
        return

    tarefa = solicitar_id_valido()
    if tarefa:
        print(f"Prioridade atual: {tarefa['Prioridade']}")
        nova_prioridade = valida_escolha_lista("Nova Prioridade (Urgente, Alta, Média, Baixa): ", OPCOES_PRIORIDADE)

        tarefa['Prioridade'] = nova_prioridade
        print(f"✅ Prioridade da tarefa ID {tarefa['ID']} atualizada para '{nova_prioridade}'.")

def concluir_tarefa():
    """
    Marca uma tarefa como 'Concluída', registra a data de conclusão e informa o
    tempo de execução. (Requisito 4)
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função concluir_tarefa")
    if not LISTA_TAREFAS:
        print("Não há tarefas na lista para concluir.")
        return

    tarefa = solicitar_id_valido()
    if tarefa:
        if tarefa['Status'] == 'Concluída':
            print(f"A tarefa ID {tarefa['ID']} já está 'Concluída'.")
            return
        
        # Só preenche Data de Conclusão se ainda não estiver preenchida
        if tarefa['Data de Conclusão'] is None:
            tarefa['Data de Conclusão'] = datetime.now().isoformat()

        tarefa['Status'] = 'Concluída'
        tempo = calcular_tempo_execucao(tarefa['Data de Criação'], tarefa['Data de Conclusão'])
        print(f"✅ Tarefa ID {tarefa['ID']} marcada como 'Concluída'. Tempo de execução: {tempo}")

def exclusao_logica():
    """
    Atualiza o status de uma tarefa para 'Excluída' (Exclusão Lógica). (Requisito 6)
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função exclusao_logica")
    if not LISTA_TAREFAS:
        print("Não há tarefas na lista para excluir.")
        return

    tarefa = solicitar_id_valido()
    if tarefa:
        tarefa['Status'] = 'Excluída'
        print(f"✅ Tarefa ID {tarefa['ID']} marcada como 'Excluída' (Exclusão Lógica).")

def limpar_tarefas_antigas():
    """
    CORREÇÃO DE ERRO: Adicionada a declaração 'global LISTA_TAREFAS' no topo.
    
    Arquivando Tarefas Antigas: Move tarefas 'Concluídas' há mais de 7 dias
    e tarefas 'Excluídas' para o status 'Arquivado' e as move para o arquivo
    de histórico, limpando a lista ativa. (Requisito 5, 14)
    Parâmetros: nenhum
    Retorno: nenhum
    """
    global LISTA_TAREFAS # Necessário para reatribuir o valor da lista global
    print("Executando a função limpar_tarefas_antigas")
    
    tarefas_para_arquivar = []
    lista_principal_atualizada = []
    hoje = datetime.now()

    for tarefa in LISTA_TAREFAS:
        deve_arquivar = False

        # Verifica se a tarefa foi 'Concluída' há mais de uma semana
        if tarefa['Status'] == 'Concluída' and tarefa['Data de Conclusão']:
            try:
                data_conclusao = datetime.fromisoformat(tarefa['Data de Conclusão'])
                if hoje - data_conclusao > timedelta(weeks=1):
                    tarefa['Status'] = 'Arquivado'
                    deve_arquivar = True
            except ValueError:
                # Mantém na lista se a data estiver inválida
                lista_principal_atualizada.append(tarefa)
                continue 

        # Verifica se a tarefa foi marcada como 'Excluída'
        elif tarefa['Status'] == 'Excluída':
            deve_arquivar = True

        if deve_arquivar:
            tarefas_para_arquivar.append(tarefa)
        else:
            # Mantém todas as outras tarefas (Pendente, Fazendo, Concluída recente, etc.)
            lista_principal_atualizada.append(tarefa)

    # 1. Mover as tarefas marcadas para o arquivo de arquivamento
    arquivar_tarefas(tarefas_para_arquivar)

    # 2. Atualizar a lista global principal (Remover as tarefas movidas/arquivadas)
    LISTA_TAREFAS = lista_principal_atualizada
    print("✅ Limpeza de tarefas antigas/excluídas concluída. Lista principal atualizada.")

def exibir_relatorio(lista, titulo_relatorio, incluir_tempo_execucao=False):
    """
    Função auxiliar para exibir relatórios.
    Parâmetros:
        lista (list): Lista de tarefas a serem exibidas.
        titulo_relatorio (str): Título do relatório.
        incluir_tempo_execucao (bool): Se deve calcular e exibir o tempo.
    Retorno: nenhum
    """
    print("Executando a função exibir_relatorio")
    print("\n" + "="*50)
    print(f"  {titulo_relatorio.upper()}")
    print("="*50)

    if not lista:
        print("  Nenhum item encontrado neste relatório.")
        print("="*50)
        return

    for tarefa in lista:
        tempo_execucao = ""
        # Verifica se deve calcular o tempo de execução (Requisito 7)
        if incluir_tempo_execucao and tarefa['Status'] == 'Concluída' and tarefa['Data de Conclusão']:
            tempo_execucao = calcular_tempo_execucao(tarefa['Data de Criação'], tarefa['Data de Conclusão'])
            tempo_execucao = f" | Tempo Exec: {tempo_execucao}"

        print(f"ID: {tarefa.get('ID', 'N/A')} | Título: {tarefa.get('Título', 'N/A')}")
        print(f"  > Prioridade: {tarefa.get('Prioridade', 'N/A')} | Status: {tarefa.get('Status', 'N/A')} | Origem: {tarefa.get('Origem', 'N/A')}{tempo_execucao}")
        
        # Formatação de datas
        data_criacao = tarefa.get('Data de Criação', 'N/A').split('T')[0]
        data_conclusao = tarefa.get('Data de Conclusão')
        data_conclusao_formatada = data_conclusao.split('T')[0] if data_conclusao else 'N/A'
        
        print(f"  > Criação: {data_criacao} | Conclusão: {data_conclusao_formatada}")
        if tarefa.get('Descrição'):
            print(f"  > Descrição: {tarefa['Descrição']}")
        print("-" * 50)

def relatorio_tarefas_ativas():
    """
    Exibe todas as tarefas ativas (não 'Arquivado' ou 'Excluída') e calcula 
    o tempo de execução para as concluídas. (Requisito 7)
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função relatorio_tarefas_ativas")
    # Filtra tarefas que não estão 'Arquivado' ou 'Excluída'
    tarefas_ativas = [t for t in LISTA_TAREFAS if t['Status'] not in ['Arquivado', 'Excluída']]
    exibir_relatorio(tarefas_ativas, "Relatório de Tarefas Ativas", incluir_tempo_execucao=True)

def relatorio_tarefas_arquivadas():
    """
    Exibe a lista de tarefas arquivadas (somente status 'Arquivado') lendo do 
    arquivo tarefas_arquivadas.json. (Requisito 8)
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função relatorio_tarefas_arquivadas")
    tarefas_arquivadas_list = []
    try:
        with open(ARQUIVO_ARQUIVADAS, 'r') as f:
            historico = json.load(f)
            # Excluídas não devem ser listadas neste relatório (Requisito 8)
            tarefas_arquivadas_list = [t for t in historico if t['Status'] == 'Arquivado']
    except (FileNotFoundError, json.JSONDecodeError):
        pass # A função exibir_relatorio lidará com a lista vazia
        
    exibir_relatorio(tarefas_arquivadas_list, "Relatório de Tarefas Arquivadas", incluir_tempo_execucao=True)

# ==============================================================================
# CORPO PRINCIPAL DO PROGRAMA (Requisitos 1, 2)
# ==============================================================================

def sair_programa():
    """
    Opção Sair: Salva o estado atual da LISTA_TAREFAS e encerra o programa. 
    (Requisito 13)
    Parâmetros: nenhum
    Retorno: N/A (encerra o programa)
    """
    print("Executando a função sair_programa")
    print("\nSalvando tarefas antes de encerrar...")
    salvar_tarefas()
    print("Dados salvos com sucesso.")
    print("Encerrando o programa. Até logo!")
    exit()

def menu_principal():
    """
    Menu Principal (1): Centraliza todas as opções do sistema e gerencia o fluxo
    principal de execução.
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando o menu_principal")
    OPCOES_MENU = {
        1: ("Criar Nova Tarefa", criar_tarefa),
        2: ("Verificar e Iniciar Próxima Tarefa (Urgência)", verificar_urgencia),
        3: ("Atualizar Prioridade de Tarefa", atualizar_prioridade),
        4: ("Concluir Tarefa", concluir_tarefa),
        5: ("Exclusão Lógica de Tarefa", exclusao_logica),
        6: ("Executar Limpeza e Arquivamento Automático", limpar_tarefas_antigas),
        7: ("Relatório de Tarefas Ativas", relatorio_tarefas_ativas),
        8: ("Relatório de Tarefas Arquivadas", relatorio_tarefas_arquivadas),
        9: ("Sair do Programa", sair_programa)
    }

    # Carrega os dados persistidos no início da execução (Requisito 13)
    carregar_dados_iniciais()

    while True:
        print("\n" + "="*40)
        print("  SISTEMA DE GERENCIAMENTO DE TAREFAS")
        print("="*40)
        for num, (texto, _) in OPCOES_MENU.items():
            print(f"| {num}. {texto}")
        print("="*40)

        # Validação da opção e Tratamento de Exceção (Requisitos 1, 9)
        opcao_escolhida = valida_opcao_menu("Escolha uma opção: ", OPCOES_MENU.keys())

        # Execução da funcionalidade (Requisito 2)
        func = OPCOES_MENU[opcao_escolhida][1]
        func()

if __name__ == "__main__":
    menu_principal()