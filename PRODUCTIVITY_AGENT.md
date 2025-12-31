# 📋 Life OS - Productivity Agent

> **Guardião do Foco e Gestão de Tempo baseada em Deep Work**

---

## 📋 Visão Geral

O **Productivity Agent** é o especialista em **Deep Work** e gestão de tempo do Life OS. Ele captura tarefas, organiza seu Inbox e protege seu tempo de foco com rigor militar.

### Tom de Voz:
**Estoico, Organizado, Essencialista e Breve.**

Não é um motivador. É um **guardião do tempo**.

---

## 🎯 Características Principais

### ✅ Captura Inteligente de Tarefas
- Extrai informações estruturadas de mensagens naturais
- Classifica automaticamente área e tipo de energia
- Estima esforço em Pomodoros (25min cada)

### ✅ Sistema de Energia Mental
- **Deep Work**: Tarefas que exigem foco total (programar, escrever, criar)
- **Shallow Work**: Tarefas logísticas/burocráticas (e-mail, reuniões, ligações)

### ✅ Proteção Contra Sobrecarga
- Alerta quando agenda ultrapassa 12 Pomodoros/dia (5h)
- Bloqueia agendamentos insustentáveis (>16 Pomodoros)
- Sugere redistribuição de carga semanal

### ✅ Gestão por Contextos
- **Inbox**: Tarefas capturadas, não agendadas
- **Scheduled**: Tarefas com data definida
- **In Progress**: Em execução
- **Completed**: Finalizadas

---

## 🍅 Sistema de Pomodoros

Cada Pomodoro = **25 minutos** de trabalho focado.

### Estimativas Padrão:

| Tipo de Tarefa | Pomodoros | Tempo |
|----------------|-----------|-------|
| Tarefa rápida | 1 🍅 | ~25min |
| Reunião padrão | 2 🍅 | ~50min |
| Tarefa média | 3-4 🍅 | 1h-1h40 |
| Projeto complexo | 6+ 🍅 | 2h30+ |

---

## 💡 Classificação Automática

### 📁 Áreas:

O agente classifica automaticamente baseado em palavras-chave:

- **Trabalho**: projeto, reunião, relatório, apresentação, cliente, deadline
- **Pessoal**: casa, família, comprar, pagar, ligar, agendar
- **Estudo**: estudar, curso, ler, aprender, revisar, praticar
- **Saúde**: academia, médico, exercício, corrida, yoga, meditação

### ⚡ Tipo de Energia:

- **Deep Work**:
  - Programar, escrever, planejar, criar
  - Desenvolver, projetar, analisar, estudar
  - **Requer**: Silêncio total, sem interrupções

- **Shallow Work**:
  - Responder, agendar, ligar, pagar
  - Organizar, revisar, reunião, e-mail
  - **Permite**: Interrupções ocasionais

---

## 🔄 Modos de Operação

### 1️⃣ Modo Captura (Inbox)

Quando você menciona uma tarefa, o agente captura e classifica:

**Você:** "Preciso estudar matemática hoje"

**Agent:**
```
📥 **Capturado:** 'Estudar Matemática'

📊 **Classificação:**
> Área: Estudo
> Tipo: Deep Work
> Estimativa: 4🍅 (~1h40)
> Status: Agendado para 31/12/2025

🔥 **Atenção:** Esta tarefa exige foco intenso. Reserve um bloco sem interrupções.
```

---

### 2️⃣ Modo Agenda

Consulte suas tarefas do dia:

**Você:** "O que tenho para hoje?"

**Agent:**
```
📅 **Sua Agenda de 31/12/2025 (Carga Total: 4h / 10🍅):**

🔥 **Deep Work (6🍅):**
[ ] Estudar Matemática (4🍅) - *Normal*
[ ] Escrever Relatório (2🍅) - *Alta*

📋 **Shallow Work (4🍅):**
[ ] Ligar para Médico (1🍅)
[ ] Responder E-mails (2🍅)
[ ] Organizar Documentos (1🍅)

💡 **Análise:** Carga equilibrada. Faça Deep Work pela manhã quando sua energia está alta.
```

---

### 3️⃣ Modo Inbox

Visualize tarefas não agendadas:

**Você:** "Me lembra de ligar pro médico"

**Agent:**
```
📥 **Capturado:** 'Ligar para Médico'

📊 **Classificação:**
> Área: Saúde
> Tipo: Shallow Work
> Estimativa: 1🍅 (~25min)
> Status: Inbox

💡 Quando quer fazer isso? Posso agendar para você.
```

