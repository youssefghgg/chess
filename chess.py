import tkinter as tk
from PIL import Image, ImageTk
import os


class ChessPiece:
    def __init__(self, color, name):
        self.color = color
        self.name = name
        self.has_moved = False
        self.en_passant_vulnerable = False


class ChessGame:
    def __init__(self, root, main_menu):
        self.root = root
        self.main_menu = main_menu
        self.root.title("Chess Game")

        # Initialize piece images dictionary
        self.piece_images = {
            "white_pawn": "♙", "white_rook": "♖", "white_knight": "♘",
            "white_bishop": "♗", "white_queen": "♕", "white_king": "♔",
            "black_pawn": "♟", "black_rook": "♜", "black_knight": "♞",
            "black_bishop": "♝", "black_queen": "♛", "black_king": "♚"
        }

        # Create a frame for the game content (only once)
        self.game_container = tk.Frame(self.root, bg='#2C3E50')
        self.game_container.pack(expand=True, fill='both', padx=20, pady=20)

        # Initialize game components
        self.selected_piece = None
        self.current_player = "white"
        self.last_move = None

        # Add a return to menu button
        self.menu_button = tk.Button(self.game_container,
                                     text="Return to Menu",
                                     command=self.return_to_menu,
                                     font=('Helvetica', 12),
                                     bg='#34495E',
                                     fg='white',
                                     activebackground='#2C3E50',
                                     activeforeground='white',
                                     bd=0,
                                     cursor='hand2')
        self.menu_button.pack(pady=(0, 10))

        # Create and pack the turn indicator
        self.turn_label = tk.Label(self.game_container,
                                   text="White's turn",
                                   font=("Helvetica", 16),
                                   bg='#2C3E50',
                                   fg='white')
        self.turn_label.pack(pady=10)

        # Create the chess board
        self.board_size = 8
        self.cell_size = 60
        self.canvas_size = self.board_size * self.cell_size

        self.canvas = tk.Canvas(self.game_container,
                                width=self.canvas_size,
                                height=self.canvas_size,
                                bg='#ECF0F1')
        self.canvas.pack(pady=20)

        # Initialize the game
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.create_pieces()
        self.draw_board()

        # Bind click event
        self.canvas.bind('<Button-1>', self.on_square_click)
    def load_pieces(self):
        piece_files = {
            "white_pawn": "♙", "white_rook": "♖", "white_knight": "♘",
            "white_bishop": "♗", "white_queen": "♕", "white_king": "♔",
            "black_pawn": "♟", "black_rook": "♜", "black_knight": "♞",
            "black_bishop": "♝", "black_queen": "♛", "black_king": "♚"
        }

        for piece_name, symbol in piece_files.items():
            color = piece_name.split('_')[0]
            self.piece_images[piece_name] = symbol

    def create_pieces(self):
        # Add pawns - switched positions
        for col in range(self.board_size):
            self.board[1][col] = ChessPiece("black", "pawn")  # Changed to black
            self.board[6][col] = ChessPiece("white", "pawn")  # Changed to white

        # Add other pieces - switched colors
        piece_order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        for col, piece_name in enumerate(piece_order):
            self.board[0][col] = ChessPiece("black", piece_name)  # Changed to black
            self.board[7][col] = ChessPiece("white", piece_name)  # Changed to white

    def return_to_menu(self):
        self.root.destroy()  # Close game window
        self.main_menu.root.deiconify()  # Show main menu

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Alternate colors for squares
                fill = "#DDB88C" if (row + col) % 2 == 0 else "#A66D4F"

                # Highlight selected piece's square
                if (self.selected_piece and
                        self.selected_piece[0] == row and
                        self.selected_piece[1] == col):
                    fill = "#AAD794"  # Highlight color

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")

                # Draw piece if present
                piece = self.board[row][col]
                if piece:
                    piece_key = f"{piece.color}_{piece.name}"
                    self.canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text=self.piece_images[piece_key],
                        font=("Arial", 36),
                        fill="white" if piece.color == "white" else "black"
                    )
        if self.selected_piece:
            row, col = self.selected_piece
            piece = self.board[row][col]
            if piece and piece.name == "king" and not piece.has_moved:
                if self.is_valid_castling((row, col), (row, col + 2)):  # Kingside
                    x = (col + 2) * self.cell_size
                    y = row * self.cell_size
                    self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size,
                                                 outline="yellow", width=2)
                if self.is_valid_castling((row, col), (row, col - 2)):  # Queenside
                    x = (col - 2) * self.cell_size
                    y = row * self.cell_size
                    self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size,
                                                 outline="yellow", width=2)

    def is_valid_castling(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        king = self.board[start_row][start_col]

        if king.has_moved:
            return False

        # Determine rook position and target squares
        if end_col > start_col:  # Kingside castling
            rook_col = 7
            path_cols = [5, 6]  # Squares that must be empty
        else:  # Queenside castling
            rook_col = 0
            path_cols = [1, 2, 3]  # Squares that must be empty

        # Check if rook is in position and hasn't moved
        rook = self.board[start_row][rook_col]
        if not rook or rook.name != "rook" or rook.has_moved:
            return False

        # Check if squares between king and rook are empty
        for col in path_cols:
            if self.board[start_row][col] is not None:
                return False

        return True

    def move_piece(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        piece = self.board[start_row][start_col]

        # Check if we're capturing a king
        target_piece = self.board[end_row][end_col]
        game_over = target_piece and target_piece.name == "king"

        # Reset en passant vulnerability for all pawns
        for row in self.board:
            for p in row:
                if p and p.name == "pawn":
                    p.en_passant_vulnerable = False

        # Handle castling
        if piece.name == "king" and abs(end_col - start_col) == 2:
            # Move rook
            if end_col > start_col:  # Kingside castling
                rook = self.board[start_row][7]
                self.board[start_row][5] = rook  # Move rook to F1/F8
                self.board[start_row][7] = None
            else:  # Queenside castling
                rook = self.board[start_row][0]
                self.board[start_row][3] = rook  # Move rook to D1/D8
                self.board[start_row][0] = None
            if rook:
                rook.has_moved = True

        # Handle en passant capture
        if piece.name == "pawn" and abs(start_col - end_col) == 1 and not self.board[end_row][end_col]:
            self.board[start_row][end_col] = None

        # Set en passant vulnerability for two-square pawn moves
        if piece.name == "pawn" and abs(start_row - end_row) == 2:
            piece.en_passant_vulnerable = True

        # Store last move
        self.last_move = (start, end)

        # Move piece
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        piece.has_moved = True

        # Check for pawn promotion
        if piece.name == "pawn":
            if (piece.color == "white" and end_row == 0) or \
                    (piece.color == "black" and end_row == 7):
                self.promote_pawn(end_row, end_col)

        # Check for game over
        if game_over:
            self.game_over(piece.color)

    def on_square_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if self.selected_piece is None:
            # Select piece
            piece = self.board[row][col]
            if piece and piece.color == self.current_player:
                self.selected_piece = (row, col)
                self.draw_board()
        else:
            # Move piece
            if self.is_valid_move(self.selected_piece, (row, col)):
                self.move_piece(self.selected_piece, (row, col))
                self.current_player = "black" if self.current_player == "white" else "white"
                self.turn_label.config(text=f"{self.current_player.capitalize()}'s turn")
            self.selected_piece = None
            self.draw_board()

    def is_valid_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        piece = self.board[start_row][start_col]
        target = self.board[end_row][end_col]

        # Can't capture own pieces
        if target and target.color == piece.color:
            return False

        # Check castling
        if piece.name == "king" and not piece.has_moved:
            if abs(end_col - start_col) == 2:
                return self.is_valid_castling(start, end)

        # Basic movement rules for each piece
        if piece.name == "pawn":
            if piece.color == "white":
                # Normal pawn moves
                if start_col == end_col and not target:
                    if end_row == start_row - 1:
                        return True
                    if not piece.has_moved and end_row == start_row - 2:
                        return True
                # Captures (including en passant)
                if abs(start_col - end_col) == 1 and end_row == start_row - 1:
                    # Normal capture
                    if target:
                        return True
                    # En passant
                    if self.last_move and self.board[start_row][end_col] and \
                            self.board[start_row][end_col].en_passant_vulnerable:
                        return True
                    return False
            else:  # Black pawn
                if start_col == end_col and not target:
                    if end_row == start_row + 1:
                        return True
                    if not piece.has_moved and end_row == start_row + 2:
                        return True
                if abs(start_col - end_col) == 1 and end_row == start_row + 1:
                    if target:
                        return True
                    if self.last_move and self.board[start_row][end_col] and \
                            self.board[start_row][end_col].en_passant_vulnerable:
                        return True
                    return False

        # Basic movement rules for each piece
        if piece.name == "pawn":
            if piece.color == "white":  # White pawns now move up (decreasing row)
                if start_col == end_col and not target:  # Moving forward
                    if end_row == start_row - 1:  # Changed from + to -
                        return True
                    if not piece.has_moved and end_row == start_row - 2:  # Changed from + to -
                        return True
                if abs(start_col - end_col) == 1 and end_row == start_row - 1:  # Changed from + to -
                    return target is not None
            else:  # Black pawns now move down (increasing row)
                if start_col == end_col and not target:
                    if end_row == start_row + 1:  # Changed from - to +
                        return True
                    if not piece.has_moved and end_row == start_row + 2:  # Changed from - to +
                        return True
                if abs(start_col - end_col) == 1 and end_row == start_row + 1:  # Changed from - to +
                    return target is not None

        # Rest of the movement rules remain the same
        elif piece.name == "rook":
            return start_row == end_row or start_col == end_col

        elif piece.name == "knight":
            row_diff = abs(start_row - end_row)
            col_diff = abs(start_col - end_col)
            return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

        elif piece.name == "bishop":
            return abs(start_row - end_row) == abs(start_col - end_col)

        elif piece.name == "queen":
            return (start_row == end_row or
                    start_col == end_col or
                    abs(start_row - end_row) == abs(start_col - end_col))

        elif piece.name == "king":
            return abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1

        return False

    def promote_pawn(self, row, col):
        # Create promotion window
        promotion_window = tk.Toplevel(self.root)
        promotion_window.title("Pawn Promotion")
        promotion_window.geometry("300x100")

        pieces = ["queen", "rook", "bishop", "knight"]

        def promote_to(piece_name):
            self.board[row][col] = ChessPiece(self.board[row][col].color, piece_name)
            promotion_window.destroy()
            self.draw_board()

        # Create buttons for each piece option
        for i, piece in enumerate(pieces):
            tk.Button(promotion_window,
                      text=piece.capitalize(),
                      command=lambda p=piece: promote_to(p)).pack(side=tk.LEFT, padx=10, pady=20)

    def check_game_over(self):
        # Count kings
        white_king = black_king = False
        for row in self.board:
            for piece in row:
                if piece and piece.name == "king":
                    if piece.color == "white":
                        white_king = True
                    else:
                        black_king = True

        if not white_king:
            self.game_over("Black")
        elif not black_king:
            self.game_over("White")

    def game_over(self, winner):
        game_over_window = tk.Toplevel(self.root)
        game_over_window.title("Game Over")
        game_over_window.geometry("300x200")

        game_over_window.transient(self.root)
        game_over_window.grab_set()

        game_over_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50))

        tk.Label(game_over_window,
                 text=f"{winner.capitalize()} Wins!",
                 font=("Arial", 24, "bold")).pack(pady=20)

        def new_game():
            game_over_window.destroy()
            self.reset_game()

        def return_to_main():
            game_over_window.destroy()
            self.return_to_menu()

        tk.Button(game_over_window,
                  text="New Game",
                  font=("Arial", 12),
                  command=new_game).pack(pady=10)

        tk.Button(game_over_window,
                  text="Return to Menu",
                  font=("Arial", 12),
                  command=return_to_main).pack(pady=10)

    def reset_game(self):
        # Reset board and game state
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.create_pieces()
        self.current_player = "white"
        self.selected_piece = None
        self.last_move = None
        self.turn_label.config(text="White's turn")
        self.draw_board()

    def add_controls(self):
        # Create control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # New Game button
        tk.Button(control_frame,
                  text="New Game",
                  command=self.reset_game).pack(side=tk.LEFT, padx=10)

        # Undo button (you'll need to implement move history for this)
        tk.Button(control_frame,
                  text="Undo",
                  command=self.undo_move).pack(side=tk.LEFT, padx=10)

    def undo_move(self):
        # Implement move history and undo functionality
        pass


