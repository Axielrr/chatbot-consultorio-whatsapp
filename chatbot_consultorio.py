"""
Chatbot de Atendimento - Consultório
=====================================
Chatbot de terminal para atendimento de consultório médico/odontológico.

Funcionalidades:
- Agendamento de consultas
- Consulta de horários disponíveis
- Cancelamento de consultas
- Perguntas frequentes (FAQ)
- Informações do consultório
- Encaminhamento para atendente humano

Os agendamentos são salvos em um arquivo JSON (agendamentos.json)
para persistir entre execuções do programa.
"""

import json
import os
import re
from datetime import datetime, timedelta

ARQUIVO_AGENDAMENTOS = "agendamentos.json"

# -------------------- CONFIGURAÇÕES DO CONSULTÓRIO --------------------

NOME_CONSULTORIO = "Consultório Saúde & Bem-Estar"
ENDERECO = "Rua das Flores, 123 - Centro"
TELEFONE = "(11) 1234-5678"
HORARIO_FUNCIONAMENTO = "Segunda a sexta, das 08h às 18h"

# Horários fixos disponíveis para agendamento (exemplo simplificado)
HORARIOS_DISPONIVEIS = [
    "08:00", "09:00", "10:00", "11:00",
    "14:00", "15:00", "16:00", "17:00"
]

FAQ = {
    "convenio": "Trabalhamos com os principais convênios. Confirme o seu na recepção pelo telefone {tel}.".format(tel=TELEFONE),
    "documentos": "Traga um documento com foto e, se possível, a carteirinha do convênio.",
    "atraso": "Pedimos que chegue com 15 minutos de antecedência. Atrasos acima de 15 minutos podem exigir reagendamento.",
    "cancelamento": "Cancelamentos podem ser feitos por aqui mesmo, com até 24h de antecedência.",
    "preco": "Os valores variam por especialidade. Consulte a recepção pelo telefone para mais detalhes.",
    "estacionamento": "Há estacionamento conveniado em frente ao consultório.",
}


