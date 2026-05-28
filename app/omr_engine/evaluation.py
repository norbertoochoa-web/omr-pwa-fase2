from app.omr_engine.logger import logger


class EvaluationEngine:
    def __init__(self, evaluation_data: dict):
        self.evaluation_data = evaluation_data
        self.options = evaluation_data.get("options", {})
        self.marking_schemes = evaluation_data.get("marking_schemes", {})

        self.questions_in_order = self.options.get("questions_in_order", [])
        self.answers_in_order = self.options.get("answers_in_order", [])

        self._answer_map = {}
        for q, a in zip(self.questions_in_order, self.answers_in_order):
            self._answer_map[q] = a

        self.default_scheme = self.marking_schemes.get("DEFAULT", {
            "correct": 1, "incorrect": 0, "unmarked": 0
        })

    def evaluate(self, omr_response: dict) -> tuple:
        score = 0.0
        verdicts = {}

        for question in self.questions_in_order:
            marked = omr_response.get(question, "")
            correct_answer = self._answer_map.get(question, "")

            if marked == "" or marked is None:
                verdicts[question] = "Unmarked"
                score += self.default_scheme.get("unmarked", 0)
            elif marked == correct_answer:
                verdicts[question] = "Correct"
                score += self.default_scheme.get("correct", 1)
            else:
                # Check for multi-marked
                if len(marked) > 1:
                    verdicts[question] = "Incorrect"
                else:
                    verdicts[question] = "Incorrect"
                score += self.default_scheme.get("incorrect", 0)

        return score, verdicts
