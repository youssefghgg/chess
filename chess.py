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

    def is_checkmate(self, color):
        """
        Check if the specified color is in checkmate
        """
        # If not in check, it's not checkmate
        if not self.is_in_check(color):
            return False

        # If in check, see if there are any valid moves that can get out of check
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for end_row in range(self.board_size):
                        for end_col in range(self.board_size):
                            if self.is_valid_move((row, col), (end_row, end_col)):
                                return False
        return True

    def return_to_menu(self):
        self.root.destroy()  # Close game window
        self.main_menu.root.deiconify()  # Show main menu

    def get_valid_moves(self, start):
        """
        Get all valid moves for a piece at the given position
        """
        if not start:
            return []

        start_row, start_col = start
        piece = self.board[start_row][start_col]
        if not piece:
            return []

        valid_moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.is_valid_move((start_row, start_col), (row, col)):
                    valid_moves.append((row, col))
        return valid_moves

    def draw_board(self):
        self.canvas.delete("all")

        # Draw squares
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

        # Draw move indicators
        if self.selected_piece:
            valid_moves = self.get_valid_moves(self.selected_piece)
            for move in valid_moves:
                row, col = move
                x = col * self.cell_size + self.cell_size // 2
                y = row * self.cell_size + self.cell_size // 2

                # Draw different indicators based on the type of move
                target_piece = self.board[row][col]
                if target_piece:
                    # Draw capture indicator (red circle)
                    self.canvas.create_oval(
                        x - self.cell_size // 3, y - self.cell_size // 3,
                        x + self.cell_size // 3, y + self.cell_size // 3,
                        outline="red", width=2
                    )
                else:
                    # Draw move indicator (green dot)
                    self.canvas.create_oval(
                        x - 5, y - 5, x + 5, y + 5,
                        fill="green", outline="darkgreen"
                    )

        # Highlight king if in check
        king_pos = self.find_king(self.current_player)
        if king_pos and self.is_in_check(self.current_player):
            row, col = king_pos
            x1 = col * self.cell_size
            y1 = row * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3)

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

    def move_puts_in_check(self, start, end):
        """
        Check if making this move would put or leave the player's king in check
        """
        start_row, start_col = start
        end_row, end_col = end

        # Store the current board state
        piece = self.board[start_row][start_col]
        target = self.board[end_row][end_col]

        # Temporarily make the move
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        # Check if the king is in check after the move
        in_check = self.is_in_check(piece.color)

        # Undo the move
        self.board[start_row][start_col] = piece
        self.board[end_row][end_col] = target

        return in_check

    def move_piece(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        piece = self.board[start_row][start_col]

        # Store last move
        self.last_move = (start, end)

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

        # Move piece
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        piece.has_moved = True

        # Check for pawn promotion
        if piece.name == "pawn":
            if (piece.color == "white" and end_row == 0) or \
                    (piece.color == "black" and end_row == 7):
                self.promote_pawn(end_row, end_col)

        # Check for checkmate on the opponent
        opponent_color = "black" if piece.color == "white" else "white"
        if self.is_checkmate(opponent_color):
            self.game_over(piece.color)

    def on_square_click(self, event):
        try:
            col = event.x // self.cell_size
            row = event.y // self.cell_size

            # Validate coordinates
            if not (0 <= row < self.board_size and 0 <= col < self.board_size):
                return

            if self.selected_piece is None:
                # Select piece
                piece = self.board[row][col]
                if piece and piece.color == self.current_player:
                    self.selected_piece = (row, col)
                    self.draw_board()
            else:
                # Move piece if valid
                if self.is_valid_move(self.selected_piece, (row, col)):
                    self.move_piece(self.selected_piece, (row, col))
                    # Switch players only if game isn't over
                    if not self.is_checkmate("white") and not self.is_checkmate("black"):
                        self.current_player = "black" if self.current_player == "white" else "white"
                        self.turn_label.config(text=f"{self.current_player.capitalize()}'s turn")
                self.selected_piece = None
                self.draw_board()
        except Exception as e:
            print(f"Error in on_square_click: {e}")
            self.selected_piece = None
            self.draw_board()

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        return not self.has_valid_moves(color)

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        return not self.has_valid_moves(color)

    def has_valid_moves(self, color):
        """
        Check if the specified color has any valid moves
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for r in range(self.board_size):
                        for c in range(self.board_size):
                            if self.is_valid_move((row, col), (r, c)):
                                return True
        return False

    def is_valid_basic_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end

        # Basic boundary checks
        if not (0 <= start_row < 8 and 0 <= start_col < 8 and 0 <= end_row < 8 and 0 <= end_col < 8):
            return False

        piece = self.board[start_row][start_col]
        target = self.board[end_row][end_col]

        # Must have a piece to move
        if not piece:
            return False

        # Can't capture own pieces
        if target and target.color == piece.color:
            return False

        # Calculate move deltas
        row_diff = end_row - start_row
        col_diff = end_col - start_col

        # Check piece-specific movement rules
        if piece.name == "pawn":
            if piece.color == "white":
                # Normal move forward
                if col_diff == 0 and not target:
                    if row_diff == -1:
                        return True
                    # First move can be two squares
                    if not piece.has_moved and row_diff == -2:
                        return not self.board[start_row - 1][start_col]  # Path must be clear

                # Capture moves (including en passant)
                if row_diff == -1 and abs(col_diff) == 1:
                    # Normal capture
                    if target:
                        return True
                    # En passant
                    if (self.last_move and
                            self.board[start_row][end_col] and
                            self.board[start_row][end_col].name == "pawn" and
                            self.board[start_row][end_col].en_passant_vulnerable):
                        return True

            else:  # Black pawn
                # Normal move forward
                if col_diff == 0 and not target:
                    if row_diff == 1:
                        return True
                    # First move can be two squares
                    if not piece.has_moved and row_diff == 2:
                        return not self.board[start_row + 1][start_col]  # Path must be clear

                # Capture moves (including en passant)
                if row_diff == 1 and abs(col_diff) == 1:
                    # Normal capture
                    if target:
                        return True
                    # En passant
                    if (self.last_move and
                            self.board[start_row][end_col] and
                            self.board[start_row][end_col].name == "pawn" and
                            self.board[start_row][end_col].en_passant_vulnerable):
                        return True

            return False

        elif piece.name == "knight":
            # Knights move in L-shape and can jump over pieces
            return (abs(row_diff), abs(col_diff)) in [(2, 1), (1, 2)]

        elif piece.name == "king":
            # Normal king move (one square in any direction)
            if abs(row_diff) <= 1 and abs(col_diff) <= 1:
                return True

            # Castling
            if not piece.has_moved and abs(col_diff) == 2 and row_diff == 0:
                # Check if it's a valid castling move
                return self.is_valid_castling(start, end)

            return False

        # For pieces that move in straight lines (rook, bishop, queen)
        # Check if the path is clear
        if piece.name in ["rook", "bishop", "queen"]:
            # Rook moves (horizontal/vertical)
            valid_rook_move = row_diff == 0 or col_diff == 0
            # Bishop moves (diagonal)
            valid_bishop_move = abs(row_diff) == abs(col_diff)

            # Determine if the piece can move this way
            if piece.name == "rook" and not valid_rook_move:
                return False
            if piece.name == "bishop" and not valid_bishop_move:
                return False
            if piece.name == "queen" and not (valid_rook_move or valid_bishop_move):
                return False

            # Check if path is clear
            row_step = 0 if row_diff == 0 else row_diff // abs(row_diff)
            col_step = 0 if col_diff == 0 else col_diff // abs(col_diff)

            current_row = start_row + row_step
            current_col = start_col + col_step

            while (current_row, current_col) != (end_row, end_col):
                if self.board[current_row][current_col]:
                    return False
                current_row += row_step
                current_col += col_step

            return True

        return False

    def is_in_check(self, color):
        """
        Determine if the king of the specified color is in check
        """
        # Find the king's position
        king_pos = self.find_king(color)
        if not king_pos:
            return False

        # Check if any opponent's piece can attack the king
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece and piece.color != color:
                    if self.is_valid_basic_move((row, col), king_pos):
                        return True
        return False

    def is_valid_move(self, start, end):
        """
        Check if a move from start to end is valid
        """
        if not start or not end:
            return False

        start_row, start_col = start
        end_row, end_col = end

        # Basic boundary checks
        if not (0 <= start_row < self.board_size and
                0 <= start_col < self.board_size and
                0 <= end_row < self.board_size and
                0 <= end_col < self.board_size):
            return False

        # Check basic move validity
        if not self.is_valid_basic_move(start, end):
            return False

        # Check if move puts or leaves king in check
        if self.move_puts_in_check(start, end):
            return False

        return True

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
        game_over_window.grab_set()  # Make the window modal

        # Center the window
        game_over_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50))

        # Show winner
        tk.Label(game_over_window,
                 text=f"Checkmate!\n{winner.capitalize()} Wins!",
                 font=("Arial", 24, "bold")).pack(pady=10)

        def new_game():
            game_over_window.destroy()
            self.reset_game()

        def return_to_main():
            game_over_window.destroy()
            self.return_to_menu()

        # Add buttons
        tk.Button(game_over_window,
                  text="New Game",
                  font=("Arial", 12),
                  command=new_game).pack(pady=10)

        tk.Button(game_over_window,
                  text="Return to Menu",
                  font=("Arial", 12),
                  command=return_to_main).pack(pady=10)

        # Disable the main game window while showing game over
        self.canvas.unbind('<Button-1>')  # Prevent further moves

    def find_king(self, color):
        """
        Find the position of the king of the specified color
        Returns: tuple (row, col) or None if not found
        """
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece and piece.name == "king" and piece.color == color:
                    return (row, col)
        return None

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

    def get_pins(self, color):
        pins = []
        king_pos = self.find_king(color)
        if not king_pos:
            return pins

        king_row, king_col = king_pos

        # Check all directions for pins
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Rook directions
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Bishop directions
        ]

        for direction in directions:
            possible_pin = None
            for i in range(1, 8):
                row = king_row + direction[0] * i
                col = king_col + direction[1] * i

                if not (0 <= row < 8 and 0 <= col < 8):
                    break

                current_piece = self.board[row][col]
                if current_piece:
                    if current_piece.color == color:
                        if possible_pin is None:
                            possible_pin = (row, col, direction[0], direction[1])
                        else:
                            break
                    else:
                        # Check if piece can pin
                        if possible_pin:
                            piece_name = current_piece.name
                            if ((piece_name == "rook" and direction[0] * direction[1] == 0) or
                                    (piece_name == "bishop" and direction[0] * direction[1] != 0) or
                                    (piece_name == "queen")):
                                pins.append(possible_pin)
                        break
        return pins

    def get_checks(self, color):
        checks = []
        king_pos = self.find_king(color)
        if not king_pos:
            return checks

        king_row, king_col = king_pos

        # Check all possible attacking pieces
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color:
                    if self.is_valid_basic_move((row, col), king_pos):
                        checks.append((row, col))
        return checks

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