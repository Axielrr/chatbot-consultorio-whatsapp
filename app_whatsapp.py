"""
Chatbot de Atendimento - Consultório (WhatsApp via Twilio)
=============================================================
Webhook Flask que recebe mensagens do WhatsApp através da API do Twilio
e conduz o mesmo fluxo de atendimento do chatbot de terminal:
agendamento, consulta de horários, cancelamento, FAQ e informações.

--------------------------------------------------------------------
COMO USAR (modo teste - Twilio Sandbox, gratuito):
--------------------------------------------------------------------
1. Crie uma conta em https://www.twilio.com/try-twilio
2. No painel, vá em "Messaging" > "Try it out" > "Send a WhatsApp message"
   e siga as instruções para entrar no Sandbox (enviar um código pelo
   WhatsApp do seu celular para o número de teste da Twilio).
3. Instale as dependências:
       pip install flask twilio
4. Rode este arquivo:
       python app_whatsapp.py
   O servidor vai rodar em http://localhost:5000
5. Como o Twilio precisa acessar sua máquina pela internet, use o ngrok
   (https://ngrok.com) para expor o servidor local:
       ngrok http 5000
   Isso vai gerar uma URL pública, ex: https://abcd1234.ngrok.io
6. No painel do Twilio, em "Sandbox Settings", cole a URL pública seguida
   de "/whatsapp" no campo "WHEN A MESSAGE COMES IN", por exemplo:
       https://abcd1234.ngrok.io/whatsapp
   Método: HTTP POST
7. Envie uma mensagem pelo WhatsApp para o número do Sandbox da Twilio.
   O bot deve responder automaticamente!

--------------------------------------------------------------------
Para produção (número de WhatsApp Business próprio), é necessário
solicitar aprovação do WhatsApp através do Twilio ou da Meta Cloud API,
mas a lógica do chatbot (abaixo) continua a mesma.
--------------------------------------------------------------------
"""

import json
import os
import re
from datetime import datetime

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

ARQUIVO_AGENDAMENTOS = "agendamentos.json"
ARQUIVO_SESSOES = "sessoes.json"

# -------------------- CONFIGURAÇÕES DO CONSULTÓRIO --------------------

NOME_CONSULTORIO = "Consultório Saúde & Bem-Estar"
ENDERECO = "Rua das Flores, 123 - Centro"
TELEFONE = "(11) 1234-5678"
HORARIO_FUNCIONAMENTO = "Segunda a sexta, das 08h às 18h"

HORARIOS_DISPONIVEIS = [
    "08:00", "09:00", "10:00", "11:00",
    "14:00", "15:00", "16:00", "17:00"
]

FAQ = {
    "1": ("Vocês aceitam convênio?",
          f"Trabalhamos com os principais convênios. Confirme o seu ligando para {TELEFONE}."),
    "2": ("Quais documentos devo levar?",
          "Traga um documento com foto e, se possível, a carteirinha do convênio."),
    "3": ("O que acontece se eu me atrasar?",
          "Pedimos que chegue com 15 minutos de antecedência. Atrasos acima de 15 minutos podem exigir reagendamento."),
    "4": ("Quanto custa a consulta?",
          "Os valores variam por especialidade. Ligue para a recepção para mais detalhes."),
    "5": ("Há estacionamento?",
          "Sim, há estacionamento conveniado em frente ao consultório."),
}

# -------------------- PERSISTÊNCIA --------------------


