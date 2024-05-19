class Gender:
    def __init__(self, gender):
        if gender not in {"man", "woman"}:
            raise ValueError("Invalid gender")
        self.gender = gender

    @property
    def name(self) -> str:
        return "男性" if self.gender == "man" else "女性"
