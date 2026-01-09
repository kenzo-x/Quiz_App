from dataclasses import dataclass
from typing import List, Dict, Any

import pandas as pd


@dataclass
class Question:
    id: str
    question: str
    choices: List[str]
    answer: int  # 1-4
    explanation: str
    meta: Dict[str, Any] | None = None


class QuizEngine:
    def __init__(self, questions: List[Question]):
        if not questions:
            raise ValueError("クイズデータが空です")
        self._questions = questions
        self._index_by_id = {q.id: q for q in questions}

    @classmethod
    def load_from_excel(cls, path: str) -> "QuizEngine":
        try:
            df = pd.read_excel(path)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Excelファイルが見つかりません: {path}") from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Excel読み込みに失敗しました: {exc}") from exc

        return cls._from_dataframe(df)

    @classmethod
    def load_from_csv(cls, path: str, *, encoding: str | None = None) -> "QuizEngine":
        try:
            df = pd.read_csv(path, encoding=encoding)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"CSVファイルが見つかりません: {path}") from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"CSV読み込みに失敗しました: {exc}") from exc

        return cls._from_dataframe(df)

    @classmethod
    def _from_dataframe(cls, df: pd.DataFrame) -> "QuizEngine":
        required_cols = ["id", "question", "choice1", "choice2", "choice3", "choice4", "answer", "explanation"]

        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"必要な列が欠けています: {', '.join(missing)}")

        questions: List[Question] = []
        for idx, row in df.iterrows():
            try:
                if pd.isna(row["id"]):
                    raise ValueError("id が空です")
                if pd.isna(row["question"]):
                    raise ValueError("question が空です")
                if pd.isna(row["explanation"]):
                    raise ValueError("explanation が空です")

                qid = str(row["id"])
                question_text = str(row["question"])
                choices = []
                for i in range(1, 5):
                    val = row[f"choice{i}"]
                    if pd.isna(val):
                        raise ValueError(f"choice{i} が空です")
                    choices.append(str(val))
                answer_raw = row["answer"]
                if pd.isna(answer_raw):
                    raise ValueError("answer が空です")
                answer = int(answer_raw)
                if answer not in (1, 2, 3, 4):
                    raise ValueError("answer は 1-4 の整数である必要があります")
                explanation = str(row["explanation"])
                meta = {}
                for key in row.index:
                    if key not in required_cols:
                        meta[key] = row[key]
                questions.append(Question(qid, question_text, choices, answer, explanation, meta or None))
            except Exception as exc:
                raise ValueError(f"{idx + 1} 行目のデータが不正です: {exc}") from exc

        return cls(questions)

    @property
    def total_questions(self) -> int:
        return len(self._questions)

    def get_question(self, index: int) -> Question:
        if index < 0 or index >= len(self._questions):
            raise IndexError("指定されたインデックスの問題は存在しません")
        return self._questions[index]

    def check_answer(self, question_id: str, choice_index: int) -> bool:
        if choice_index not in (1, 2, 3, 4):
            raise ValueError("choice_index は 1-4 の整数である必要があります")
        question = self._index_by_id.get(question_id)
        if not question:
            raise KeyError(f"question_id が見つかりません: {question_id}")
        return question.answer == choice_index

    def correct_choice(self, question_id: str) -> int:
        question = self._index_by_id.get(question_id)
        if not question:
            raise KeyError(f"question_id が見つかりません: {question_id}")
        return question.answer

    def get_by_id(self, question_id: str) -> Question:
        question = self._index_by_id.get(question_id)
        if not question:
            raise KeyError(f"question_id が見つかりません: {question_id}")
        return question