class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess Game")
        self.root.geometry("800x600")
        self.root.configure(bg='#2C3E50')  # Dark blue background

        self.game_window = None

        # Create main frame
        self.main_frame = tk.Frame(self.root, bg='#2C3E50')
        self.main_frame.pack(expand=True, fill='both')

        self.create_title()
        self.create_buttons()
        self.create_footer()

    def create_title(self):
        # Title Frame
        title_frame = tk.Frame(self.main_frame, bg='#2C3E50')
        title_frame.pack(pady=50)

        # Main Title
        title = tk.Label(title_frame,
                         text="♔ CHESS ♔",
                         font=('Helvetica', 60, 'bold'),
                         fg='#ECF0F1',  # Light text color
                         bg='#2C3E50')
        title.pack()

        # Subtitle
        subtitle = tk.Label(title_frame,
                            text="Classic Two-Player Strategy",
                            font=('Helvetica', 20),
                            fg='#3498DB',  # Blue accent color
                            bg='#2C3E50')
        subtitle.pack(pady=10)

    def create_buttons(self):
        # Buttons Frame
        button_frame = tk.Frame(self.main_frame, bg='#2C3E50')
        button_frame.pack(pady=30)

        # Button style
        button_style = {
            'font': ('Helvetica', 16, 'bold'),
            'width': 20,
            'height': 2,
            'bd': 0,
            'cursor': 'hand2'
        }

        # Play Button
        self.play_button = tk.Button(button_frame,
                                     text="Play Game",
                                     command=self.start_game,
                                     bg='#27AE60',  # Green
                                     fg='white',
                                     activebackground='#2ECC71',
                                     activeforeground='white',
                                     **button_style)
        self.play_button.pack(pady=10)

        # Quit Button
        self.quit_button = tk.Button(button_frame,
                                     text="Quit",
                                     command=self.root.quit,
                                     bg='#E74C3C',  # Red
                                     fg='white',
                                     activebackground='#C0392B',
                                     activeforeground='white',
                                     **button_style)
        self.quit_button.pack(pady=10)

        # Add hover effects
        for button in (self.play_button, self.quit_button):
            button.bind('<Enter>', self.on_enter)
            button.bind('<Leave>', self.on_leave)

    def create_footer(self):
        # Footer Frame
        footer_frame = tk.Frame(self.main_frame, bg='#2C3E50')
        footer_frame.pack(side='bottom', pady=20)

        # Footer text
        footer_text = tk.Label(footer_frame,
                               text="© Youssefghgg",
                               font=('Helvetica', 10),
                               fg='#95A5A6',  # Grey text
                               bg='#2C3E50')
        footer_text.pack()

    def on_enter(self, e):
        e.widget.config(relief='raised')

    def on_leave(self, e):
        e.widget.config(relief='flat')

    def start_game(self):
        self.root.withdraw()  # Hide main menu
        self.game_window = tk.Toplevel(self.root)
        self.game_window.title("Chess Game")
        self.game_window.geometry("800x800")  # Set proper size for game window
        self.game_window.configure(bg='#2C3E50')

        # Create and start the game
        chess_game = ChessGame(self.game_window, self)

        def on_game_window_close():
            self.game_window.destroy()
            self.game_window = None
            self.root.deiconify()

        self.game_window.protocol("WM_DELETE_WINDOW", on_game_window_close)

    def show_menu(self):
        if self.game_window:
            self.game_window.destroy()
            self.game_window = None
        self.root.deiconify()

    def run(self):
        self.root.mainloop()


# Modify your main execution to use the new menu
if __name__ == "__main__":
    menu = MainMenu()
    menu.run()