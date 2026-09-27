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

## 📂 Estrutura do projeto
