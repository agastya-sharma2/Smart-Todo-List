from flask import Flask, render_template, request, redirect
import logic

app = Flask(__name__)

@app.route("/")
def home():
    tasks = logic.load_tasks()
    
    return render_template(
        "index.html",
        due_now = tasks["due_now"],
        due_pace = tasks["due_pace"],
        due_later = tasks["due_later"]
    )

@app.route("/add", methods=["POST"])
def add():
    task_name = request.form["task"]
    es_time = int(request.form["estimated_time"])
    due_date = request.form.get("due_date")

    logic.add_task(task_name, es_time, due_date)
    return redirect("/")

@app.route("/complete", methods=["POST"])
def complete():
    task_name = request.form.get('task_name')
    is_slice = request.form.get('is_slice') == 'True'
    parent_name = request.form.get('parent_name')

    logic.remove_task(task_name, is_slice=is_slice, parent_name=parent_name)
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)