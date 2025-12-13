import os
import random
from pathlib import Path
from typing import Dict, Any, List

from flask import Flask, jsonify, render_template, request, session

from quiz_engine import QuizEngine

# 実行方法（簡易README相当）
# python -m venv .venv && source .venv/bin/activate
# pip install -r requirements.txt
# flask run もしくは python app.py で起動し /quiz /overlay にアクセス

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(24)
RANDOMIZE_ORDER = os.getenv("QUIZ_RANDOMIZE", "false").lower() == "true"

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
app.secret_key = SECRET_KEY

_engine_cache: Dict[str, QuizEngine] = {}


def list_quiz_files() -> List[str]:
    files = sorted([p.name for p in DATA_DIR.glob("*.xlsx") if p.is_file()])
    return files


def get_engine_for(filename: str) -> QuizEngine:
    files = list_quiz_files()
    if filename not in files:
        raise FileNotFoundError(f"指定されたクイズファイルが見つかりません: {filename}")
    if filename in _engine_cache:
        return _engine_cache[filename]
    engine = QuizEngine.load_from_excel(str(DATA_DIR / filename))
    _engine_cache[filename] = engine
    return engine


def get_selected_quiz() -> str:
    files = list_quiz_files()
    if not files:
        raise FileNotFoundError("data ディレクトリに *.xlsx がありません")
    selected = session.get("selected_quiz")
    if not selected or selected not in files:
        selected = files[0]
        session["selected_quiz"] = selected
        _reset_progress(selected)
    return selected


def _reset_progress(selected_quiz: str):
    engine = get_engine_for(selected_quiz)
    order = list(range(engine.total_questions))
    if RANDOMIZE_ORDER:
        random.shuffle(order)
    session["order"] = order
    session["index"] = 0
    session["score_by_player"] = {"p0": 0}
    session["answered"] = {}
    session["selected_quiz"] = selected_quiz


def _init_session():
    if "selected_quiz" not in session:
        get_selected_quiz()
    if "index" not in session:
        _reset_progress(session["selected_quiz"])


def _current_question() -> tuple[bool, Dict[str, Any]]:
    """セッションに基づき現在の問題と状態を返す。finishedの場合は第二戻り値に finished 情報を含む。"""
    _init_session()
    selected_quiz = get_selected_quiz()
    engine = get_engine_for(selected_quiz)
    order = session.get("order", list(range(engine.total_questions)))
    idx = session.get("index", 0)
    total = engine.total_questions
    if idx >= total:
        return True, {
            "finished": True,
            "total": total,
            "score": session.get("score_by_player", {}).get("p0", 0),
            "players": {pid: {"score": sc} for pid, sc in session.get("score_by_player", {}).items()},
            "selected_quiz": selected_quiz,
        }
    question = engine.get_question(order[idx])
    return False, {
        "id": question.id,
        "question": question.question,
        "choices": question.choices,
        "index": idx + 1,
        "total": total,
        "score": session.get("score_by_player", {}).get("p0", 0),
        "players": {pid: {"score": sc} for pid, sc in session.get("score_by_player", {}).items()},
        "selected_quiz": selected_quiz,
    }


@app.route("/quiz")
def quiz_page():
    _init_session()
    return render_template("quiz.html")


@app.route("/overlay")
def overlay_page():
    _init_session()
    return render_template("overlay.html")


@app.route("/api/question", methods=["GET"])
def api_question():
    finished, payload = _current_question()
    if finished:
        return jsonify(payload)
    return jsonify(payload)


@app.route("/api/answer", methods=["POST"])
def api_answer():
    _init_session()
    selected_quiz = get_selected_quiz()
    engine = get_engine_for(selected_quiz)
    order = session.get("order", list(range(engine.total_questions)))
    idx = session.get("index", 0)
    if idx >= len(order):
        return jsonify({"error": "全ての問題が終了しました"}), 400
    current_question = engine.get_question(order[idx])

    data = request.get_json(silent=True) or {}
    choice_index = data.get("choice_index")
    question_id = data.get("id")
    player_id = data.get("player_id") or "p0"

    if not isinstance(choice_index, int):
        return jsonify({"error": "choice_index は整数で指定してください"}), 400
    if choice_index not in (1, 2, 3, 4):
        return jsonify({"error": "choice_index は 1-4 の範囲で指定してください"}), 400
    if not question_id:
        return jsonify({"error": "id は必須です"}), 400
    if question_id != current_question.id:
        return jsonify({"error": "現在の問題IDと一致していません"}), 400

    try:
        correct_choice = engine.correct_choice(question_id)
        is_correct = engine.check_answer(question_id, choice_index)
    except (KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400

    answered = session.get("answered", {})
    player_scores = session.get("score_by_player", {"p0": 0})
    already_answered = answered.get(question_id)

    if player_id not in player_scores:
        player_scores[player_id] = 0

    if not already_answered and is_correct:
        player_scores[player_id] += 1
    answered[question_id] = True

    session["answered"] = answered
    session["score_by_player"] = player_scores

    return jsonify(
        {
            "correct": is_correct,
            "correct_choice": correct_choice,
            "explanation": engine.get_by_id(question_id).explanation,
            "score": player_scores.get("p0", 0),
            "player_score": player_scores[player_id],
            "selected_quiz": selected_quiz,
        }
    )


@app.route("/api/next", methods=["POST"])
def api_next():
    _init_session()
    selected_quiz = get_selected_quiz()
    engine = get_engine_for(selected_quiz)
    order = session.get("order", list(range(engine.total_questions)))
    idx = session.get("index", 0)
    if idx < len(order):
        session["index"] = idx + 1
    return jsonify({"ok": True})


@app.route("/api/quizzes", methods=["GET"])
def api_quizzes():
    try:
        files = list_quiz_files()
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    selected = session.get("selected_quiz")
    return jsonify({"files": files, "selected": selected})


@app.route("/api/select_quiz", methods=["POST"])
def api_select_quiz():
    data = request.get_json(silent=True) or {}
    filename = data.get("filename")
    if not filename or not isinstance(filename, str):
        return jsonify({"error": "filename を指定してください"}), 400
    try:
        engine = get_engine_for(filename)
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 400
    _reset_progress(filename)
    return jsonify({"ok": True, "selected": filename, "total": engine.total_questions})


@app.route("/")
def index():
    return quiz_page()


if __name__ == "__main__":
    app.run(debug=True, port=5200)
