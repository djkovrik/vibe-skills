class PreferenceComponent:
    def __init__(self) -> None:
        self._value: str | None = None

    def create_preference(self, value: str) -> None:
        if self._value is not None:
            raise ValueError("preference already exists")
        self._value = value

    def read_preference(self) -> str | None:
        return self._value

    def update_preference(self, value: str) -> None:
        if self._value is None:
            raise ValueError("preference does not exist")
        self._value = value

    def delete_preference(self) -> None:
        self._value = None