def carregar_agendamentos():
    """Carrega agendamentos do arquivo JSON, se existir."""
    if os.path.exists(ARQUIVO_AGENDAMENTOS):
        try:
            with open(ARQUIVO_AGENDAMENTOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def salvar_agendamentos(agendamentos):
    """Salva a lista de agendamentos no arquivo JSON."""
    with open(ARQUIVO_AGENDAMENTOS, "w", encoding="utf-8") as f:
        json.dump(agendamentos, f, ensure_ascii=False, indent=2)


def validar_data(data_str):
    """Valida data no formato DD/MM/AAAA e verifica se não é passada."""
    try:
        data = datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        return None, "Data inválida. Use o formato DD/MM/AAAA (ex: 25/09/2026)."

    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if data < hoje:
        return None, "Essa data já passou. Informe uma data futura."

    if data.weekday() >= 5:  # sábado=5, domingo=6
        return None, "Não atendemos em fins de semana. Escolha um dia entre segunda e sexta."

    return data, None


def validar_telefone(tel_str):
    """Validação simples de telefone (aceita formatos comuns)."""
    numeros = re.sub(r"\D", "", tel_str)
    if 10 <= len(numeros) <= 11:
        return numeros
    return None


def horarios_livres(data_str, agendamentos):
    """Retorna os horários ainda livres para uma data."""
    ocupados = [a["horario"] for a in agendamentos if a["data"] == data_str]
    return [h for h in HORARIOS_DISPONIVEIS if h not in ocupados]


def agendar_consulta(agendamentos):
    print("\n📅 Vamos agendar sua consulta!")

    nome = input("Qual o seu nome completo? ").strip()
    while not nome:
        nome = input("Por favor, digite seu nome: ").strip()

    telefone = None
    while telefone is None:
        tel_input = input("Qual seu telefone para contato? ").strip()
        telefone = validar_telefone(tel_input)
        if telefone is None:
            print("Telefone inválido. Digite um número com DDD (ex: 11987654321).")

    data = None
    data_str = ""
    while data is None:
        data_str = input("Para qual data (DD/MM/AAAA)? ").strip()
        data, erro = validar_data(data_str)
        if erro:
            print(f"⚠️  {erro}")

    livres = horarios_livres(data_str, agendamentos)
    if not livres:
        print(f"\n😕 Não há horários livres em {data_str}. Tente outra data.")
        return

    print(f"\nHorários disponíveis em {data_str}:")
    for i, h in enumerate(livres, 1):
        print(f"  {i}. {h}")

    escolha = None
    while escolha is None:
        entrada = input("Escolha o número do horário desejado: ").strip()
        if entrada.isdigit() and 1 <= int(entrada) <= len(livres):
            escolha = livres[int(entrada) - 1]
        else:
            print("Opção inválida, tente novamente.")

    especialidade = input("Qual especialidade ou motivo da consulta? ").strip() or "Não informado"

    novo_agendamento = {
        "nome": nome,
        "telefone": telefone,
        "data": data_str,
        "horario": escolha,
        "especialidade": especialidade,
        "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    agendamentos.append(novo_agendamento)
    salvar_agendamentos(agendamentos)

    print("\n✅ Consulta agendada com sucesso!")
    print(f"   Paciente: {nome}")
    print(f"   Data: {data_str} às {escolha}")
    print(f"   Especialidade: {especialidade}")
    print("   Guarde essas informações. Você pode cancelar pelo menu principal.")


def cancelar_consulta(agendamentos):
    print("\n❌ Cancelamento de consulta")
    telefone = input("Digite o telefone usado no agendamento: ").strip()
    numeros = re.sub(r"\D", "", telefone)

    encontrados = [a for a in agendamentos if a["telefone"] == numeros]
    if not encontrados:
        print("Nenhum agendamento encontrado com esse telefone.")
        return

    print("\nAgendamentos encontrados:")
    for i, a in enumerate(encontrados, 1):
        print(f"  {i}. {a['data']} às {a['horario']} - {a['especialidade']} ({a['nome']})")

    entrada = input("Digite o número do agendamento a cancelar (ou 0 para voltar): ").strip()
    if not entrada.isdigit() or int(entrada) == 0:
        print("Operação cancelada.")
        return

    idx = int(entrada) - 1
    if 0 <= idx < len(encontrados):
        agendamento_remover = encontrados[idx]
        agendamentos.remove(agendamento_remover)
        salvar_agendamentos(agendamentos)
        print("✅ Consulta cancelada com sucesso.")
    else:
        print("Opção inválida.")


def consultar_horarios():
    print("\n🕐 Consulta de horários disponíveis")
    agendamentos = carregar_agendamentos()
    data_str = input("Para qual data (DD/MM/AAAA)? ").strip()
    data, erro = validar_data(data_str)
    if erro:
        print(f"⚠️  {erro}")
        return
    livres = horarios_livres(data_str, agendamentos)
    if livres:
        print(f"\nHorários livres em {data_str}: {', '.join(livres)}")
    else:
        print(f"\nNão há horários livres em {data_str}.")


def mostrar_faq():
    print("\n❓ Perguntas Frequentes")
    perguntas = {
        "1": ("Vocês aceitam convênio?", FAQ["convenio"]),
        "2": ("Quais documentos devo levar?", FAQ["documentos"]),
        "3": ("O que acontece se eu me atrasar?", FAQ["atraso"]),
        "4": ("Como cancelo minha consulta?", FAQ["cancelamento"]),
        "5": ("Quanto custa a consulta?", FAQ["preco"]),
        "6": ("Há estacionamento?", FAQ["estacionamento"]),
    }
    for chave, (pergunta, _) in perguntas.items():
        print(f"  {chave}. {pergunta}")

    escolha = input("Digite o número da pergunta (ou Enter para voltar): ").strip()
    if escolha in perguntas:
        print(f"\n👉 {perguntas[escolha][1]}")


def mostrar_informacoes():
    print(f"\n🏥 {NOME_CONSULTORIO}")
    print(f"   Endereço: {ENDERECO}")
    print(f"   Telefone: {TELEFONE}")
    print(f"   Funcionamento: {HORARIO_FUNCIONAMENTO}")


def falar_com_atendente():
    print("\n📞 Encaminhando para atendimento humano...")
    print(f"   Por favor, ligue para {TELEFONE} durante nosso horário de funcionamento.")
    print(f"   ({HORARIO_FUNCIONAMENTO})")


def menu_principal():
    print("\n" + "=" * 50)
    print(f"   {NOME_CONSULTORIO} — Atendimento Virtual")
    print("=" * 50)
    print("1. Agendar consulta")
    print("2. Consultar horários disponíveis")
    print("3. Cancelar consulta")
    print("4. Perguntas frequentes (FAQ)")
    print("5. Informações do consultório")
    print("6. Falar com atendente humano")
    print("0. Sair")


def main():
    agendamentos = carregar_agendamentos()
    print(f"👋 Olá! Bem-vindo(a) ao atendimento virtual do {NOME_CONSULTORIO}.")

    while True:
        menu_principal()
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            agendar_consulta(agendamentos)
        elif opcao == "2":
            consultar_horarios()
        elif opcao == "3":
            cancelar_consulta(agendamentos)
        elif opcao == "4":
            mostrar_faq()
        elif opcao == "5":
            mostrar_informacoes()
        elif opcao == "6":
            falar_com_atendente()
        elif opcao == "0":
            print("\nObrigado pelo contato. Até logo! 👋")
            break
        else:
            print("\n⚠️  Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
