async function loadMemory() {
    const res = await fetch("/api/memory");
    const records = await res.json();
    const list = document.getElementById("memory-list");
    list.innerHTML = records.map(r => `<div>${r.goal} — ${r.outcome}</div>`).join("");
}

let currentTaskId = null;
let eventSource = null;

async function runTask() {
    const goal = document.getElementById("goal-input").value;
    const autoApprove = document.getElementById("auto-approve-toggle").checked;

    const res = await fetch("/api/tasks", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({goal: goal, auto_approve: autoApprove})
    });
    const task = await res.json();
    currentTaskId = task.id;

    document.getElementById("activity-log").innerHTML = "";
    document.getElementById("final-report").innerText = "";
    startEventStream(currentTaskId);
}

function startEventStream(taskId) {
    if (eventSource) eventSource.close();
    eventSource = new EventSource(`/api/tasks/${taskId}/events`);

    eventSource.onmessage = async (e) => {
        const payload = JSON.parse(e.data);
        logActivity(payload);

        const task = await fetchTask(taskId);
        renderTask(task);

        if (task.status === "completed" || task.status === "failed") {   // task状态是哪两个值时,这条SSE连接该主动关掉?(回忆main.py里判断过的同一件事)
            eventSource.close();
        }
    };
}

async function fetchTask(taskId) {
    const res = await fetch(`/api/tasks/${taskId}`);
    return await res.json();
}

function logActivity(payload) {
    const log = document.getElementById("activity-log");
    const text = payload.type === "snapshot" ? "Connected, loading snapshot..." : payload.message;
    log.innerHTML += `<div>${text}</div>`;
    log.scrollTop = log.scrollHeight;
}

function renderTask(task) {
    document.getElementById("active-goal").innerText = task.goal;
    document.getElementById("committee-status").innerText = task.status;
    document.getElementById("task-steps").innerHTML = task.steps.map(
        s => `<li>${s.agent}: ${s.command} [${s.status}]</li>`
    ).join("");

    if (task.risk) {
        document.getElementById("risk-score").innerText = `Risk: ${task.risk.score} (${task.risk.level})`;
    }
    if (task.report) {
        document.getElementById("final-report").innerText = task.report;
    }
    renderApprovalButtons(task);
}

function renderApprovalButtons(task) {
    const container = document.getElementById("risk-score");
    const existing = document.getElementById("approval-buttons");
    if (existing) existing.remove();

    if (task.status === "awaiting_approval") {   
        const div = document.createElement("div");
        div.id = "approval-buttons";
        div.innerHTML = `
            <button class="approval-btn approve-btn">Approve</button>
            <button class="approval-btn deny-btn">Deny</button>
        `;
        container.after(div);
        div.querySelector(".approve-btn").onclick = () => sendApproval(task.id, true);
        div.querySelector(".deny-btn").onclick = () => sendApproval(task.id, false);
    }
}

async function sendApproval(taskId, approved) {
    await fetch(`/api/tasks/${taskId}/approval?approved=${approved}`, {method: "POST"});
}

document.getElementById("run-task-btn").onclick = runTask;
loadMemory();
