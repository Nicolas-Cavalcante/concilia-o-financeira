SmartCheck - Documentação do Projeto

1. Visão Geral
O SmartCheck é uma solução de automação desenvolvida em Python para otimizar o processo de conciliação EBTA. O sistema cruza dados de planilhas de pendências com uma base SQL, realiza o matching das informações e automatiza o envio de notificações via Outlook.

3. Arquitetura do Sistema

📁 Estrutura
  •	inputs/ → arquivos de entrada (pendências, base de emails, depara) 
  •	outputs/ 
    o	Corretos/ → conciliados 
    o	Incorretos/ → pendências não tratadas 
  •	logs/ → histórico de execução
  
📦 Camadas
  •	src/extract → leitura de dados (Excel + SQL) 
  •	src/transform → tratamento e padronização 
  •	src/matching → motor de conciliação 
  •	src/export → geração de arquivos formatados 
  •	src/notify → envio de e-mails 
  •	src/log → rastreabilidade e auditoria 
  •	src/interface → UI (CustomTkinter) 
  •	src/config → paths e controle de ambiente
  •	src/main → orquestração

4. Controle de Ambiente
  •	BASE_DIR → recursos internos 
  •	EXEC_DIR → execução (outputs/logs) 
Permite execução como .py ou .exe.

5. Estrutura de Entrada
Arquivos esperados:
inputs/
    pendencias*.xlsx
    Base_emails.xlsx
    De_Para_*.xlsx

6. Requisitos de Entrada
📄 Planilha de Pendências
Deve conter obrigatoriamente o padrão do bradesco em estrutura de colunas. Arquivos fora desse padrão gerarão erro de validação.

7. Fluxo de Processamento
  1.	Seleção de arquivos 
  2.	Carregamento das bases 
  3.	Tratamento dos dados 
  4.	Geração de chaves 
  5.	Execução do matching 
  6.	Classificação 
  7.	Geração de outputs 
  8.	Registro de logs 
  9.	Envio de e-mails
  10. Motor de Conciliação
  •	Matching sequencial:
  •	K1 → Aut + Data + Valor 
  •	K2 → nr_aut + Data + Valor 
  •	K3 → Loc + Data + Valor 
  •	K4 → Cartão + Data + Valor + Loc 
  •	K5 → Cartão + Valor + Loc 

10.	Regras:
  •	Apenas chaves únicas 
  •	Duplicadas são descartadas 
  •	Primeiro match válido vence 
  •	Log por tentativa

8. Regras Dinâmicas (De-Para)
   
Permite:
  •	regras padrão 
  •	regras por cliente 
  •	override automático 

10. Classificação de Status
  •	Ok 
  •	Não Localizado 
  •	Colunas com ausência de dados

11. Logs e Auditoria
    
Log Geral
  •	quantidade por empresa 
  •	status 
  •	data execução 
Log de Chaves
  •	chave utilizada 
  •	resultado 
  •	data execução
  
13. Outputs
  •	Conciliados.xlsx 
  •	Pendências_EBTA.xlsx 
Características:
  •	layout formatado (OpenPyXL) 
  •	filtros 
  •	freeze panes 
  •	ajuste automático

15. Interface
  •	seleção de arquivos 
  •	barra de progresso 
  •	status em tempo real 
  •	execução em thread 
  •	feedback visual

17. Envio de E-mails
  •	envio para operação 
  •	envio para diretoria (casos críticos) 
Critério:
  •	baseado em dias restantes

19. Regras Implícitas
  •	'**********' → ausência válida 
  •	datas → string 
  •	cartão → últimos 3 dígitos 
  •	valores → 2 casas decimais

21. Tratamento de Erros
  •	arquivo aberto 
  •	estrutura inválida 
  •	erro SQL 
  •	erro de execução

23. Limitações
  •	matching exato (sem fuzzy) 
  •	duplicados ignorados 
  •	dependência de estrutura

25. Modos de Execução
Interface
.exe
CLI
python -m src.interface
caminho variável: python -m src.main --input1 arquivo1 --input2 arquivo2
