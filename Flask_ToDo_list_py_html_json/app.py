import json
import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "todo_data.json"

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    all_tasks = load_tasks()
    current_filter = request.args.get("filter", "all")
    
    # กรองข้อมูลตามสถานะที่กดเลือก
    if current_filter == "active":
        filtered_tasks = [t for t in all_tasks if not t.get("done")]
    elif current_filter == "done":
        filtered_tasks = [t for t in all_tasks if t.get("done")]
    else:
        filtered_tasks = all_tasks

    done_count = sum(1 for t in all_tasks if t.get("done"))
    
    return render_template(
        "index.html", 
        tasks=filtered_tasks, 
        total_count=len(all_tasks),
        done_count=done_count, 
        current_filter=current_filter
    )

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    filter_state = request.form.get("filter", "all")
    if title:
        tasks = load_tasks()
        # ดึงเวลาปัจจุบัน เช่น "14:30" (หรือใช้ "%H:%M:%S" หากต้องการวินาทีด้วย)
        created_at = datetime.now().strftime("%H:%M")
        # หา ID สูงสุดที่มีอยู่แล้ว + 1 (หากไม่มีงานเลยให้เริ่มที่ 1)
        max_id = max([t["id"] for t in tasks], default=0)
        new_id = max_id + 1
        tasks.insert(0, {"id": new_id, "title": title, "done": False, "created_at": created_at})
        save_tasks(tasks)
    return redirect(url_for("index", filter=filter_state))

@app.route("/toggle/<int:task_id>")
def toggle_task(task_id):
    filter_state = request.args.get("filter", "all")
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = not t["done"]
            break
    save_tasks(tasks)
    return redirect(url_for("index", filter=filter_state))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    filter_state = request.args.get("filter", "all")
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    return redirect(url_for("index", filter=filter_state))

@app.route("/clear_done")
def clear_done():
    filter_state = request.args.get("filter", "all")
    tasks = load_tasks()
    tasks = [t for t in tasks if not t.get("done")]
    save_tasks(tasks)
    return redirect(url_for("index", filter=filter_state))

if __name__ == "__main__":
    app.run(debug=True)