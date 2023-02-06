class SearchResult:
    """
    many: boolean for whether search result has many elements (list type)
    """
    def __init__(self, data,  many: bool = True) -> None:
        self.data = data
        self._many = many

    def search_was_empty(self) -> bool:
        return self.data is None or len(self.data) == 0

    def result(self):
        if self.search_was_empty():
            raise ValueError("No results")
        else:
            if self._many:
                return self.data
            else:
                return self.data[0]
