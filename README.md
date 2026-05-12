



SmartCheck
Documentação Técnica
Conciliação EBTA · Versão 1.0
12 de maio de 2026


 
1. Visão Geral
O SmartCheck é uma solução de automação desenvolvida em Python para otimizar o processo de conciliação EBTA. O sistema cruza dados de planilhas de pendências com uma base SQL Server, realiza o matching das informações por meio de chaves compostas e automatiza o envio de notificações via Microsoft Outlook.

O resultado da execução é a classificação de cada registro em um dos três status possíveis — Ok, Não Localizado ou Ausência de Dados — e a geração de arquivos formatados para envio ao Bradesco e para acompanhamento interno.

2. Arquitetura do Sistema
Estrutura de Pastas

inputs/casos_pendencias/	Arquivo de pendências do Bradesco (pendencias*.xlsx)
inputs/base_emails/	Base de e-mails dos responsáveis (Base_emails.xlsx)
inputs/	Arquivo De-Para (De_Para_*.xlsx)
outputs/Corretos/	Arquivo de conciliados gerado pelo sistema
outputs/Incorretos/	Arquivo de pendências não conciliadas
logs/	Histórico de execuções e assertividade por chave
.env	Credenciais de banco e e-mail (não versionado)
SmartCheck.exe	Executável principal
build.bat	Script de reempacotamento do executável
SmartCheck.spec	Configuração do PyInstaller

Camadas da Aplicação

src/extract	Leitura de dados — Excel (pendências, e-mails, De-Para) e SQL Server
src/transform	Tratamento e padronização — normalização, criação de chaves e colunas auxiliares
src/matching	Motor de conciliação — matching sequencial por chaves compostas
src/export	Geração de arquivos de saída formatados via OpenPyXL
src/notify	Montagem do corpo dos e-mails e envio via Outlook
src/log	Registro de histórico de execução e assertividade por chave
src/interface	Interface gráfica (CustomTkinter) — seleção de arquivos, progresso e feedback
src/config	Paths e controle de ambiente (.py vs .exe)
src/main	Orquestração do fluxo completo

3. Requisitos de Ambiente

Componente	Requisito	Observação
Sistema Operacional	Windows 10 (64-bit) ou superior	
Memória RAM	16 GB mínimo	
Espaço em disco	500 MB livres	Para outputs e logs
Driver SQL	SQL Server (nativo Windows)	Não requer instalação adicional
Microsoft Outlook	Instalado e configurado	Usado para envio de e-mails
Rede / VPN	Acesso ao SQL Server	Porta e credenciais configuradas
Permissão de escrita	Nas subpastas outputs/ e logs/	Sem isso exportação e log falham silenciosamente
Python 3.10+	Apenas para execução via CLI	O .exe não requer Python instalado

4. Configuração do Ambiente (.env)
O arquivo .env fica na raiz do projeto e não é versionado no repositório Git. Deve ser criado ou atualizado manualmente em cada ambiente. Não está embutido no executável — alterações no .env não requerem rebuild.

Variável	Descrição
DB_Server	Endereço do servidor SQL Server
DB_Database	Nome do banco de dados
DB_User	Usuário de acesso ao banco (autenticação SQL Server)
DB_Password	Senha de acesso ao banco
Email_User	Conta de e-mail remetente (Outlook local configurado)
Email_Diretoria	Destinatários para alertas críticos - múltiplos separados por ;

Atenção: qualquer alteração de senha, servidor ou conta de e-mail exige atualização manual deste arquivo antes da próxima execução.

5. Estrutura dos Arquivos de Entrada
Pendências Bradesco - inputs/casos_pendencias/pendencias*.xlsx
Colunas obrigatórias validadas pelo sistema na abertura do arquivo:

Coluna	Descrição
Autorização	Código de autorização da transação
Valor Total	Valor da transação
Nome da Empresa	Identificador da célula — chave de vínculo com o De-Para
Cartão	Número do cartão