def carregar_json(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_agendamentos():
    dados = carregar_json(ARQUIVO_AGENDAMENTOS)
    return dados if isinstance(dados, list) else []


def salvar_agendamentos(lista):
    with open(ARQUIVO_AGENDAMENTOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)


# -------------------- VALIDAÇÕES --------------------


def validar_data(data_str):
    try:
        data = datetime.strptime(data_str.strip(), "%d/%m/%Y")
    except ValueError:
        return None, "Data inválida. Envie no formato DD/MM/AAAA (ex: 25/09/2026)."

    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if data < hoje:
        return None, "Essa data já passou. Envie uma data futura."
    if data.weekday() >= 5:
        return None, "Não atendemos em fins de semana. Escolha um dia entre segunda e sexta."
    return data, None


def horarios_livres(data_str, agendamentos):
    ocupados = [a["horario"] for a in agendamentos if a["data"] == data_str]
    return [h for h in HORARIOS_DISPONIVEIS if h not in ocupados]


# -------------------- MENU --------------------

MENU_TEXTO = (
    f"👋 Olá! Bem-vindo(a) ao *{NOME_CONSULTORIO}*.\n\n"
    "Digite o número da opção desejada:\n"
    "1️⃣ Agendar consulta\n"
    "2️⃣ Consultar horários disponíveis\n"
    "3️⃣ Cancelar consulta\n"
    "4️⃣ Perguntas frequentes\n"
    "5️⃣ Informações do consultório\n"
    "6️⃣ Falar com atendente humano\n\n"
    "A qualquer momento, digite *menu* para voltar aqui."
)


def nova_sessao():
    return {"estado": "menu", "dados": {}}


# -------------------- LÓGICA DE CONVERSA --------------------


def processar_mensagem(numero, texto, sessoes, agendamentos):
    """Recebe o número do remetente e o texto da mensagem,
    atualiza o estado da sessão e retorna a resposta."""

    texto = texto.strip()
    sessao = sessoes.get(numero, nova_sessao())
    estado = sessao["estado"]
    dados = sessao["dados"]

    texto_lower = texto.lower()
    if texto_lower in ("menu", "voltar", "cancelar tudo", "0"):
        sessoes[numero] = nova_sessao()
        return MENU_TEXTO

    # ----- ESTADO: MENU PRINCIPAL -----
    if estado == "menu":
        if texto == "1":
            sessao["estado"] = "agendar_nome"
            resposta = "📅 Vamos agendar sua consulta!\n\nQual o seu nome completo?"
        elif texto == "2":
            sessao["estado"] = "consultar_data"
            resposta = "🕐 Para qual data você quer consultar os horários? (DD/MM/AAAA)"
        elif texto == "3":
            minhas = [a for a in agendamentos if a["telefone"] == numero]
            if not minhas:
                resposta = "Você não possui agendamentos com este número.\n\n" + MENU_TEXTO
            else:
                linhas = [f"{i+1}. {a['data']} às {a['horario']} - {a['especialidade']}"
                          for i, a in enumerate(minhas)]
                dados["cancelaveis"] = minhas
                sessao["estado"] = "cancelar_escolha"
                resposta = ("❌ Seus agendamentos:\n" + "\n".join(linhas) +
                            "\n\nDigite o número do agendamento que deseja cancelar.")
        elif texto == "4":
            linhas = [f"{k}. {v[0]}" for k, v in FAQ.items()]
            sessao["estado"] = "faq_escolha"
            resposta = "❓ Perguntas frequentes:\n" + "\n".join(linhas) + \
                "\n\nDigite o número da pergunta."
        elif texto == "5":
            resposta = (f"🏥 *{NOME_CONSULTORIO}*\n"
                        f"Endereço: {ENDERECO}\n"
                        f"Telefone: {TELEFONE}\n"
                        f"Funcionamento: {HORARIO_FUNCIONAMENTO}\n\n" + MENU_TEXTO)
        elif texto == "6":
            resposta = (f"📞 Um momento, vou te encaminhar!\n"
                        f"Se preferir falar agora, ligue para {TELEFONE} "
                        f"({HORARIO_FUNCIONAMENTO}).\n\n" + MENU_TEXTO)
        else:
            resposta = "Não entendi 🤔. " + MENU_TEXTO

    # ----- FLUXO: AGENDAR -----
    elif estado == "agendar_nome":
        if not texto:
            resposta = "Por favor, digite seu nome completo:"
        else:
            dados["nome"] = texto
            sessao["estado"] = "agendar_data"
            resposta = "Para qual data você quer agendar? (DD/MM/AAAA)"

    elif estado == "agendar_data":
        data, erro = validar_data(texto)
        if erro:
            resposta = f"⚠️ {erro}"
        else:
            livres = horarios_livres(texto, agendamentos)
            if not livres:
                resposta = (f"😕 Não há horários livres em {texto}. "
                             "Envie outra data (DD/MM/AAAA) ou digite *menu* para voltar.")
            else:
                dados["data"] = texto
                dados["livres"] = livres
                sessao["estado"] = "agendar_horario"
                lista = "\n".join(f"{i+1}. {h}" for i, h in enumerate(livres))
                resposta = f"Horários disponíveis em {texto}:\n{lista}\n\nDigite o número do horário desejado."

    elif estado == "agendar_horario":
        livres = dados.get("livres", [])
        if texto.isdigit() and 1 <= int(texto) <= len(livres):
            dados["horario"] = livres[int(texto) - 1]
            sessao["estado"] = "agendar_especialidade"
            resposta = "Qual a especialidade ou motivo da consulta?"
        else:
            resposta = "Opção inválida. Digite o número correspondente ao horário."

    elif estado == "agendar_especialidade":
        especialidade = texto or "Não informado"
        novo = {
            "nome": dados["nome"],
            "telefone": numero,
            "data": dados["data"],
            "horario": dados["horario"],
            "especialidade": especialidade,
            "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        agendamentos.append(novo)
        salvar_agendamentos(agendamentos)
        sessoes[numero] = nova_sessao()
        resposta = (f"✅ Consulta agendada com sucesso!\n"
                    f"Paciente: {novo['nome']}\n"
                    f"Data: {novo['data']} às {novo['horario']}\n"
                    f"Especialidade: {especialidade}\n\n"
                    "Digite *menu* para voltar ao início.")

    # ----- FLUXO: CONSULTAR HORÁRIOS -----
    elif estado == "consultar_data":
        data, erro = validar_data(texto)
        if erro:
            resposta = f"⚠️ {erro}"
        else:
            livres = horarios_livres(texto, agendamentos)
            sessoes[numero] = nova_sessao()
            if livres:
                resposta = f"Horários livres em {texto}: {', '.join(livres)}\n\n" + MENU_TEXTO
            else:
                resposta = f"Não há horários livres em {texto}.\n\n" + MENU_TEXTO

    # ----- FLUXO: CANCELAR -----
    elif estado == "cancelar_escolha":
        cancelaveis = dados.get("cancelaveis", [])
        if texto.isdigit() and 1 <= int(texto) <= len(cancelaveis):
            item = cancelaveis[int(texto) - 1]
            if item in agendamentos:
                agendamentos.remove(item)
                salvar_agendamentos(agendamentos)
            sessoes[numero] = nova_sessao()
            resposta = "✅ Consulta cancelada com sucesso.\n\n" + MENU_TEXTO
        else:
            resposta = "Opção inválida. Digite o número do agendamento a cancelar, ou *menu* para voltar."

    # ----- FLUXO: FAQ -----
    elif estado == "faq_escolha":
        if texto in FAQ:
            sessoes[numero] = nova_sessao()
            resposta = f"👉 {FAQ[texto][1]}\n\n" + MENU_TEXTO
        else:
            resposta = "Opção inválida. Digite o número da pergunta, ou *menu* para voltar."

    else:
        sessao["estado"] = "menu"
        resposta = MENU_TEXTO

    sessoes[numero] = sessao
    return resposta


# -------------------- ROTA DO WEBHOOK --------------------


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    numero = request.values.get("From", "")  # ex: "whatsapp:+5511987654321"
    texto = request.values.get("Body", "")

    sessoes = carregar_json(ARQUIVO_SESSOES)
    agendamentos = carregar_agendamentos()

    if not texto.strip():
        resposta_texto = MENU_TEXTO
    else:
        resposta_texto = processar_mensagem(numero, texto, sessoes, agendamentos)

    salvar_json(ARQUIVO_SESSOES, sessoes)

    resposta = MessagingResponse()
    resposta.message(resposta_texto)
    return str(resposta)


@app.route("/", methods=["GET"])
def health_check():
    return f"Webhook do {NOME_CONSULTORIO} está ativo. Configure a URL /whatsapp no Twilio."


if __name__ == "__main__":
    app.run(debug=True, port=5000)
