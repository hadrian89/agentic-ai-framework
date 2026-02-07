class InMemoryStore:

    STORE = {}

    @classmethod
    def get(cls, session_id):
        return cls.STORE.get(session_id, [])

    @classmethod
    def update(cls, session_id, message):
        if session_id not in cls.STORE:
            cls.STORE[session_id] = []
        cls.STORE[session_id].append(message)

