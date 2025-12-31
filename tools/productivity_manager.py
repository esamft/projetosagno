"""
Life OS - Gerenciador de Produtividade

Ferramentas para gestão de tarefas baseadas em Deep Work e Pomodoro.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from loguru import logger


# Diretório de dados
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TASKS_FILE = DATA_DIR / "tasks.json"


def _load_tasks() -> List[Dict[str, Any]]:
    """Carrega tarefas do arquivo JSON"""
    if not TASKS_FILE.exists():
        return []

    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar tarefas: {e}")
        return []


def _save_tasks(tasks: List[Dict[str, Any]]) -> None:
    """Salva tarefas no arquivo JSON"""
    try:
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Erro ao salvar tarefas: {e}")


def add_task(
    title: str,
    area: str = "Pessoal",
    pomodoros: int = 1,
    energy_type: str = "Shallow Work",
    status: str = "inbox",
    due_date: Optional[str] = None,
    priority: str = "Normal",
    notes: Optional[str] = None
) -> str:
    """
    Adiciona nova tarefa ao sistema de produtividade.

    Args:
        title: Título da tarefa (conciso)
        area: Área da tarefa (Trabalho, Pessoal, Estudo, Saúde)
        pomodoros: Estimativa de esforço em Pomodoros (1 Pomodoro = 25min)
        energy_type: Tipo de energia (Deep Work ou Shallow Work)
        status: Status da tarefa (inbox, scheduled, in_progress, completed)
        due_date: Data de vencimento (formato DD/MM/YYYY, opcional)
        priority: Prioridade (Alta, Normal, Baixa)
        notes: Notas adicionais (opcional)

    Returns:
        Mensagem de confirmação com ID da tarefa
    """

    # Validações
    valid_areas = ["Trabalho", "Pessoal", "Estudo", "Saúde"]
    if area not in valid_areas:
        area = "Pessoal"

    valid_energy = ["Deep Work", "Shallow Work"]
    if energy_type not in valid_energy:
        energy_type = "Shallow Work"

    valid_status = ["inbox", "scheduled", "in_progress", "completed"]
    if status not in valid_status:
        status = "inbox"

    valid_priority = ["Alta", "Normal", "Baixa"]
    if priority not in valid_priority:
        priority = "Normal"

    # Carregar tarefas existentes
    tasks = _load_tasks()

    # Criar nova tarefa
    task_id = len(tasks) + 1

    # Calcular tempo estimado
    estimated_hours = (pomodoros * 25) / 60
    estimated_time = f"{pomodoros}🍅 (~{estimated_hours:.1f}h)"

    task = {
        "id": task_id,
        "title": title,
        "area": area,
        "pomodoros": pomodoros,
        "estimated_time": estimated_time,
        "energy_type": energy_type,
        "status": status,
        "priority": priority,
        "due_date": due_date or "",
        "notes": notes or "",
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "completed_at": ""
    }

    tasks.append(task)
    _save_tasks(tasks)

    logger.info(f"✅ Tarefa criada: {title} (ID: {task_id})")

    return json.dumps({
        "success": True,
        "task_id": task_id,
        "title": title,
        "area": area,
        "pomodoros": pomodoros,
        "estimated_time": estimated_time,
        "energy_type": energy_type,
        "status": status,
        "priority": priority
    }, ensure_ascii=False)


def get_today_tasks() -> str:
    """
    Retorna todas as tarefas agendadas para hoje.

    Returns:
        JSON com tarefas de hoje agrupadas por tipo de energia
    """
    tasks = _load_tasks()
    today = datetime.now().strftime("%d/%m/%Y")

    # Filtrar tarefas de hoje (scheduled e in_progress)
    today_tasks = [
        t for t in tasks
        if t.get("due_date") == today and t["status"] in ["scheduled", "in_progress"]
    ]

    # Agrupar por energia
    deep_work = [t for t in today_tasks if t["energy_type"] == "Deep Work"]
    shallow_work = [t for t in today_tasks if t["energy_type"] == "Shallow Work"]

    # Calcular totais
    total_pomodoros = sum(t["pomodoros"] for t in today_tasks)
    total_hours = (total_pomodoros * 25) / 60
    deep_pomodoros = sum(t["pomodoros"] for t in deep_work)
    shallow_pomodoros = sum(t["pomodoros"] for t in shallow_work)

    return json.dumps({
        "date": today,
        "total_tasks": len(today_tasks),
        "total_pomodoros": total_pomodoros,
        "total_hours": round(total_hours, 1),
        "deep_work": {
            "count": len(deep_work),
            "pomodoros": deep_pomodoros,
            "tasks": deep_work
        },
        "shallow_work": {
            "count": len(shallow_work),
            "pomodoros": shallow_pomodoros,
            "tasks": shallow_work
        },
        "alert": "⚠️ Carga excessiva de Deep Work!" if deep_pomodoros > 12 else None
    }, ensure_ascii=False, indent=2)


def get_inbox_tasks() -> str:
    """
    Retorna todas as tarefas no Inbox (não agendadas).

    Returns:
        JSON com tarefas no inbox agrupadas por área
    """
    tasks = _load_tasks()

    # Filtrar tarefas no inbox
    inbox = [t for t in tasks if t["status"] == "inbox"]

    # Agrupar por área
    by_area = {}
    for task in inbox:
        area = task["area"]
        if area not in by_area:
            by_area[area] = []
        by_area[area].append(task)

    return json.dumps({
        "total_inbox": len(inbox),
        "by_area": by_area,
        "message": "📥 Organize estas tarefas para a sua agenda" if len(inbox) > 0 else "✅ Inbox vazio!"
    }, ensure_ascii=False, indent=2)


def update_task_status(task_id: int, new_status: str, completed_pomodoros: Optional[int] = None) -> str:
    """
    Atualiza o status de uma tarefa.

    Args:
        task_id: ID da tarefa
        new_status: Novo status (inbox, scheduled, in_progress, completed)
        completed_pomodoros: Número de pomodoros realmente gastos (opcional)

    Returns:
        Mensagem de confirmação
    """
    tasks = _load_tasks()

    # Encontrar tarefa
    task = next((t for t in tasks if t["id"] == task_id), None)

    if not task:
        return json.dumps({
            "success": False,
            "error": f"Tarefa {task_id} não encontrada"
        })

    # Atualizar status
    old_status = task["status"]
    task["status"] = new_status

    # Se completou, registrar data
    if new_status == "completed":
        task["completed_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        if completed_pomodoros:
            task["actual_pomodoros"] = completed_pomodoros
            variance = completed_pomodoros - task["pomodoros"]
            task["estimation_variance"] = variance

    _save_tasks(tasks)

    logger.info(f"✅ Tarefa {task_id} atualizada: {old_status} → {new_status}")

    return json.dumps({
        "success": True,
        "task_id": task_id,
        "title": task["title"],
        "old_status": old_status,
        "new_status": new_status,
        "completed_at": task.get("completed_at", "")
    }, ensure_ascii=False)


def schedule_task(task_id: int, due_date: str) -> str:
    """
    Agenda uma tarefa do Inbox para uma data específica.

    Args:
        task_id: ID da tarefa
        due_date: Data desejada (formato DD/MM/YYYY)

    Returns:
        Mensagem de confirmação
    """
    tasks = _load_tasks()

    # Encontrar tarefa
    task = next((t for t in tasks if t["id"] == task_id), None)

    if not task:
        return json.dumps({
            "success": False,
            "error": f"Tarefa {task_id} não encontrada"
        })

    # Atualizar
    task["due_date"] = due_date
    task["status"] = "scheduled"

    _save_tasks(tasks)

    # Verificar carga do dia
    today_tasks_data = json.loads(get_today_tasks())
    total_pomodoros = today_tasks_data.get("total_pomodoros", 0)

    alert = None
    if total_pomodoros > 16:
        alert = "🚨 ALERTA: Você tem mais de 16 Pomodoros (6h+) agendados. Isso é insustentável!"
    elif total_pomodoros > 12:
        alert = "⚠️ ATENÇÃO: Você tem muitas tarefas agendadas. Considere realocar algumas."

    logger.info(f"✅ Tarefa {task_id} agendada para {due_date}")

    return json.dumps({
        "success": True,
        "task_id": task_id,
        "title": task["title"],
        "due_date": due_date,
        "day_total_pomodoros": total_pomodoros,
        "alert": alert
    }, ensure_ascii=False)


def get_weekly_overview() -> str:
    """
    Retorna visão geral da semana (próximos 7 dias).

    Returns:
        JSON com distribuição de tarefas por dia
    """
    tasks = _load_tasks()

    # Próximos 7 dias
    weekly_overview = {}

    for i in range(7):
        date = (datetime.now() + timedelta(days=i)).strftime("%d/%m/%Y")
        day_tasks = [
            t for t in tasks
            if t.get("due_date") == date and t["status"] in ["scheduled", "in_progress"]
        ]

        total_pomodoros = sum(t["pomodoros"] for t in day_tasks)
        total_hours = (total_pomodoros * 25) / 60

        weekly_overview[date] = {
            "tasks_count": len(day_tasks),
            "total_pomodoros": total_pomodoros,
            "total_hours": round(total_hours, 1),
            "deep_work_count": len([t for t in day_tasks if t["energy_type"] == "Deep Work"]),
            "status": "🔥" if total_pomodoros > 12 else "✅" if total_pomodoros > 0 else "📭"
        }

    return json.dumps({
        "week_overview": weekly_overview
    }, ensure_ascii=False, indent=2)
