# CRM de Relacionamentos Pessoal

Sistema de CRM pessoal com agentes inteligentes especializados para mapeamento automatico de relacionamentos. Construido com o framework **Agno** e modelos OpenAI.

## Conceito

O CRM ajuda voce a **manter relacoes saudaveis e focar em se comunicar com quem realmente importa**. Em vez de um CRM corporativo focado em vendas, este e um sistema pessoal que:

- Mapeia sua rede de relacionamentos automaticamente
- Calcula a saude de cada relacionamento (score 0-100)
- Sugere com quem voce deveria falar e quando
- Identifica gaps e oportunidades na sua rede
- Adapta prioridades ao seu perfil profissional

## Perfis Disponiveis

| Perfil | Foco | Categorias Prioritarias |
|--------|------|------------------------|
| **Empresario** | Clientes, parceiros, investidores | cliente, parceiro, investidor, fornecedor |
| **Diretor** | Equipe, stakeholders, mentorados | colega_trabalho, mentorado, parceiro |
| **Servidor Publico** | Relacoes institucionais, parcerias | governo, colega_trabalho, parceiro |
| **Saude** | Pacientes, referencias medicas | paciente, referencia_medica, colega_trabalho |
| **Custom** | Personalizado | Configuravel |

## Agentes Inteligentes

### 1. Analista de Relacionamentos
Avalia a saude de cada relacionamento, calcula scores, identifica tendencias e gera alertas.

### 2. Estrategista de Comunicacao
Sugere quando, como e por que comunicar com cada contato. Gera planos de comunicacao personalizados.

### 3. Mapeador de Rede
Analisa a estrutura da rede de contatos, identifica clusters, gaps e oportunidades de networking.

### 4. Consultor de Prioridades
Agente mais completo. Ajuda a focar nas pessoas certas, gerencia o CRM e configura perfis.

### 5. Orquestrador
Coordena todos os agentes. Entende sua intencao e delega para o especialista certo.

## Como Usar

### 1. Setup Inicial

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env com sua OPENAI_API_KEY

# Configurar perfil
python crm_main.py --setup
```

### 2. Modo Interativo (Chat)

```bash
# Usar o orquestrador (recomendado)
python crm_main.py

# Usar agente especifico
python crm_main.py --agent analyst
python crm_main.py --agent strategist
python crm_main.py --agent mapper
python crm_main.py --agent advisor
```

### 3. Comandos Rapidos (sem LLM)

```bash
# Relatorio rapido
python crm_main.py --report

# Sugestoes de comunicacao
python crm_main.py --suggest
```

### 4. Testes

```bash
# Rodar suite completa de testes (sem API key)
python test_crm.py
```

## Exemplos de Uso no Chat

```
Voce: Adicione o contato Maria Silva, cliente da empresa TechCorp, email maria@tech.com
Voce: Registre que almocei com o Joao ontem, conversa muito boa sobre o projeto
Voce: Como estao meus relacionamentos?
Voce: Com quem devo falar essa semana?
Voce: Onde tenho gaps na minha rede?
Voce: Quem estou negligenciando?
Voce: Gere um relatorio completo
```

## Arquitetura

```
crm_main.py                    # Entry point CLI
│
├── agents/
│   ├── crm_orchestrator.py    # Orquestrador (coordena todos)
│   ├── relationship_analyst.py # Analise de saude
│   ├── communication_strategist.py # Sugestoes de comunicacao
│   ├── network_mapper.py      # Mapeamento de rede
│   └── priority_advisor.py    # Consultoria de prioridades
│
├── tools/
│   ├── contact_manager.py     # CRUD de contatos e interacoes
│   ├── relationship_scorer.py # Algoritmo de scoring
│   ├── network_analyzer.py    # Analise de rede e sugestoes
│   └── profile_manager.py     # Gerenciamento de perfil
│
├── models/
│   └── crm.py                 # Schemas Pydantic
│
├── config/
│   ├── settings.py            # Configuracoes gerais
│   └── crm_profiles.py       # Perfis e defaults por tipo
│
├── storage/
│   └── crm_store.py           # Persistencia JSON
│
└── data/                      # Dados do usuario (gitignored)
    ├── contacts.json
    ├── interactions.json
    └── profile.json
```

## Score de Relacionamento (0-100)

O algoritmo considera:

| Fator | Impacto |
|-------|---------|
| Frequencia de contato vs ideal | +30 a -25 pontos |
| Volume de interacoes no mes | +20 a -10 pontos |
| Sentimento das interacoes | +10 a -10 pontos |
| Variedade de tipos de contato | +5 a +10 pontos |

| Score | Classificacao |
|-------|--------------|
| 80-100 | Forte |
| 60-79 | Moderado |
| 40-59 | Fraco |
| 20-39 | Esfriando |
| 0-19 | Perdido |