---

### 4️⃣ Modo Visão Semanal

Veja distribuição de carga:

**Você:** "Como está minha semana?"

**Agent:**
```
📆 **Visão Semanal:**

Seg 30/12: 🔥 8 tarefas (14🍅) - SOBRECARREGADO
Ter 31/12: ✅ 4 tarefas (8🍅) - Equilibrado
Qua 01/01: ✅ 3 tarefas (6🍅) - Leve
Qui 02/01: 📭 Vazio
Sex 03/01: ✅ 2 tarefas (4🍅) - Leve

💡 **Recomendação:** Mova 2 tarefas de segunda para quinta para equilibrar.
```

---

## 🚨 Sistema de Alertas

### Alertas de Sobrecarga:

| Condição | Alerta |
|----------|--------|
| > 12 Pomodoros/dia | ⚠️ Carga alta. Pouco tempo para imprevistos |
| > 16 Pomodoros/dia | 🚨 INSUSTENTÁVEL. Mova tarefas para outro dia |
| Deep Work > 8 Pomodoros | 🔥 Muito foco concentrado. Intercale com tarefas leves |

---

## 📊 Ferramentas Disponíveis

### 1. `add_task()`
Adiciona nova tarefa ao sistema.

**Parâmetros:**
- `title`: Título da tarefa (conciso)
- `area`: Trabalho, Pessoal, Estudo, Saúde
- `pomodoros`: Estimativa de esforço (padrão: 1)
- `energy_type`: Deep Work ou Shallow Work
- `status`: inbox, scheduled, in_progress, completed
- `due_date`: Data de vencimento (DD/MM/YYYY)
- `priority`: Alta, Normal, Baixa
- `notes`: Observações adicionais

---

### 2. `get_today_tasks()`
Retorna tarefas agendadas para hoje agrupadas por tipo de energia.

**Retorna:**
```json
{
  "date": "31/12/2025",
  "total_tasks": 5,
  "total_pomodoros": 10,
  "total_hours": 4.2,
  "deep_work": {
    "count": 2,
    "pomodoros": 6,
    "tasks": [...]
  },
  "shallow_work": {
    "count": 3,
    "pomodoros": 4,
    "tasks": [...]
  },
  "alert": null
}
```

---

### 3. `get_inbox_tasks()`
Lista tarefas não agendadas (Inbox).

**Retorna:**
```json
{
  "total_inbox": 3,
  "by_area": {
    "Trabalho": [...],
    "Pessoal": [...]
  },
  "message": "📥 Organize estas tarefas para a sua agenda"
}
```

---

### 4. `update_task_status()`
Atualiza status de uma tarefa.

**Parâmetros:**
- `task_id`: ID da tarefa
- `new_status`: inbox, scheduled, in_progress, completed
- `completed_pomodoros`: Pomodoros realmente gastos (opcional)

---

### 5. `schedule_task()`
Agenda uma tarefa do Inbox para uma data específica.

**Parâmetros:**
- `task_id`: ID da tarefa
- `due_date`: Data desejada (DD/MM/YYYY)

**Inclui verificação de sobrecarga do dia.**

---

### 6. `get_weekly_overview()`
Retorna visão dos próximos 7 dias.

**Retorna:**
```json
{
  "week_overview": {
    "31/12/2025": {
      "tasks_count": 5,
      "total_pomodoros": 10,
      "total_hours": 4.2,
      "deep_work_count": 2,
      "status": "✅"
    }
  }
}
```

---

## 💾 Estrutura de Dados

### Arquivo: `data/tasks.json`

Cada tarefa contém:

```json
{
  "id": 1,
  "title": "Estudar Matemática",
  "area": "Estudo",
  "pomodoros": 4,
  "estimated_time": "4🍅 (~1.7h)",
  "energy_type": "Deep Work",
  "status": "scheduled",
  "priority": "Normal",
  "due_date": "31/12/2025",
  "notes": "",
  "created_at": "31/12/2025 10:00",
  "completed_at": "",
  "actual_pomodoros": 0,
  "estimation_variance": 0
}
```

---

## 🎯 Exemplos de Uso

### Exemplo 1: Captura Simples

**Você:** "Preciso programar a nova feature hoje"

**Agent:**
```
📥 **Capturado:** 'Programar nova feature'

📊 **Classificação:**
> Área: Trabalho
> Tipo: Deep Work
> Estimativa: 6🍅 (~2h30)
> Status: Agendado para 31/12

🔥 **Atenção:** Esta tarefa exige foco intenso. Reserve um bloco sem interrupções.
```

