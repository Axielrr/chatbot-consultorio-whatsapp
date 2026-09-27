# 🏥 Chatbot de Atendimento para Consultório (WhatsApp)

Chatbot de atendimento automatizado para consultórios médicos/odontológicos, integrado ao WhatsApp através da API do Twilio. Permite que pacientes agendem consultas, consultem horários disponíveis, cancelem agendamentos e tirem dúvidas frequentes — tudo pelo WhatsApp, sem intervenção humana.

## ✨ Funcionalidades

- 📅 **Agendamento de consultas** — coleta nome, data, horário e especialidade
- 🕐 **Consulta de horários disponíveis** por data
- ❌ **Cancelamento de consultas** vinculado ao número do paciente
- ❓ **Perguntas frequentes (FAQ)** — convênios, documentos, atrasos, valores
- 🏥 **Informações do consultório** — endereço, telefone, horário de funcionamento
- 📞 **Encaminhamento para atendente humano**
- 💾 Persistência de dados em JSON (agendamentos e sessões de conversa)

## 🛠️ Tecnologias

- **Python 3**
- **Flask** — servidor web que recebe as mensagens
- **Twilio API** — integração com o WhatsApp (via Sandbox para testes)
- **ngrok** — exposição do servidor local para a internet (ambiente de desenvolvimento)

## 📁 Estrutura do projeto

```
├── chatbot_consultorio.py   # Versão de terminal (console) do chatbot
├── app_whatsapp.py          # Versão integrada ao WhatsApp via Twilio (Flask)
├── requirements.txt         # Dependências do projeto
└── README.md
```

## 🚀 Como rodar localmente

### Versão de terminal (mais simples, sem WhatsApp)

```bash
python chatbot_consultorio.py
```

### Versão integrada ao WhatsApp

1. **Crie uma conta gratuita na Twilio**: [twilio.com/try-twilio](https://www.twilio.com/try-twilio)

2. **Ative o Sandbox do WhatsApp**: no Console da Twilio, vá em *Messaging → Try it out → Send a WhatsApp message* e siga as instruções para conectar seu número (enviar `join <código>` pelo WhatsApp).

3. **Instale as dependências:**
```bash
   pip install -r requirements.txt
```

4. **Rode o servidor:**
```bash
   python app_whatsapp.py
```
   O servidor sobe em `http://localhost:5000`.

5. **Exponha o servidor com o ngrok** (necessário para o Twilio acessar sua máquina local):
```bash
   ngrok http 5000
```
   Isso gera uma URL pública, por exemplo: `https://xxxx.ngrok-free.app`

6. **Configure o webhook no Twilio**: em *Messaging → Try it out → Send a WhatsApp message → Sandbox Settings*, cole a URL gerada seguida de `/whatsapp` no campo **"When a message comes in"**, com método **HTTP POST**. Salve.

Você: oi

Bot: 👋 Olá! Bem-vindo(a) ao Consultório Saúde & Bem-Estar.
 Digite o número da opção desejada:
 1️⃣ Agendar consulta
 2️⃣ Consultar horários disponíveis
 3️⃣ Cancelar consulta
 4️⃣ Perguntas frequentes
 5️⃣ Informações do consultório
 6️⃣ Falar com atendente humano
 Você: 1

Bot: 📅 Vamos agendar sua consulta!
Qual o seu nome completo?

## 🔮 Possíveis melhorias futuras

- Substituir o armazenamento em JSON por um banco de dados (PostgreSQL, SQLite)
- Adicionar lembretes automáticos de consulta (24h antes)
- Integrar com IA generativa para respostas mais naturais e flexíveis
- Painel administrativo web para o consultório gerenciar agendamentos
- Migrar do Sandbox de testes para um número de WhatsApp Business em produção

## 📄 Licença

Este projeto está sob a licença MIT.

---

Projeto desenvolvido como estudo de integração de chatbots com WhatsApp usando Python, Flask e a API da Twilio.

8. **Teste**: mande uma mensagem pelo WhatsApp para o número do Sandbox da Twilio. O bot deve responder automaticamente com o menu de atendimento!

## 💬 Exemplo de conversa
[20:28] **Você:** oi

[20:28] **PhishGuard:** Não entendi 🤔. 👋 Olá! Bem-vindo(a) ao Consultório Saúde & Bem-Estar.

Digite o número da opção desejada:
1️⃣ Agendar consulta
2️⃣ Consultar horários disponíveis
3️⃣ Cancelar consulta
4️⃣ Perguntas frequentes
5️⃣ Informações do consultório
6️⃣ Falar com atendente humano

A qualquer momento, digite menu para voltar aqui.

[20:29] **Você:** 1

[20:29] **PhishGuard:** 📅 Vamos agendar sua consulta!

Qual o seu nome completo?

[20:30] **Você:** Axiel Rodrigues Rosa

[20:30] **PhishGuard:** Para qual data você quer agendar? (DD/MM/AAAA)

[20:37] **Você:** 25/11/2026

[20:37] **PhishGuard:** Horários disponíveis em 25/11/2026:
1. 08:00
2. 09:00
3. 10:00
4. 11:00
5. 14:00
6. 15:00
7. 16:00
8. 17:00

Digite o número do horário desejado.

[20:38] **Você:** 6

[20:38] **PhishGuard:** Qual a especialidade ou motivo da consulta?

[20:38] **Você:** Clínico geral

[20:38] **PhishGuard:** ✅ Consulta agendada com sucesso!
Paciente: Axiel Rodrigues Rosa
Data: 25/11/2026 às 15:00
Especialidade: Clínico geral

Digite menu para voltar ao início.

[21:33] **Você:** Boa Noite

[21:33] **PhishGuard:** ✅ Consulta agendada com sucesso!
Paciente: Axiel Rodrigues Rosa
Data: 25/11/2026 às 15:00
Especialidade: Boa Noite

