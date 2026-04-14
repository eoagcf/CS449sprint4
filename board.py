class Board:
    def __init__(self, size=7, board_type="English"):
        self.size = size
        self.board_type = board_type
        self.grid = self.create_board()

    def create_board(self):
        grid = [[-1 for _ in range(self.size)] for _ in range(self.size)]
        mid = self.size // 2

        if self.board_type == "English":
            third = self.size // 3
            for r in range(self.size):
                for c in range(self.size):
                    if (third <= r <= self.size - third - 1) or \
                       (third <= c <= self.size - third - 1):
                        grid[r][c] = 1

        elif self.board_type == "Diamond":
            for r in range(self.size):
                for c in range(self.size):
                    if abs(r - mid) + abs(c - mid) <= mid:
                        grid[r][c] = 1

        elif self.board_type == "Hexagon":
            playable_counts = [3, 5, 7, 7, 7, 5, 3]

            for r in range(self.size):
                count = playable_counts[r]
                start_col = (self.size - count) // 2

                for c in range(start_col, start_col + count):
                    grid[r][c] = 1

        else:
            # Default to English
            third = self.size // 3
            for r in range(self.size):
                for c in range(self.size):
                    if (third <= r <= self.size - third - 1) or \
                       (third <= c <= self.size - third - 1):
                        grid[r][c] = 1

        # Center hole is always empty
        grid[mid][mid] = 0
        return grid

    def get_cell(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row][col]
        return -1

    def set_cell(self, row, col, value):
        if 0 <= row < self.size and 0 <= col < self.size:
            self.grid[row][col] = value