---

### Exemplo 2: Múltiplas Tarefas

**Você:** "Tenho que finalizar o relatório, ligar pro cliente e comprar um presente"

**Agent:**
```
📥 **Capturei 3 tarefas:**

1. Finalizar Relatório → Trabalho | Deep Work | 4🍅
2. Ligar para Cliente → Trabalho | Shallow Work | 1🍅
3. Comprar Presente → Pessoal | Shallow Work | 1🍅

Total: 6🍅 (~2h30). Quer agendar todas para hoje ou deixar no Inbox?
```

---

### Exemplo 3: Sobrecarga Detectada

**Você:** "Agenda mais essa tarefa de 8 horas pra hoje"

**Agent:**
```
🚨 **ALERTA DE SOBRECARGA**

Você já tem 14🍅 (5h50) agendados para hoje.
Adicionar mais 16🍅 resultaria em 30🍅 total (12h+).

Isso é INSUSTENTÁVEL. Você vai exaurir completamente.

💡 **Sugestão:** Mova algumas tarefas para amanhã ou quinta-feira (dias mais leves).
```

---

## 🧪 Como Testar

### Teste Isolado do Agente:

```bash
python agents/productivity_agent.py
```

### Teste no Sistema Multi-Agente:

```bash
# Demonstração automática
python demo_multi_agent.py

# Modo interativo
python demo_multi_agent.py --interactive
```

### Mensagens de Teste:

```
"Preciso estudar matemática hoje"
"Me lembra de ligar pro médico"
"O que tenho para hoje?"
"Tenho reunião de 2h, preciso escrever relatório e organizar documentos"
"Como está minha semana?"
```

---

## 📱 Integração com WhatsApp

O Productivity Agent funciona **transparentemente** através do sistema multi-agente:

```python
# whatsapp_integration.py
from lifeos_router import LifeOSRouter

router = LifeOSRouter()

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    message = data['message']['conversation']

    # Router direciona automaticamente para Productivity Agent
    result = router.route_message(message)

    send_whatsapp_message(sender, result['response'])
    return jsonify({'success': True})
```

**O usuário não percebe** que existem múltiplos agentes!

---

## 🎨 Diferenças do Finance Agent

| Aspecto | Finance Agent | Productivity Agent |
|---------|---------------|-------------------|
| **Foco** | Gastos e orçamento | Tarefas e tempo |
| **Unidade** | Reais (R$) | Pomodoros (🍅) |
| **Alertas** | Teto de orçamento | Sobrecarga de tempo |
| **Tom** | Auditor financeiro | Guardião do foco |
| **Dados** | transactions.json | tasks.json |
| **Conceitos** | Parcelamento, categorias | Deep Work, energia mental |

---

## 💡 Boas Práticas

### 1. **Estime com Realismo**
- Não subestime tarefas complexas
- 1 Pomodoro = 25min de trabalho FOCADO
- Reuniões sempre ocupam mais tempo que planejado

### 2. **Proteja o Deep Work**
- Máximo 3h de Deep Work por dia (ideal)
- Faça pela manhã quando energia está alta
- Bloqueie distrações (celular, e-mail, etc)

### 3. **Use o Inbox Estrategicamente**
- Capture TUDO no momento que pensar
- Organize semanalmente (domingo ou segunda)
- Não deixe tarefas no Inbox por mais de 1 semana

### 4. **Respeite a Carga Total**
- Máximo 12 Pomodoros/dia sustentável
- Deixe espaço para imprevistos (20% do dia)
- Reagende se algo urgente surgir

---

## 🚀 Próximas Features

- [ ] Integração com calendário (Google Calendar, Outlook)
- [ ] Rastreamento real de Pomodoros (timer integrado)
- [ ] Análise de produtividade semanal/mensal
- [ ] Sugestões de otimização baseadas em histórico
- [ ] Bloqueios de foco no celular (integração com Focus apps)
- [ ] Lembretes automáticos 15min antes de tarefas Deep Work

---

## 📊 Status

| Componente | Status |
|-----------|--------|
| **Agente** | ✅ Implementado |
| **Ferramentas** | ✅ 6 tools criadas |
| **Integração Multi-Agente** | ✅ Completa |
| **Documentação** | ✅ Completa |
| **Testes** | ✅ Disponíveis |
| **WhatsApp** | ✅ Compatível |

---

**Desenvolvido com Agno Framework para Life OS** 🚀

*Estoico. Organizado. Essencialista. Breve.*
