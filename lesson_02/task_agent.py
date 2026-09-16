task_list = []
task_id_num = 0

def create_task(title, description, priority="medium"):
    task_id_num += 1
    task_list.append({"task_id": f"TASK-{task_id_num}"})
