"""
src/erros.py
Classificação de erros do SmartCheck.

Cada erro retorna um dict com:
  - mensagem   : texto exibido na interface para o usuário
  - detalhe    : texto técnico para o terminal / log
  - tipo       : 'usuario' | 'sistema'
"""


#==============================================
#  ERROS DE USUÁRIO
#  Problema que o próprio usuário pode resolver
#==============================================
_ERROS_USUARIO = [
    {
        "identificador": "Planilha vazia",
        "mensagem": "O arquivo de pendências está vazio. Verifique o conteúdo e tente novamente.",
        "tipo": "usuario",
    },
    {
        "identificador": "Arquivo fora do padrão esperado",
        "mensagem": "O arquivo de pendências está fora do formato esperado. Verifique o conteúdo e tente novamente.",
        "tipo": "usuario",
    },
    {
    "identificador": "nenhuma aba contém as colunas obrigatórias",
    "mensagem": "O arquivo selecionado não contém as abas ou colunas esperadas. Verifique se é o arquivo correto.",
    "tipo": "usuario",
    },
    {
        "identificador": "Base SQL vazia",
        "mensagem": "A base interna retornou sem dados. Verifique a conexão com o banco e tente novamente.",
        "tipo": "usuario",
    },
    {
        "identificador": "PermissionError",
        "mensagem": "Um arquivo está aberto no Excel. Feche-o e execute novamente.",
        "tipo": "usuario",
    },
    {
        "identificador": "O arquivo está aberto",
        "mensagem": "Um arquivo está aberto no Excel. Feche-o e execute novamente.",
        "tipo": "usuario",
    },
    {
        "identificador": "FileNotFoundError",
        "mensagem": "Arquivo não encontrado. Verifique se os arquivos selecionados ainda existem.",
        "tipo": "usuario",
    },
    {
        "identificador": "No such file",
        "mensagem": "Arquivo não encontrado. Verifique se os arquivos selecionados ainda existem.",
        "tipo": "usuario",
    },
    {
        "identificador": "not a valid Excel",
        "mensagem": "O arquivo selecionado não é um Excel válido. Verifique o formato e tente novamente.",
        "tipo": "usuario",
    },
    {
        "identificador": "Worksheet",
        "mensagem": "Aba não encontrada no arquivo Excel. Verifique se o arquivo está no formato correto.",
        "tipo": "usuario",
    },
    {
        "identificador": "SMTPException",
        "mensagem": "Falha no envio do e-mail. Verifique se o Outlook está aberto e configurado.",
        "tipo": "usuario",
    },
    {
        "identificador": "SMTP",
        "mensagem": "Falha no envio do e-mail. Verifique se o Outlook está aberto e configurado.",
        "tipo": "usuario",
    },
    {
        "identificador": "COM",
        "mensagem": "Falha na integração com o Outlook. Verifique se o Outlook está aberto.",
        "tipo": "usuario",
    },
]


#==============================================
#  ERROS DE SISTEMA
#  Problema no algoritmo — usuário não resolve
#==============================================
_ERROS_SISTEMA = [
    {
        "identificador": "KeyError",
        "mensagem": "Coluna esperada não encontrada no processamento. Contate o suporte.",
        "tipo": "sistema",
    },
    {
        "identificador": "08001",
        "mensagem": "Falha na conexão com a base interna. Se estiver em casa, verifique sua VPN, caso esteja na rede da empresa, contate o suporte.",
        "tipo": "sistema",
    },
       {
        "identificador": "SQL Server inexistente ou acesso negado.",
        "mensagem": "Falha na conexão com a base interna. Se estiver em casa, verifique sua VPN, caso esteja na rede da empresa, contate o suporte.",
        "tipo": "sistema",
    },
    {
        "identificador": "TypeError",
        "mensagem": "Erro de tipo em operação interna. Contate o suporte.",
        "tipo": "sistema",
    },
    {
        "identificador": "AttributeError",
        "mensagem": "Atributo inesperado no processamento. Contate o suporte.",
        "tipo": "sistema",
    },
    {
        "identificador": "ValueError",
        "mensagem": "Valor inesperado no processamento. Contate o suporte.",
        "tipo": "sistema",
    },
    {
        "identificador": "not supported between instances",
        "mensagem": "Erro de comparação entre tipos incompatíveis. Contate o suporte.",
        "tipo": "sistema",
    },
    {
        "identificador": "NoneType",
        "mensagem": "Resultado vazio em etapa crítica do processamento. Contate o suporte.",
        "tipo": "sistema",
    },
    {
        "identificador": "Processamento encerrado sem resultado",
        "mensagem": "O processamento foi encerrado sem retornar resultado. Contate o suporte.",
        "tipo": "sistema",
    },
    {
        "identificador": "operands could not be broadcast",
        "mensagem": "Erro de dimensão em operação matricial. Contate o suporte.",
        "tipo": "sistema",
    },
    {
        "identificador": "merge",
        "mensagem": "Erro ao cruzar bases de dados. Contate o suporte.",
        "tipo": "sistema",
    },
]


#==============================================
#  FUNÇÃO PRINCIPAL
#==============================================

def classificar_erro(exc: Exception) -> dict:
    """
    Recebe uma exceção e retorna um dict com:
      mensagem  : texto amigável para exibir ao usuário na interface
      detalhe   : representação técnica do erro para o terminal/log
      tipo      : 'usuario' | 'sistema'

    Exemplo de uso no main.py:
        except Exception as e:
            info = classificar_erro(e)
            print(f"[{info['tipo'].upper()}] {info['detalhe']}")
            raise SmartCheckError(info['mensagem'], info['tipo']) from e
    """
    tipo_exc   = type(exc).__name__
    msg_exc    = str(exc)
    busca      = f"{tipo_exc} {msg_exc}"

    # Verifica erros de usuário primeiro (prioridade)
    for regra in _ERROS_USUARIO:
        if regra["identificador"] in busca:
            return {
                "mensagem": regra["mensagem"],
                "detalhe":  f"[{tipo_exc}] {msg_exc}",
                "tipo":     "usuario",
            }

    # Verifica erros de sistema
    for regra in _ERROS_SISTEMA:
        if regra["identificador"] in busca:
            return {
                "mensagem": regra["mensagem"],
                "detalhe":  f"[{tipo_exc}] {msg_exc}",
                "tipo":     "sistema",
            }

    # Não mapeado — trata como sistema
    return {
        "mensagem": "Erro interno não identificado. Contate o suporte com o detalhe abaixo.",
        "detalhe":  f"[{tipo_exc}] {msg_exc}",
        "tipo":     "sistema",
    }


class SmartCheckError(Exception):
    """
    Exceção customizada que carrega a mensagem amigável e o tipo do erro.
    Lançada pelo main.py após classificar_erro(), capturada pelo tela_processamento.py.
    """
    def __init__(self, mensagem_usuario: str, tipo: str = "sistema", detalhe: str = ""):
        super().__init__(mensagem_usuario)
        self.mensagem_usuario = mensagem_usuario
        self.tipo             = tipo
        self.detalhe          = detalhe