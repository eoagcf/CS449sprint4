import unittest
from game import ManualGame, AutomatedGame, Game
from board import Board


# ==============================================================
# BOARD TESTS
# ==============================================================

class TestBoard(unittest.TestCase):

    def test_english_board_center_empty(self):
        """Center cell starts empty on English board."""
        board = Board(7, "English")
        self.assertEqual(board.get_cell(3, 3), 0)

    def test_diamond_board_center_empty(self):
        """Center cell starts empty on Diamond board."""
        board = Board(7, "Diamond")
        self.assertEqual(board.get_cell(3, 3), 0)

    def test_hexagon_board_center_empty(self):
        """Center cell starts empty on Hexagon board."""
        board = Board(7, "Hexagon")
        self.assertEqual(board.get_cell(3, 3), 0)

    def test_english_corners_are_invalid(self):
        """Corner cells are off the English board (value -1)."""
        board = Board(7, "English")
        self.assertEqual(board.get_cell(0, 0), -1)
        self.assertEqual(board.get_cell(0, 6), -1)
        self.assertEqual(board.get_cell(6, 0), -1)
        self.assertEqual(board.get_cell(6, 6), -1)

    def test_out_of_bounds_returns_minus_one(self):
        """Accessing outside the grid returns -1."""
        board = Board(7, "English")
        self.assertEqual(board.get_cell(-1, 0), -1)
        self.assertEqual(board.get_cell(0, 99), -1)


# ==============================================================
# MANUAL GAME TESTS
# ==============================================================

