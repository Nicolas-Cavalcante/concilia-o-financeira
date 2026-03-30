# projeto-conciliacao_ebta
Melhorias no processo de conciliacao.

# SmartCheck - Documentação do Projeto

# 1. Visão Geral

O SmartCheck é uma solução de automação desenvolvida em Python para otimizar o processo de conciliação EBTA. O sistema cruza dados de planilhas de pendências com uma base SQL, realiza o matching das informações e automatiza o envio de notificações via Outlook.

# 2. Arquitetura do Sistema

O projeto segue uma arquitetura modular para facilitar manutenção, escalabilidade e organização:

•	inputs/base_clientes: Base de clientes utilizada no processamento.

•	inputs/casos_pendencias: Arquivo de pendências do Bradesco.

•	inputs/de_para: Mapeamento de campos por cliente.

•	outputs/arquivos de saída.

•	src/extract: Ingestão de dados (SQL, Excel, bases auxiliares).

•	src/transform: Tratamento e criação de chaves de matching.

•	src/matching: Motor de regras para cruzamento de dados.

•	src/notify: Lógica de criticidade e envio de e-mails.

•	src/interface: Interface gráfica em Tkinter.

Em mapeamento de campos por cliente temos um cuidado maior de verificação, a mascara de colunas criada no arquivo vai corresponder onde cada informação está no banco. Temos clientes por exemplo que a informação do “centro de custo” fica na coluna de “infpolitica” no banco, para esses casos precisamos identificar qual a coluna correspondente para cada cliente.

# 3. Fluxo de Dados

O processamento segue as seguintes etapas:

•	Entrada de arquivos via interface (pendências e base de clientes).

•	Consulta SQL com dados dos últimos 2 meses.

•	Geração de múltiplas chaves de matching.

•	Execução do motor de conciliação.

•	Geração de outputs (conciliados e pendentes).

•	Envio automático de notificações por e-mail.

Chaves de Matching:

•	K1: Autorização

•	K2: Autorização + Data + Valor

•	K3: Autorização + Cartão + Data + Valor

•	K4: Cartão + Data + Valor

•	K5: Cartão + Data + Valor + Localizador

•	K6: Cartão + Valor + Localizador

# 4. Regras de Negócio

Casos não conciliados são enviados para ajuste operacional via e-mail. As correções devem ser realizadas no sistema de origem (benner), assim no próximo processamento este caso não subirá como pendência.

Caso os ajustes não sejam feitos dentro da data de corte do cliente, a fatura será fechada e os casos subirão em branco.

Como está desenhado abaixo, casos com a data de corte < 0 serão encaminhados à diretoria, para que todos estejam a par do processo pendente.

# Criticidade (Aging)

Aging (Dias)	Status	Prioridade	Ação

< 0	Crítico	Alta	Envio + Diretoria

= 0	Urgente	Alta	Envio imediato

1 a 5	Alta	Média	Envio operação

6 a 10	Média	Baixa	Acompanhamento

> 10	Baixa	Baixa	Rotina normal

# 5. Dependências Principais

•	Pandas & Openpyxl: Manipulação de dados.

•	SQLAlchemy & pyodbc: Conexão com SQL Server.

•	Pywin32: Integração com Outlook.

•	Tkinter: Interface gráfica.

Variáveis de Ambiente (.env)

•	DB_Server;

•	DB_Database;

•	DB_User;

•	DB_Password;

•	Email_User;

•	Email_Diretoria.

# 6. Utilização

•	Executar interface;

•	Selecionar planilha de pendências (extraída do site/Bradesco);

•	Selecione a Base de Clientes atualizada;

•	Confirmar se deseja realizar o envio de e-mails ao final do processamento;

•	Validar outputs gerados para conferir os resultados processados.
