import tkinter as tk
from tkinter import messagebox
import threading
import time
from game import ManualGame, AutomatedGame
from recorder import GameRecorder


class PegSolitaireGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Peg Solitaire")

        # Game state
        self.game = None
        self.selected_peg = None
        self.game_mode = tk.StringVar(value="Manual")
        self.board_type_var = tk.StringVar(value="English")
        self.board_size_var = tk.StringVar(value="7")
        self.autoplay_running = False

        self.recorder = GameRecorder()
        self.recording_var = tk.BooleanVar(value=False)

        self._build_ui()
        self.start_new_game()

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Build all GUI widgets."""

        # ---- Top bar: board size ----
        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=6)

        tk.Label(top_frame, text="Board size:").pack(side="left")
        size_entry = tk.Entry(top_frame, textvariable=self.board_size_var, width=4)
        size_entry.pack(side="left", padx=4)

        # ---- Left panel: board type + game mode ----
        left_frame = tk.Frame(self.root)
        left_frame.grid(row=1, column=0, sticky="n", padx=10, pady=6)

        tk.Label(left_frame, text="Board Type", font=("", 10, "bold")).pack(anchor="w")
        for btype in ["English", "Hexagon", "Diamond"]:
            tk.Radiobutton(
                left_frame,
                text=btype,
                variable=self.board_type_var,
                value=btype
            ).pack(anchor="w")

        tk.Label(left_frame, text="").pack()  # spacer

        tk.Label(left_frame, text="Game Mode", font=("", 10, "bold")).pack(anchor="w")
        for mode in ["Manual", "Automated"]:
            tk.Radiobutton(
                left_frame,
                text=mode,
                variable=self.game_mode,
                value=mode
            ).pack(anchor="w")

        # Record checkbox in left panel
        tk.Label(left_frame, text="").pack()  # spacer
        self.record_checkbox = tk.Checkbutton(
            left_frame,
            text="Record game",
            variable=self.recording_var,
            command=self.toggle_recording
        )
        self.record_checkbox.pack(anchor="w")

        # ---- Center: board canvas ----
        self.board_frame = tk.Frame(self.root)
        self.board_frame.grid(row=1, column=1, padx=10, pady=6)

        # ---- Right panel: buttons ----
        right_frame = tk.Frame(self.root)
        right_frame.grid(row=1, column=2, sticky="n", padx=10, pady=6)

        tk.Button(
            right_frame,
            text="New Game",
            width=10,
            command=self.start_new_game
        ).pack(pady=4)

        tk.Button(
            right_frame,
            text="Replay",
            width=10,
            command=self.replay_game
        ).pack(pady=4)

        self.autoplay_btn = tk.Button(
            right_frame,
            text="Autoplay",
            width=10,
            bg="lightgreen",
            command=self.start_autoplay
        )
        self.autoplay_btn.pack(pady=4)

        self.randomize_btn = tk.Button(
            right_frame,
            text="Randomize",
            width=10,
            bg="lightgreen",
            command=self.randomize_board
        )
        self.randomize_btn.pack(pady=4)

        # ---- Bottom: status label ----
        self.status_label = tk.Label(
            self.root,
            text="Welcome! Choose settings and press New Game.",
            wraplength=500
        )
        self.status_label.grid(row=2, column=0, columnspan=3, pady=8)

    # ------------------------------------------------------------------
    # GAME CONTROL
    # ------------------------------------------------------------------

    def start_new_game(self):
        """Start a new game using current settings."""
        self.autoplay_running = False
        self.selected_peg = None

        # Validate board size
        try:
            size = int(self.board_size_var.get())
            if size < 5 or size > 15 or size % 2 == 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Size",
                "Board size must be an odd number between 5 and 15."
            )
            self.board_size_var.set("7")
            return

        board_type = self.board_type_var.get()
        mode = self.game_mode.get()

        if mode == "Manual":
            self.game = ManualGame(size, board_type)
            self._set_button_states(manual=True)
            self.status_label.config(
                text=f"New Manual game: {board_type}, size {size}. Click a peg to start."
            )
        else:
            self.game = AutomatedGame(size, board_type)
            self._set_button_states(manual=False)
            self.status_label.config(
                text=f"New Automated game: {board_type}, size {size}. Press Autoplay."
            )

        if self.recorder.recording:
            self.recorder.log(f"NEW_GAME {size} {board_type} {mode}")

        self.draw_board()

    def toggle_recording(self):
        """Start or stop recording based on checkbox state."""
        if self.recording_var.get():
            self.recorder.start("game.txt")
            # Log the current game state so replaying starts from the right config
            if self.game is not None:
                size = self.game.board.size
                board_type = self.board_type_var.get()
                mode = self.game_mode.get()
                self.recorder.log(f"NEW_GAME {size} {board_type} {mode}")
            self.status_label.config(text="Recording started. Moves will be saved to game.txt.")
        else:
            self.recorder.stop()
            self.status_label.config(text="Recording stopped. File saved as game.txt.")

    def randomize_board(self):
        """Randomize the current manual game board."""
        if not isinstance(self.game, ManualGame):
            messagebox.showinfo("Info", "Randomize is only available in Manual mode.")
            return
        self.selected_peg = None
        self.game.randomize()

        if self.recorder.recording:
            self.recorder.log("RANDOMIZE")

        self.draw_board()
        self.status_label.config(text="Board randomized! Keep playing.")
        self._check_game_over()

    def start_autoplay(self):
        """Run the automated game step by step in a background thread."""
        if not isinstance(self.game, AutomatedGame):
            messagebox.showinfo("Info", "Autoplay is only available in Automated mode.")
            return
        if self.autoplay_running:
            return

        self.autoplay_running = True
        self.autoplay_btn.config(state="disabled")
        self.status_label.config(text="Autoplaying...")

        def run():
            while not self.game.is_game_over() and self.autoplay_running:
                move = self.game.make_move()  # returns (r1, c1, r2, c2) or None

                # Log the move if recording
                if self.recorder.recording and move is not None:
                    r1, c1, r2, c2 = move
                    self.recorder.log(f"MOVE {r1} {c1} {r2} {c2}")

                # Schedule GUI update on the main thread
                self.root.after(0, self.draw_board)
                time.sleep(0.4)

            self.autoplay_running = False
            self.root.after(0, self._show_game_over)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    # ------------------------------------------------------------------
    # REPLAY
    # ------------------------------------------------------------------

    def replay_game(self):
        """Replay a recorded game from game.txt."""
        try:
            with open("game.txt", "r") as f:
                commands = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            messagebox.showerror("Error", "No recorded game file (game.txt) found.")
            return

        # Stop any active recording so replay moves aren't re-logged
        if self.recording_var.get():
            self.recording_var.set(False)
            self.recorder.stop()

        self.autoplay_running = False
        self.selected_peg = None
        self.status_label.config(text="Replaying recorded game...")

        def run_replay():
            for command in commands:
                # Schedule each command on the main thread and wait
                self.root.after(0, lambda cmd=command: self._process_replay_command(cmd))
                time.sleep(0.7)
            self.root.after(0, lambda: self.status_label.config(text="Replay finished."))

        thread = threading.Thread(target=run_replay, daemon=True)
        thread.start()

    def _process_replay_command(self, command):
        """Process one replay command from the recorded file (runs on main thread)."""
        parts = command.split()
        if not parts:
            return
        if parts[0] == "RECORDING_STOPPED": # only new line
            return

        if parts[0] == "NEW_GAME":
            size = int(parts[1])
            board_type = parts[2]
            mode = parts[3]

            self.board_size_var.set(str(size))
            self.board_type_var.set(board_type)
            self.game_mode.set(mode)
            self.start_new_game()

        elif parts[0] == "MOVE":
            r1, c1, r2, c2 = map(int, parts[1:])

            if isinstance(self.game, ManualGame):
                self.game.make_move(r1, c1, r2, c2)

            elif isinstance(self.game, AutomatedGame):
                # Apply the move directly on the board
                mid_r = (r1 + r2) // 2
                mid_c = (c1 + c2) // 2
                self.game.board.set_cell(r1, c1, 0)
                self.game.board.set_cell(mid_r, mid_c, 0)
                self.game.board.set_cell(r2, c2, 1)

            self.draw_board()

        elif parts[0] == "RANDOMIZE":
            if isinstance(self.game, ManualGame):
                self.game.randomize()
            self.draw_board()

    # ------------------------------------------------------------------
    # BOARD DRAWING
    # ------------------------------------------------------------------

    def draw_board(self):
        """Redraw the entire board."""
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        for r in range(self.game.board.size):
            for c in range(self.game.board.size):
                value = self.game.board.get_cell(r, c)

                if value == -1:
                    # Empty padding cell (off the board shape)
                    tk.Label(
                        self.board_frame,
                        text=" ",
                        width=4,
                        height=2
                    ).grid(row=r, column=c, padx=1, pady=1)
                else:
                    text = "●" if value == 1 else "○"
                    is_selected = (self.selected_peg == (r, c))

                    btn = tk.Button(
                        self.board_frame,
                        text=text,
                        width=4,
                        height=2,
                        relief="sunken" if is_selected else "raised",
                        bg="yellow" if is_selected else None,
                        command=lambda row=r, col=c: self.handle_click(row, col)
                    )
                    btn.grid(row=r, column=c, padx=1, pady=1)

    # ------------------------------------------------------------------
    # CLICK HANDLING (Manual mode only)
    # ------------------------------------------------------------------

    def handle_click(self, row, col):
        """Handle a player click on the board."""
        if not isinstance(self.game, ManualGame):
            return

        value = self.game.board.get_cell(row, col)

        if self.selected_peg is None:
            # First click: select a peg
            if value == 1:
                self.selected_peg = (row, col)
                self.status_label.config(
                    text=f"Peg selected at ({row}, {col}). Now click a destination."
                )
                self.draw_board()
            else:
                self.status_label.config(text="Please click on a peg (●) first.")
        else:
            # Second click: attempt the move
            from_row, from_col = self.selected_peg

            if (row, col) == (from_row, from_col):
                # Clicked same peg — deselect
                self.selected_peg = None
                self.status_label.config(text="Deselected. Click a peg to start.")
                self.draw_board()
                return

            moved = self.game.make_move(from_row, from_col, row, col)
            self.selected_peg = None

            if moved:
                if self.recorder.recording:
                    self.recorder.log(f"MOVE {from_row} {from_col} {row} {col}")

                self.status_label.config(
                    text=f"Moved from ({from_row}, {from_col}) to ({row}, {col})."
                )
                self.draw_board()
                self._check_game_over()
            else:
                self.status_label.config(
                    text="Invalid move. Click a peg to try again."
                )
                self.draw_board()

    # ------------------------------------------------------------------
    # GAME OVER
    # ------------------------------------------------------------------

    def _check_game_over(self):
        """Check if the manual game is over and show result if so."""
        if self.game.is_game_over():
            self._show_game_over()

    def _show_game_over(self):
        """Display the game over message with rating."""
        pegs = self.game.count_pegs()
        rating = self.game.get_rating()
        self.status_label.config(
            text=f"Game Over! Pegs remaining: {pegs} — Rating: {rating}"
        )
        messagebox.showinfo(
            "Game Over",
            f"No more moves possible!\n\nPegs remaining: {pegs}\nRating: {rating}"
        )

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _set_button_states(self, manual: bool):
        """Enable/disable buttons based on game mode."""
        self.randomize_btn.config(state="normal" if manual else "disabled")
        self.autoplay_btn.config(state="disabled" if manual else "normal")