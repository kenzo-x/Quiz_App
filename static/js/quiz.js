(function () {
  const state = {
    currentQuestion: null,
    answered: false,
    finished: false,
    quizzes: [],
    selectedQuiz: null,
  };

  const els = {
    question: document.getElementById("question-text"),
    choices: Array.from(document.querySelectorAll(".choice-btn")),
    result: document.getElementById("result"),
    explanation: document.getElementById("explanation"),
    progress: document.getElementById("progress"),
    score: document.getElementById("score"),
    nextBtn: document.getElementById("next-btn"),
    quizSelect: document.getElementById("quiz-select"),
    quizSelectLabel: document.getElementById("quiz-select-label"),
  };

  function setButtonsDisabled(disabled) {
    els.choices.forEach((btn) => {
      btn.disabled = disabled;
    });
  }

  function renderFinished(payload) {
    state.finished = true;
    els.question.textContent = "全ての問題が終了しました";
    els.result.textContent = "";
    els.explanation.textContent = "";
    setButtonsDisabled(true);
    els.nextBtn.disabled = true;
    els.progress.textContent = `${payload.total} / ${payload.total}`;
    els.score.textContent = `Score: ${payload.score}`;
  }

  function renderQuizSelect() {
    if (!els.quizSelect) return;
    els.quizSelect.innerHTML = "";
    state.quizzes.forEach((name) => {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      if (name === state.selectedQuiz) opt.selected = true;
      els.quizSelect.appendChild(opt);
    });
    if (els.quizSelectLabel) {
      els.quizSelectLabel.textContent = state.selectedQuiz ? `選択中: ${state.selectedQuiz}` : "クイズファイルを選択";
    }
  }

  async function fetchQuizzes() {
    const res = await fetch("/api/quizzes");
    if (!res.ok) return;
    const data = await res.json();
    state.quizzes = data.files || [];
    state.selectedQuiz = data.selected || (state.quizzes.length ? state.quizzes[0] : null);
    renderQuizSelect();
  }

  async function selectQuiz(filename) {
    if (!filename) return;
    const res = await fetch("/api/select_quiz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(err.error || "クイズの切り替えに失敗しました");
      return;
    }
    state.selectedQuiz = filename;
    state.finished = false;
    await fetchQuestion();
    renderQuizSelect();
  }

  async function fetchQuestion() {
    const res = await fetch("/api/question");
    if (!res.ok) {
      els.result.textContent = "問題の取得に失敗しました";
      els.result.className = "result fail";
      return;
    }
    const data = await res.json();
    if (data.selected_quiz) {
      state.selectedQuiz = data.selected_quiz;
      renderQuizSelect();
    }
    if (data.finished) {
      renderFinished(data);
      return;
    }
    state.currentQuestion = data;
    state.answered = false;
    els.question.textContent = data.question;
    els.choices.forEach((btn, idx) => {
      btn.textContent = data.choices[idx];
      btn.disabled = false;
    });
    els.result.textContent = "";
    els.result.className = "result";
    els.explanation.textContent = "";
    els.progress.textContent = `${data.index} / ${data.total}`;
    els.score.textContent = `Score: ${data.score}`;
    els.nextBtn.disabled = true;
  }

  async function submitAnswer(choiceIndex) {
    if (state.finished || state.answered || !state.currentQuestion) return;
    setButtonsDisabled(true);
    const payload = {
      id: state.currentQuestion.id,
      choice_index: choiceIndex,
      player_id: "p0",
    };
    const res = await fetch("/api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      els.result.textContent = err.error || "回答の送信に失敗しました";
      els.result.className = "result fail";
      setButtonsDisabled(false);
      return;
    }
    const data = await res.json();
    state.answered = true;
    els.result.textContent = data.correct ? "正解!" : "不正解";
    els.result.className = `result ${data.correct ? "success" : "fail"}`;
    els.explanation.textContent = `正解: ${data.correct_choice} / ${data.explanation || ""}`;
    els.score.textContent = `Score: ${data.score}`;
    els.nextBtn.disabled = false;
  }

  async function goNext() {
    if (state.finished) return;
    await fetch("/api/next", { method: "POST", headers: { "Content-Type": "application/json" } });
    await fetchQuestion();
  }

  function bindEvents() {
    els.choices.forEach((btn) => {
      btn.addEventListener("click", () => {
        const choice = Number(btn.dataset.choice);
        submitAnswer(choice);
      });
    });
    els.nextBtn.addEventListener("click", () => {
      goNext();
    });
    if (els.quizSelect) {
      els.quizSelect.addEventListener("change", (e) => {
        const value = e.target.value;
        selectQuiz(value);
      });
    }
  }

  async function init() {
    if (state.__initialized) return;
    state.__initialized = true;
    bindEvents();
    await fetchQuizzes();
    await fetchQuestion();
  }

  if (document.body?.dataset.autoInit === "true" || document.body?.dataset.autoInit === "True" || document.body?.hasAttribute("data-auto-init")) {
    document.addEventListener("DOMContentLoaded", init);
  }

  window.quizApp = {
    init,
    submitAnswer,
    next: goNext,
    refresh: fetchQuestion,
    state,
  };
})();
