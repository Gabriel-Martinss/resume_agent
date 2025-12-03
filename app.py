"""
Chatbot de Conversas sobre Carreira

Uma aplicação de chatbot baseada em Gradio que usa o GPT-4o-mini da OpenAI para simular
conversas como uma pessoa específica (Gabriel Martins). O chatbot pode responder
perguntas sobre carreira, histórico, habilidades e experiência usando contexto de
um PDF de perfil do LinkedIn e um arquivo de texto com resumo.

Recursos:
- Interface de chat interativa usando Gradio
- Capacidades de chamada de ferramentas para registrar interações do usuário
- Integração com API Pushover para notificações
- Conversas multi-turno com loop de execução de ferramentas
"""

from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)


def push(text):
    """
    Envia uma notificação push via API Pushover.
    
    Args:
        text (str): O texto da mensagem a ser enviado na notificação.
    
    Nota:
        Requer as variáveis de ambiente PUSHOVER_TOKEN e PUSHOVER_USER.
    """
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    """
    Registra os detalhes de contato do usuário e envia uma notificação.
    
    Esta função é chamada como uma ferramenta pelo LLM quando um usuário fornece
    seu endereço de email ou informações de contato.
    
    Args:
        email (str): O endereço de email do usuário (obrigatório).
        name (str, opcional): O nome do usuário. Padrão: "Name not provided".
        notes (str, opcional): Contexto adicional sobre a conversa.
            Padrão: "not provided".
    
    Returns:
        dict: Um dicionário com confirmação de status: {"recorded": "ok"}
    """
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question):
    """
    Registra uma pergunta que o chatbot não conseguiu responder.
    
    Esta função é chamada como uma ferramenta pelo LLM quando encontra
    uma pergunta que não consegue responder com base no contexto fornecido.
    
    Args:
        question (str): A pergunta que não pôde ser respondida.
    
    Returns:
        dict: Um dicionário com confirmação de status: {"recorded": "ok"}
    """
    push(f"Recording {question}")
    return {"recorded": "ok"}

# Definições de ferramentas de chamada de função da OpenAI
# Estas definem as ferramentas disponíveis para o LLM para chamada de funções

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use esta ferramenta para registrar que um usuário está interessado em entrar em contato e forneceu um endereço de email",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "O endereço de email deste usuário"
            },
            "name": {
                "type": "string",
                "description": "O nome do usuário, se ele forneceu"
            },
            "notes": {
                "type": "string",
                "description": "Qualquer informação adicional sobre a conversa que vale a pena registrar para dar contexto"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Sempre use esta ferramenta para registrar qualquer pergunta que não pôde ser respondida, pois você não sabia a resposta",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "A pergunta que não pôde ser respondida"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

# Lista de ferramentas disponíveis para o LLM
tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]