Base de E-mails - inputs/base_emails/Base_emails.xlsx
Coluna obrigatória validada pelo sistema:

Coluna	Descrição
E-mail Célula	Endereço de e-mail do responsável pela célula

De-Para - inputs/De_Para_*.xlsx
Todas as colunas abaixo devem estar presentes. As colunas Comp ID e Campo Produtividade existem na planilha mas não são utilizadas pelo sistema.

Coluna	Uso pelo sistema	Descrição
Cliente	Sim	Nome do cliente — deve ser idêntico ao valor em Nome da Empresa nas pendências
Campo Arquivo do cliente	Sim	Nome exato da coluna no arquivo de pendências do cliente
Nome do Campo	Sim	Nome exato do campo correspondente no DW
Campo Benner	Sim	Nome do campo no sistema Benner
Comp ID	Não	Identificador interno — ignorado pelo sistema
Campo Produtividade	Não	Referência de produtividade — ignorado pelo sistema

Atenção: diferenças de espaço, capitalização ou acento entre a coluna Cliente e o valor em Nome da Empresa fazem o match silenciosamente falhar para aquele cliente.

O sistema suporta uma entrada DEFAULT no De-Para — uma linha com Cliente = DEFAULT cujas regras são aplicadas como base para todos os clientes antes das regras individuais. Esta funcionalidade está implementada, mas não está em uso atualmente.

 
6. Conexão SQL

Driver	SQL Server (nativo Windows — não requer instalação adicional)
Autenticação	SQL Server (usuário e senha via variáveis do .env)
Janela de dados	Últimos 3 meses a partir da data de execução
Acesso	Somente leitura — sem permissão para criar objetos no banco
Arquivo	src/extract/database.py

Estrutura da Consulta
A extração é feita via SELECT com subquery diretamente no código. Não há views ou objetos criados no banco. As tabelas e dimensões envolvidas são:

Objeto	Papel
fato_aereo	Tabela fato central
dim_cliente	Dimensão cliente
dim_passageiro	Dimensão passageiro
dim_contato_solicitante	Dimensão solicitante
dim_rota	Dimensão rota / trecho
dim_emissor	Dimensão emissor
dim_tipo_pagamento	Dimensão tipo de pagamento
dim_classe_venda	Dimensão classe de venda

Filtro fixo: id_divisao IN (2000, 7000). Para incluir uma nova divisão, é necessário alterar este filtro em database.py e reempacotar o executável.

As chaves de matching são geradas via CONCAT no SQL (database.py) e replicadas em Python (tratamento.py). Qualquer alteração em uma chave deve ser feita nos dois arquivos - caso contrário o matching quebra sem gerar erro explícito.

7. Fluxo de Processamento
1.	Seleção dos arquivos de entrada pela interface
2.	Validação das colunas obrigatórias de cada arquivo
3.	Carregamento da base de e-mails
4.	Consulta à base SQL (janela de 3 meses)
5.	Tratamento e padronização dos dados - normalização, criação de chaves e colunas auxiliares
6.	Execução do matching sequencial por chaves compostas
7.	Classificação dos registros por status
8.	Geração dos arquivos de saída (Conciliados e Pendências)
9.	Registro nos logs de execução
10.	Envio de e-mails para operação e, se aplicável, para diretoria

8. Motor de Conciliação
Chaves de Matching
O matching é executado sequencialmente. Cada registro tenta a próxima chave apenas se não foi conciliado pela anterior. O primeiro match válido vence.

Chave	Composição	Observação
K1	Autorização + Data + Valor	Chave primária - maior especificidade
K2	nr_aut + Data + Valor	Variação do número de autorização
K3	Loc Cia + Data + Valor	Localizador da cia aérea + data + valor
K4	Cartão + Data + Valor + Loc Cia	Últimos 3 dígitos do cartão
K5	Cartão + Valor + Loc Cia	Chave mais ampla - sem data

