import random
from board import Board


class Game:
    """Base class for all game modes. Holds shared logic."""

    def __init__(self, size=7, board_type="English"):
        self.size = size
        self.board_type = board_type
        self.board = Board(size, board_type)

    def new_game(self, size=None, board_type=None):
        """Reset the board with optional new size/type."""
        if size is not None:
            self.size = size
        if board_type is not None:
            self.board_type = board_type
        self.board = Board(self.size, self.board_type)

    def is_valid_move(self, r1, c1, r2, c2):
        """Check if a move from (r1,c1) to (r2,c2) is legal."""
        mid_r = (r1 + r2) // 2
        mid_c = (c1 + c2) // 2

        if self.board.get_cell(r1, c1) != 1:
            return False
        if self.board.get_cell(r2, c2) != 0:
            return False
        if self.board.get_cell(mid_r, mid_c) != 1:
            return False

        # Orthogonal moves only (horizontal or vertical, exactly 2 steps)
        if abs(r1 - r2) == 2 and c1 == c2:
            return True
        if abs(c1 - c2) == 2 and r1 == r2:
            return True

        return False

    def get_all_valid_moves(self):
        """Return a list of all valid moves as (r1, c1, r2, c2) tuples."""
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    r2, c2 = r + dr, c + dc
                    if self.is_valid_move(r, c, r2, c2):
                        moves.append((r, c, r2, c2))
        return moves

    def is_game_over(self):
        """Game is over when no valid moves remain."""
        return len(self.get_all_valid_moves()) == 0

    def count_pegs(self):
        """Count how many pegs are on the board."""
        count = 0
        for r in range(self.size):
            for c in range(self.size):
                if self.board.get_cell(r, c) == 1:
                    count += 1
        return count

    def get_rating(self):
        """Return a performance rating based on pegs remaining."""
        pegs = self.count_pegs()
        if pegs == 1:
            return "Outstanding"
        elif pegs == 2:
            return "Very Good"
        elif pegs == 3:
            return "Good"
        else:
            return "Average"


class ManualGame(Game):
    """Game mode where a human player makes moves."""

    def __init__(self, size=7, board_type="English"):
        super().__init__(size, board_type)

    def make_move(self, r1, c1, r2, c2):
        """Attempt a move. Returns True if successful, False if invalid."""
        if not self.is_valid_move(r1, c1, r2, c2):
            return False

        mid_r = (r1 + r2) // 2
        mid_c = (c1 + c2) // 2

        self.board.set_cell(r1, c1, 0)
        self.board.set_cell(mid_r, mid_c, 0)
        self.board.set_cell(r2, c2, 1)

        return True

    def randomize(self):
        """
        Randomize the board by making a series of random valid moves
        from the starting position. This creates a reachable board state.
        """
        self.new_game()
        moves = self.get_all_valid_moves()
        num_moves = random.randint(5, 20)

        for _ in range(num_moves):
            if not moves:
                break
            r1, c1, r2, c2 = random.choice(moves)
            self.make_move(r1, c1, r2, c2)
            moves = self.get_all_valid_moves()


class AutomatedGame(Game):
    """Game mode where the computer makes moves automatically."""

    def __init__(self, size=7, board_type="English"):
        super().__init__(size, board_type)

    def make_move(self):
        """
        Pick and execute a random valid move.
        Returns the move as (r1, c1, r2, c2) if successful, or None if no moves exist.
        """
        moves = self.get_all_valid_moves()
        if not moves:
            return None  # No move possible — game over

        r1, c1, r2, c2 = random.choice(moves)
        mid_r = (r1 + r2) // 2
        mid_c = (c1 + c2) // 2

        self.board.set_cell(r1, c1, 0)
        self.board.set_cell(mid_r, mid_c, 0)
        self.board.set_cell(r2, c2, 1)

        return (r1, c1, r2, c2)  # Return coordinates so GUI can log the move

    def autoplay(self, step_callback=None):
        """
        Play the game to completion automatically.
        Optionally calls step_callback(game) after each move
        so the GUI can update the board in real time.
        """
        while not self.is_game_over():
            self.make_move()
            if step_callback:
                step_callback(self)