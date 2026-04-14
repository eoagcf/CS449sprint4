class GameRecorder:
    def __init__(self):
        self.file = None
        self.recording = False

    def start(self, filename="game.txt"):
        self.file = open(filename, "w")
        self.recording = True

    def stop(self):
        if self.file:
            self.file.write("RECORDING_STOPPED\n")  # ← only new line
            self.file.close()
        self.file = None
        self.recording = False

    def log(self, message):
        if self.recording and self.file:
            self.file.write(message + "\n")
            self.file.flush()