Regras de Matching
•	Apenas chaves únicas são utilizadas - registros com chave duplicada em qualquer uma das bases são descartados
•	O primeiro match válido encerra a tentativa para aquele registro
•	Toda tentativa é registrada no log de chaves com o resultado obtido

Regras Dinâmicas (De-Para)
O sistema aplica as regras de preenchimento em três camadas, na seguinte ordem:
11.	Regras padrão - definidas no código, aplicadas a todos os clientes
12.	Regras DEFAULT - se existir uma entrada DEFAULT no De-Para, sobrescreve as padrão (não utilizado atualmente)
13.	Regras por cliente - sobrescreve as anteriores com as regras específicas do cliente

9. Classificação de Status

Status	Significado
Ok	Registro conciliado com todas as colunas preenchidas
Não Localizado	Nenhuma das 5 chaves encontrou correspondência na base SQL
Colunas com ausência de dados	Match encontrado, mas um ou mais campos retornaram vazios na base SQL - sinalizados com **********

10. Outputs Gerados

Arquivo	Localização	Conteúdo
Conciliados.xlsx	outputs/Corretos/	Registros com status Ok, prontos para envio ao Bradesco
Pendências_EBTA.xlsx	outputs/Incorretos/	Registros Não Localizado e Ausência de Dados
historico_execucao_detalhado.xlsx	logs/	Totais por empresa por execução
historico_execucao.xlsx	logs/	Assertividade por chave de matching por execução

Todos os arquivos Excel gerados possuem layout formatado via OpenPyXL: filtros habilitados, freeze panes e ajuste automático de colunas.

11. Envio de E-mails

Destinatário	Critério de envio	Conteúdo
Operação	Sempre que o envio for habilitado pelo usuário na interface	Tabela com top 10 empresas com mais pendências + arquivo Pendências_email.xlsx em anexo
Diretoria	Apenas quando houver registros com Dias Restantes ≤ 1	Alerta com quantidade de casos críticos e menor prazo identificado, sem anexo

Os destinatários da operação são definidos dinamicamente pela função definir_destinatarios com base nos dias restantes e na base de e-mails. Os destinatários da diretoria são fixos, configurados na variável Email_Diretoria do .env.

 
12. Logs e Auditoria
Log Detalhado - historico_execucao_detalhado.xlsx
•	Data de execução
•	Célula / empresa
•	Quantidade de registros corretos, incorretos e com ausência de dados
•	Status do envio de e-mail
•	usuario

Log de Chaves - historico_execucao.xlsx
•	Chave utilizada (K1 a K5)
•	Resultado por chave (encontrado, não encontrado, incompleto)
•	Quantidade por resultado
•	Data de execução

Os arquivos de log crescem a cada execução sem rotina automática de limpeza. Recomenda-se arquivar ou excluir periodicamente. O sistema recria os arquivos automaticamente se não existirem. (Em caso de limitação de linhas no excel, será necessário substituir o arquivo ou o código irá quebrar)

13. Tratamento de Erros

Erro	Causa	Ação recomendada
Arquivo inválido	Colunas obrigatórias ausentes no arquivo selecionado	Verificar se o arquivo correto foi selecionado e se o cabeçalho está íntegro
Erro de conexão SQL	Credenciais incorretas, servidor inacessível ou VPN desconectada	Verificar .env e conectividade de rede. Em caso de troca de senha, atualizar DB_Password
Arquivo aberto	O arquivo de saída está aberto em outro programa no momento da exportação	Fechar o arquivo Excel antes de executar
Planilha vazia	Arquivo de pendências não contém registros	Verificar se o arquivo correto foi exportado do Bradesco
Erro de execução	Falha inesperada em qualquer etapa do processamento	Verificar o log no terminal (execução CLI) ou acionar o responsável técnico