class TestManualGame(unittest.TestCase):

    def setUp(self):
        """Fresh English ManualGame before each test."""
        self.game = ManualGame(7, "English")

    # --- Inheritance ---

    def test_manual_game_is_instance_of_game(self):
        """ManualGame is a subclass of Game."""
        self.assertIsInstance(self.game, Game)

    # --- New game ---

    def test_new_game_resets_board(self):
        """New game restores center cell to empty."""
        self.game.make_move(3, 1, 3, 3)
        self.game.new_game()
        self.assertEqual(self.game.board.get_cell(3, 3), 0)

    def test_new_game_changes_board_type(self):
        """New game can switch board type."""
        self.game.new_game(board_type="Diamond")
        self.assertEqual(self.game.board_type, "Diamond")

    def test_new_game_changes_board_size(self):
        """New game can change board size."""
        self.game.new_game(size=9)
        self.assertEqual(self.game.size, 9)

    # --- Valid moves ---

    def test_valid_horizontal_move_right(self):
        """Peg can jump right over an adjacent peg into an empty hole."""
        result = self.game.make_move(3, 1, 3, 3)
        self.assertTrue(result)
        self.assertEqual(self.game.board.get_cell(3, 1), 0)  # source empty
        self.assertEqual(self.game.board.get_cell(3, 2), 0)  # jumped peg removed
        self.assertEqual(self.game.board.get_cell(3, 3), 1)  # destination filled

    def test_valid_horizontal_move_left(self):
        """Peg can jump left into the starting center hole."""
        # (3,3) starts empty — so (3,5) can jump left over (3,4) into (3,3)
        result = self.game.make_move(3, 5, 3, 3)
        self.assertTrue(result)
        self.assertEqual(self.game.board.get_cell(3, 5), 0)  # source empty
        self.assertEqual(self.game.board.get_cell(3, 4), 0)  # jumped peg removed
        self.assertEqual(self.game.board.get_cell(3, 3), 1)  # destination filled

    def test_valid_vertical_move_down(self):
        """Peg can jump downward."""
        result = self.game.make_move(1, 3, 3, 3)
        self.assertTrue(result)
        self.assertEqual(self.game.board.get_cell(1, 3), 0)
        self.assertEqual(self.game.board.get_cell(2, 3), 0)
        self.assertEqual(self.game.board.get_cell(3, 3), 1)

    def test_valid_vertical_move_up(self):
        """Peg can jump upward into the starting center hole."""
        # (3,3) starts empty — so (5,3) can jump up over (4,3) into (3,3)
        result = self.game.make_move(5, 3, 3, 3)
        self.assertTrue(result)
        self.assertEqual(self.game.board.get_cell(5, 3), 0)  # source empty
        self.assertEqual(self.game.board.get_cell(4, 3), 0)  # jumped peg removed
        self.assertEqual(self.game.board.get_cell(3, 3), 1)  # destination filled

    # --- Invalid moves ---

    def test_move_from_empty_cell_rejected(self):
        """Cannot move from an empty cell."""
        result = self.game.make_move(3, 3, 3, 5)  # (3,3) starts empty
        self.assertFalse(result)

    def test_move_to_occupied_cell_rejected(self):
        """Cannot move to a cell that already has a peg."""
        result = self.game.make_move(3, 1, 3, 3)
        # Now try to move another peg to (3,2) which has a peg
        result2 = self.game.make_move(3, 0, 3, 2)
        self.assertFalse(result2)

    def test_move_only_one_step_rejected(self):
        """A move of only one step is invalid."""
        result = self.game.make_move(3, 2, 3, 3)
        self.assertFalse(result)

    def test_move_three_steps_rejected(self):
        """A move of three steps is invalid."""
        result = self.game.make_move(3, 0, 3, 3)
        self.assertFalse(result)

    def test_board_unchanged_after_invalid_move(self):
        """Board state does not change after an invalid move."""
        before = [
            [self.game.board.get_cell(r, c) for c in range(7)]
            for r in range(7)
        ]
        self.game.make_move(3, 3, 3, 5)  # invalid — source is empty
        after = [
            [self.game.board.get_cell(r, c) for c in range(7)]
            for r in range(7)
        ]
        self.assertEqual(before, after)

    # --- Game over and rating ---

    def test_game_not_over_at_start(self):
        """Game should not be over at the start."""
        self.assertFalse(self.game.is_game_over())

    def test_count_pegs_at_start(self):
        """English 7x7 board starts with 32 pegs (33 cells minus center)."""
        self.assertEqual(self.game.count_pegs(), 32)

    def test_count_pegs_decreases_after_move(self):
        """Each valid move removes one peg."""
        before = self.game.count_pegs()
        self.game.make_move(3, 1, 3, 3)
        self.assertEqual(self.game.count_pegs(), before - 1)

    def test_rating_outstanding(self):
        """Rating is Outstanding when 1 peg remains."""
        # Force board to have 1 peg
        for r in range(7):
            for c in range(7):
                if self.game.board.get_cell(r, c) == 1:
                    self.game.board.set_cell(r, c, 0)
        self.game.board.set_cell(3, 3, 1)
        self.assertEqual(self.game.get_rating(), "Outstanding")

    def test_rating_very_good(self):
        """Rating is Very Good when 2 pegs remain."""
        for r in range(7):
            for c in range(7):
                if self.game.board.get_cell(r, c) == 1:
                    self.game.board.set_cell(r, c, 0)
        self.game.board.set_cell(3, 3, 1)
        self.game.board.set_cell(3, 4, 1)
        self.assertEqual(self.game.get_rating(), "Very Good")

    def test_rating_good(self):
        """Rating is Good when 3 pegs remain."""
        for r in range(7):
            for c in range(7):
                if self.game.board.get_cell(r, c) == 1:
                    self.game.board.set_cell(r, c, 0)
        self.game.board.set_cell(3, 3, 1)
        self.game.board.set_cell(3, 4, 1)
        self.game.board.set_cell(3, 5, 1)
        self.assertEqual(self.game.get_rating(), "Good")

    def test_rating_average(self):
        """Rating is Average when 4 or more pegs remain."""
        self.assertEqual(self.game.get_rating(), "Average")

    # --- Randomize ---

    def test_randomize_changes_board(self):
        """Randomize produces a different board state than the start."""
        start_pegs = self.game.count_pegs()
        self.game.randomize()
        # After randomizing, some moves were made so peg count should differ
        self.assertNotEqual(self.game.count_pegs(), start_pegs)

    def test_randomize_board_still_valid(self):
        """After randomize, all cells are still -1, 0, or 1."""
        self.game.randomize()
        for r in range(7):
            for c in range(7):
                self.assertIn(self.game.board.get_cell(r, c), [-1, 0, 1])

    # --- Hexagon and Diamond boards ---

    def test_hexagon_board_valid_move(self):
        """A valid move works on a Hexagon board."""
        game = ManualGame(7, "Hexagon")
        result = game.make_move(3, 1, 3, 3)
        self.assertTrue(result)

    def test_diamond_board_valid_move(self):
        """A valid move works on a Diamond board."""
        game = ManualGame(7, "Diamond")
        result = game.make_move(3, 1, 3, 3)
        self.assertTrue(result)


