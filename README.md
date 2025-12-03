---
title: GabrielMartins_AI_Portfolio
app_file: app.py
sdk: gradio
sdk_version: 5.34.2
---

# Chatbot de Conversas sobre Carreira

Uma aplicação de chatbot interativa que simula conversas como uma pessoa específica (Gabriel Martins) usando o GPT-4o-mini da OpenAI. O chatbot responde perguntas sobre carreira, histórico, habilidades e experiência usando contexto de um perfil do LinkedIn e resumo pessoal.

## Recursos

- 🤖 **Conversas com IA**: Usa GPT-4o-mini para gerar respostas naturais e contextuais
- 📄 **Consciente do Contexto**: Carrega informações de PDF do LinkedIn e arquivos de texto de resumo
- 🛠️ **Chamada de Ferramentas**: Suporta chamada de funções para registrar interações do usuário
- 📱 **Notificações Push**: Integra com API Pushover para notificar sobre interações do usuário
- 💬 **Interface Interativa**: Interface de chat Gradio para conversas fluidas
- 🔄 **Execução Multi-Turno de Ferramentas**: Gerencia conversas complexas com múltiplas chamadas de ferramentas

## Como Funciona

1. O chatbot carrega informações pessoais de `me/linkedin.pdf`, `me/resume.pdf` e `me/summary.txt`
2. Os usuários interagem através de uma interface de chat Gradio
3. O LLM gera respostas com base no contexto carregado
4. Quando apropriado, o LLM chama ferramentas para:
   - Registrar detalhes de contato do usuário (email, nome, notas)
   - Registrar perguntas que não puderam ser respondidas
5. As execuções de ferramentas acionam notificações Pushover

## Configuração

### Pré-requisitos

- Python 3.8+
- Chave de API da OpenAI
- Conta Pushover (opcional, para notificações)

### Instalação

1. Clone ou baixe este repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
   
   Ou instale manualmente:
   ```bash
   pip install openai gradio python-dotenv requests pypdf
   ```

3. Crie um arquivo `.env` com suas chaves de API:
   ```
   OPENAI_API_KEY=sua_chave_api_openai_aqui
   PUSHOVER_TOKEN=seu_token_pushover_aqui
   PUSHOVER_USER=sua_chave_usuario_pushover_aqui
   ```

4. Certifique-se de ter os arquivos necessários:
   - `me/linkedin.pdf`: Arquivo PDF com informações do perfil do LinkedIn
   - `me/resume.pdf`: Arquivo PDF com currículo
   - `me/summary.txt`: Arquivo de texto com resumo pessoal

### Executando Localmente

```bash
python app.py
```

A interface Gradio será iniciada no seu navegador, geralmente em `http://127.0.0.1:7860`

## Variáveis de Ambiente

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `OPENAI_API_KEY` | Sua chave de API da OpenAI | Sim |
| `PUSHOVER_TOKEN` | Token da aplicação Pushover | Não (se não usar notificações) |
| `PUSHOVER_USER` | Chave de usuário Pushover | Não (se não usar notificações) |

## Funções de Ferramentas

### `record_user_details`
Registra quando um usuário fornece informações de contato (email, nome, notas) e envia uma notificação.

### `record_unknown_question`
Registra perguntas que o chatbot não conseguiu responder com base no contexto fornecido.

## Estrutura do Projeto

```
.
├── app.py                 # Arquivo principal da aplicação
├── README.md              # Este arquivo
├── requirements.txt       # Dependências do projeto
├── .env                   # Variáveis de ambiente (não está no repositório)
└── me/
    ├── linkedin.pdf       # PDF do perfil do LinkedIn
    └── summary.txt        # Texto de resumo pessoal
```

## Desenvolvimento

Esta aplicação está configurada para implantação no Hugging Face Spaces. Os metadados no frontmatter especificam:
- SDK: Gradio
- Versão do SDK: 5.34.2
- Arquivo da Aplicação: app.py

Para atualizar o espaço implantado, faça commit e push das alterações para o repositório Git conectado.

## Uso

Após iniciar a aplicação, você pode:

1. Fazer perguntas sobre carreira, experiência profissional, habilidades, etc.
2. O chatbot responderá como se fosse a pessoa simulada (Gabriel Martins)
3. Se você fornecer seu email, o chatbot registrará suas informações de contato
4. Perguntas não respondidas serão registradas para análise posterior

## Licença

Este projeto é para uso pessoal/educacional.
