class Breaker:
    """Breaker class - prevents requests to external services from being made if the service is unreliable."""

    def __init__(self, callback):
        self.callback = callback
        self.window = []  # This will track the long term progress of requests.
        self.state = "Closed"  # Breaker state - if false, circuit is 'closed' and working - should be an enum I think.

    def __call__(self):
        try:
            if self.state == "Closed":
                return self.callback()
        except:
            # Logic for setting state 'window' ?
            pass