14. Limitações
Limitações Atuais
•	Matching exato — sem tolerância a variação de valor ou texto; qualquer divergência resulta em Não Localizado
•	Duplicados ignorados — chaves duplicadas em qualquer uma das bases são descartadas silenciosamente, sem aviso ao usuário
•	Transações consolidadas não tratadas — quando o Bradesco agrupa múltiplas transações em uma única linha (ex: R$ 10.000) e a base interna registra as parcelas separadamente (ex: 2x R$ 5.000), o matching falha e o registro fica como Não Localizado
•	Sem controle de acesso — qualquer usuário com acesso à máquina pode executar o sistema; não há autenticação, perfis ou log de quem executou
•	Dependência de ambiente local — o executável requer Microsoft Outlook instalado, acesso ao SQL Server e estrutura de pastas correta; não há validação prévia do ambiente
•	Logs em Excel — crescem indefinidamente sem rotina automática de limpeza ou arquivamento
•	Janela de consulta fixa — registros com data de movimento fora dos últimos 3 meses não são retornados pela query e resultam em Não Localizado sem aviso explícito

Evoluções Planejadas (V2)
•	Regra de conciliação para transações consolidadas
•	Sistema de login com usuário e senha
•	Gestão de usuários e perfis de acesso

15. Guia de Manutenção
1. Atualizar credenciais do banco de dados
Abrir o arquivo .env na raiz do projeto e atualizar o valor da variável correspondente. Não requer rebuild do executável.

O .env não é versionado e não está embutido no .exe - pode ser editado diretamente a qualquer momento.

2. Adicionar ou ajustar regra de cliente no De-Para
Abrir o arquivo De_Para_*.xlsx na pasta inputs/ e inserir ou editar a linha do cliente. Atenção aos três campos críticos:
•	Cliente - deve ser exatamente igual ao valor em Nome da Empresa no arquivo de pendências
•	Campo Arquivo do cliente - deve ser exatamente igual ao nome da coluna no arquivo de pendências do cliente
•	Nome do Campo - deve ser exatamente igual ao nome do campo correspondente no DW
Não requer rebuild do executável.

3. Ajustar a consulta SQL
Abrir src/extract/database.py e localizar a query. Pontos de alteração mais comuns:
•	Nova divisão: alterar o filtro id_divisao IN (2000, 7000) adicionando o novo ID
•	Campo renomeado no banco: atualizar o alias correspondente na query
•	Janela de tempo: alterar o parâmetro meses_atras = 3

Após qualquer alteração em database.py é obrigatório reempacotar o executável conforme o item 5.
Se a alteração envolver uma chave de matching, ela deve ser replicada também em src/transform/tratamento.py.

4. Adicionar novo asset à interface
Declarar o novo arquivo na seção datas do SmartCheck.spec antes do build:
datas=[('src/fundo_fly.png', '.'), ('src/logo_fly_branca.png', '.'), ('src/novo_asset.png', '.')]
Em seguida executar o build conforme o item 5.

5. Reempacotar o executável
Com o ambiente virtual ativo, executar o arquivo build.bat na raiz do projeto:
build.bat
O script ativa o venv, executa o PyInstaller com o SmartCheck.spec e gera o SmartCheck.exe na raiz do projeto. Não é necessário excluir o executável anterior - o build sobrescreve automaticamente.

6. Limpeza de logs
Os arquivos de log em logs/ crescem a cada execução. Recomenda-se arquivar ou excluir periodicamente:
•	logs/historico_execucao_detalhado.xlsx
•	logs/historico_execucao.xlsx
Não há impacto operacional na exclusão - o sistema recria os arquivos automaticamente na próxima execução.

16. Modos de Execução

Modo	Como executar	Observação
Interface (.exe)	Abrir SmartCheck.exe	Modo padrão — não requer Python instalado
Interface (Python)	python -m src.interface	Requer Python 3.10+ e dependências instaladas
CLI	python -m src.main --input1 arquivo1 --input2 arquivo2	Sem interface gráfica — útil para automação e testes

SmartCheck · Documentação Técnica v1.0 · Uso interno e confidencial
