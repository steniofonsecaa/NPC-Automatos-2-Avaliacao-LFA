PERGUNTAS_DISPONIVEIS_INFORMANTE = [
    "cidade", "castelo", "monstros", "historia", "lendas", 
    "animais magicos", "armas lendarias"
]

RESPOSTAS_INFORMANTE = {
    'cidade': "As cidades deste reino são antigas e cheias de segredos. Cada pedra conta uma história.",
    'castelo': "O grande castelo ao norte? Dizem que foi erguido por gigantes e que seus salões ecoam com os fantasmas do passado.",
    'monstros': "As bestas selvagens e criaturas da noite espreitam além das muralhas seguras. Viaje com cautela, especialmente ao anoitecer!",
    'historia': "Este reino viu a ascensão e queda de impérios! Heróis nasceram e pereceram, e muitas crônicas se perderam no tempo.",
    'lendas': "Ah, as lendas! Falam de tesouros esquecidos, bestas míticas e ilhas que aparecem e desaparecem com a maré.",
    'animais magicos': "Sim, criaturas imbuídas de magia ainda vagam pelas florestas primordiais e picos montanhosos. Avistá-las é um privilégio... ou um aviso.",
    'armas lendarias': "Existem contos sobre armas de poder incomensurável, forjadas pelos deuses antigos ou por artesãos de eras esquecidas. Encontrá-las é o destino de poucos."
}

INFORMANTE_NPC_AUTOMATON = {
    "INICIAL": {
        "message": "Saudações, viajante! Buscas conhecimento ou apenas um pouco de prosa? Tenho muitas histórias e informações.",
        "options": {
            "1": "Fazer uma pergunta",
            "2": "Despedir-se"
        },
        "transitions": {
            "1": "ESCOLHER_PERGUNTA",
            "2": "ENCERRADO"
        }
    },
    "ESCOLHER_PERGUNTA": { 
        "message": "Muito bem. Sobre o que sua curiosidade se debruça?",
        "options_generator_handler": "generate_informant_questions",
        "options": {
            "9": "Não tenho mais perguntas (Sair)" 
        },
        "transitions": {
            "9": "ENCERRADO"
        }
    },
    "PROCESSAR_ESCOLHA_PERGUNTA": {
        "action_handler": "handle_escolha_pergunta",
        "message": "Hmm, uma boa pergunta...",
        "options": {},
        "transitions": {}
    },
    "EXIBINDO_RESPOSTA": {
        "message": "Sobre isso, posso dizer que...", 
        "options": {
            "1": "Fazer outra pergunta",
            "2": "Entendido (Sair)"
        },
        "transitions": {
            "1": "ESCOLHER_PERGUNTA",
            "2": "ENCERRADO"
        }
    },
    "ENCERRADO": {
        "message": "Que seus caminhos sejam iluminados pelo conhecimento. Até breve!",
        "options": {},
        "transitions": {}
    }
}