class Me:
    """
    Classe principal do chatbot que simula conversas como uma pessoa específica.
    
    Esta classe carrega informações pessoais de um PDF do LinkedIn e arquivo de resumo,
    depois usa a API da OpenAI para gerar respostas no personagem. Suporta
    chamada de ferramentas para registrar interações do usuário e perguntas não respondidas.
    
    Attributes:
        openai (OpenAI): Instância do cliente OpenAI.
        name (str): O nome da pessoa sendo simulada.
        linkedin (str): Texto extraído do PDF do perfil do LinkedIn.
        resume (str): Texto extraído do PDF do currículo da pessoa.
        summary (str): Texto de resumo carregado de me/summary.txt.
    """

    def __init__(self):
        """
        Inicializa a instância do chatbot Me.
        
        Carrega o cliente OpenAI, lê o PDF do perfil do LinkedIn e carrega
        o arquivo de texto de resumo. Estes são usados como contexto para o chatbot.
        
        Arquivos esperados:
            - me/linkedin.pdf: Arquivo PDF contendo informações do perfil do LinkedIn
            - me/resume.pdf: Arquivo PDF contendo o currículo da pessoa
            - me/summary.txt: Arquivo de texto com um resumo do histórico da pessoa
        """
        self.openai = OpenAI()
        self.name = "Gabriel Martins"
        
        reader_linkedin = PdfReader("me/linkedin.pdf")
        self.linkedin = ""
        for page in reader_linkedin.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text

        reader_resume = PdfReader("me/resume.pdf")
        self.resume = ""
        for page in reader_resume.pages:
            text = page.extract_text()
            if text:
                self.resume += text
        
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()

    def handle_tool_call(self, tool_calls):
        """
        Executa chamadas de ferramentas solicitadas pelo LLM.
        
        Este método processa chamadas de ferramentas da resposta da API OpenAI,
        executa as funções Python correspondentes e formata os
        resultados para inclusão no histórico da conversa.
        
        Args:
            tool_calls (list): Lista de objetos de chamada de ferramenta da resposta da API.
                Cada chamada de ferramenta contém nome da função e argumentos.
        
        Returns:
            list: Lista de dicionários de mensagem com papel "tool" contendo
                os resultados da execução, formatados para a API OpenAI.
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            
            # Verifica se a função existe em escopo global e a executa
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            
            # Formata o resultado para a API OpenAI (mensagem de papel de ferramenta)
            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })
        return results
    
    def system_prompt(self):
        """
        Gera o prompt do sistema para o LLM.
        
        Cria um prompt de sistema abrangente que instrui o LLM sobre como
        se comportar, incluindo o nome da pessoa, contexto do LinkedIn e
        resumo, e instruções para usar ferramentas.
        
        Returns:
            str: A string completa do prompt do sistema.
        """
        system_prompt = (
            f"You are acting as {self.name}. You are answering questions on {self.name}'s website, "
            f"particularly questions related to {self.name}'s career, background, skills and experience. "
            f"Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. "
            f"You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. "
            f"Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
            f"If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. "
            f"If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "
        )

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n## Resume:\n{self.resume}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        """
        Processa uma mensagem de chat e retorna uma resposta.
        
        Este método gerencia o loop principal da conversa, incluindo:
        - Construir o histórico de mensagens com o prompt do sistema
        - Fazer chamadas à API da OpenAI
        - Lidar com chamadas de ferramentas em um loop até o LLM fornecer uma resposta final
        - Retornar a resposta de texto final
        
        O loop continua até que o finish_reason do LLM não seja "tool_calls",
        permitindo execução de ferramentas multi-turno.
        
        Args:
            message (str): A mensagem/consulta do usuário.
            history (list): Histórico de conversa anterior como uma lista de
                dicionários de mensagem com chaves "role" e "content".
        
        Returns:
            str: A resposta de texto final do LLM para o usuário.
        """
        # Construir lista de mensagens: prompt do sistema + histórico + mensagem do usuário atual
        messages = (
            [{"role": "system", "content": self.system_prompt()}] 
            + history 
            + [{"role": "user", "content": message}]
        )
        
        # Loop até obter uma resposta final (não uma tool_call)
        done = False
        while not done:
            # Fazer chamada à API com ferramentas disponíveis
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )
            
            # Verifica se o LLM quer usar alguma tool
            if response.choices[0].finish_reason == "tool_calls":
                # Extrai chamadas de ferramentas e as executa
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                
                # Adiciona mensagem de tool_call e resultados ao histórico da conversa
                messages.append(message)
                messages.extend(results)
                # Continua o loop para obter a resposta do LLM após a execução da tool
            else:
                # O LLM forneceu uma resposta de texto final, sai do loop
                done = True
        
        return response.choices[0].message.content
    

if __name__ == "__main__":
    """
    Inicia a interface de chat do Gradio.
    
    Cria uma instância Me e inicia um ChatInterface do Gradio que usa
    o método chat para lidar com conversas.
    """
    me = Me()
    interface = gr.ChatInterface(me.chat, type="messages")
    interface.launch()
    