# ==============================================================
# AUTOMATED GAME TESTS
# ==============================================================

class TestAutomatedGame(unittest.TestCase):

    def setUp(self):
        """Fresh English AutomatedGame before each test."""
        self.game = AutomatedGame(7, "English")

    # --- Inheritance ---

    def test_automated_game_is_instance_of_game(self):
        """AutomatedGame is a subclass of Game."""
        self.assertIsInstance(self.game, Game)

    # --- Make move ---

    def test_make_move_returns_true_when_moves_available(self):
        """make_move() returns True at the start of the game."""
        result = self.game.make_move()
        self.assertTrue(result)

    def test_make_move_reduces_peg_count(self):
        """Each automated move removes exactly one peg."""
        before = self.game.count_pegs()
        self.game.make_move()
        self.assertEqual(self.game.count_pegs(), before - 1)

    def test_make_move_keeps_board_valid(self):
        """After each automated move, all cells are still -1, 0, or 1."""
        self.game.make_move()
        for r in range(7):
            for c in range(7):
                self.assertIn(self.game.board.get_cell(r, c), [-1, 0, 1])

    def test_make_move_returns_false_when_no_moves(self):
        """make_move() returns False when no valid moves remain."""
        # Clear the board to force no moves
        for r in range(7):
            for c in range(7):
                if self.game.board.get_cell(r, c) == 1:
                    self.game.board.set_cell(r, c, 0)
        result = self.game.make_move()
        self.assertFalse(result)

    # --- Autoplay ---

    def test_autoplay_ends_game(self):
        """autoplay() plays until no more moves are possible."""
        self.game.autoplay()
        self.assertTrue(self.game.is_game_over())

    def test_autoplay_step_callback_called(self):
        """autoplay() calls step_callback after every move."""
        call_count = []

        def callback(game):
            call_count.append(1)

        self.game.autoplay(step_callback=callback)
        # Callback should have been called once per move
        # Total moves = 32 - final peg count
        expected = 32 - self.game.count_pegs()
        self.assertEqual(len(call_count), expected)

    def test_autoplay_on_hexagon_board(self):
        """autoplay() works on a Hexagon board."""
        game = AutomatedGame(7, "Hexagon")
        game.autoplay()
        self.assertTrue(game.is_game_over())

    def test_autoplay_on_diamond_board(self):
        """autoplay() works on a Diamond board."""
        game = AutomatedGame(7, "Diamond")
        game.autoplay()
        self.assertTrue(game.is_game_over())

    # --- Game over ---

    def test_game_not_over_at_start(self):
        """Automated game should not be over at the start."""
        self.assertFalse(self.game.is_game_over())

    def test_new_game_resets_automated_board(self):
        """new_game() resets the automated board to starting state."""
        self.game.make_move()
        self.game.new_game()
        self.assertEqual(self.game.count_pegs(), 32)


# ==============================================================
# RUN ALL TESTS
# ==============================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)