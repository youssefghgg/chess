import tkinter as tk
from tkinter import messagebox
from chess import engine
import threading
import os


class ChessEngine:
    def __init__(self, depth=20):
        self.depth = depth
        self.engine = None
        self.engine_path = r"C:\Users\Youssef Ahmed\PycharmProjects\pythonProject2\chess\stockfish\stockfish-windows-x86-64-sse41-popcnt"
        self.initialize_engine()

    def initialize_engine(self):
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            # Set engine options if needed
            # self.engine.configure({"Threads": 4, "Hash": 128})
        except Exception as e:
            print(f"Error initializing engine: {e}")
            self.engine = None

    def get_best_move(self, board_fen, time_limit=2.0):
        if not self.engine:
            return None

        try:
            board = chess.Board(board_fen)
            result = self.engine.play(
                board,
                chess.engine.Limit(time=time_limit)
            )
            return result.move
        except Exception as e:
            print(f"Error getting best move: {e}")
            return None

    def get_position_evaluation(self, board_fen):
        if not self.engine:
            return None

        try:
            board = chess.Board(board_fen)
            info = self.engine.analyse(board, chess.engine.Limit(depth=self.depth))
            score = info["score"].relative.score()
            return score / 100  # Convert centipawns to pawns
        except Exception as e:
            print(f"Error getting evaluation: {e}")
            return None

    def close(self):
        if self.engine:
            self.engine.quit()
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

        # Initialize game state variables
        self.move_history = []
        self.halfmove_clock = 0
        self.position_counts = {}

        # Main container
        self.main_container = tk.Frame(self.root, bg='#2C3E50')
        self.main_container.pack(expand=True, fill='both', padx=20, pady=20)

        # Top control panel
        self.control_panel = tk.Frame(self.main_container, bg='#2C3E50')
        self.control_panel.pack(fill='x', pady=(0, 10))

        # Return to menu button
        self.menu_button = tk.Button(self.control_panel,
                                     text="Return to Menu",
                                     command=self.return_to_menu,
                                     font=('Helvetica', 12),
                                     bg='#34495E',
                                     fg='white',
                                     activebackground='#2C3E50',
                                     activeforeground='white',
                                     bd=0,
                                     cursor='hand2')
        self.menu_button.pack(side=tk.LEFT, padx=10)

        # Draw button
        self.draw_button = tk.Button(
            self.control_panel,
            text="Offer Draw",
            command=self.offer_draw,
            font=('Helvetica', 12),
            bg='#34495E',
            fg='white',
            activebackground='#2C3E50',
            activeforeground='white',
            bd=0,
            cursor='hand2'
        )
        self.draw_button.pack(side=tk.LEFT, padx=10)

        # Turn indicator
        self.turn_label = tk.Label(self.control_panel,
                                   text="White's turn",
                                   font=("Helvetica", 16),
                                   bg='#2C3E50',
                                   fg='white')
        self.turn_label.pack(side=tk.LEFT, padx=20)

        # Game area container
        self.game_area = tk.Frame(self.main_container, bg='#2C3E50')
        self.game_area.pack(expand=True, fill='both')

        # Evaluation frame on the left
        self.eval_frame = tk.Frame(self.game_area, bg='#2C3E50', width=100)
        self.eval_frame.pack(side=tk.LEFT, padx=20, fill='y')

        # Material count labels
        self.black_material_label = tk.Label(
            self.eval_frame,
            text="Black: 0",
            font=("Helvetica", 14, "bold"),
            bg='#2C3E50',
            fg='white'
        )
        self.black_material_label.pack(pady=10)

        # Evaluation bar
        self.eval_canvas = tk.Canvas(
            self.eval_frame,
            width=60,
            height=500,
            bg='#34495E',
            highlightthickness=1,
            highlightbackground='#95A5A6'
        )
        self.eval_canvas.pack(pady=10)

        self.white_material_label = tk.Label(
            self.eval_frame,
            text="White: 0",
            font=("Helvetica", 14, "bold"),
            bg='#2C3E50',
            fg='white'
        )
        self.white_material_label.pack(pady=10)

        # Chess board container
        self.board_container = tk.Frame(self.game_area, bg='#2C3E50')
        self.board_container.pack(side=tk.LEFT, expand=True, fill='both')
        # Add to existing initialization
        self.engine = ChessEngine()
        self.engine_thinking = False

        # Add engine control buttons
        self.add_engine_controls()
        # Initialize game components
        self.selected_piece = None
        self.current_player = "white"
        self.last_move = None
        self.board_size = 8
        self.cell_size = 80
        self.canvas_size = self.board_size * self.cell_size

        # Initialize piece images
        self.piece_images = {
            "white_pawn": "♙", "white_rook": "♖", "white_knight": "♘",
            "white_bishop": "♗", "white_queen": "♕", "white_king": "♔",
            "black_pawn": "♟", "black_rook": "♜", "black_knight": "♞",
            "black_bishop": "♝", "black_queen": "♛", "black_king": "♚"
        }

        # Create the chess board canvas
        self.canvas = tk.Canvas(
            self.board_container,
            width=self.canvas_size,
            height=self.canvas_size,
            bg='#ECF0F1'
        )
        self.canvas.pack(padx=20, pady=20)

        # Initialize the board
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.create_pieces()
        self.draw_board()

        # Bind click event
        self.canvas.bind('<Button-1>', self.on_square_click)


        self.move_history = []  # Store positions for threefold repetition
        self.halfmove_clock = 0  # For fifty-move rule
        self.position_counts = {}  # For tracking repeated positions

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
        # Update evaluation after creating pieces
        self.update_evaluation_display()

    def add_engine_controls(self):
        # Add to control panel
        self.engine_button = tk.Button(
            self.control_panel,
            text="Get Engine Move",
            command=self.get_engine_move,
            font=('Helvetica', 12),
            bg='#34495E',
            fg='white',
            activebackground='#2C3E50',
            activeforeground='white',
            bd=0,
            cursor='hand2'
        )
        self.engine_button.pack(side=tk.LEFT, padx=10)

    def board_to_fen(self):
        """Convert current board position to FEN string"""
        fen = []
        for row in range(self.board_size):
            empty = 0
            row_fen = ''
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece is None:
                    empty += 1
                else:
                    if empty > 0:
                        row_fen += str(empty)
                        empty = 0
                    # Convert piece to FEN notation
                    symbol = piece.name[0].upper() if piece.name != 'knight' else 'N'
                    if piece.color == 'black':
                        symbol = symbol.lower()
                    row_fen += symbol
            if empty > 0:
                row_fen += str(empty)
            fen.append(row_fen)

        # Join rows and add other FEN components
        fen_str = '/'.join(fen)
        fen_str += f" {'w' if self.current_player == 'white' else 'b'} KQkq - 0 1"
        return fen_str

    def get_engine_move(self):
        if self.engine_thinking:
            return

        self.engine_thinking = True
        self.engine_button.config(state='disabled')

        def engine_think():
            try:
                # Get current position FEN
                fen = self.board_to_fen()

                # Get engine's move
                move = self.engine.get_best_move(fen)

                if move:
                    # Convert move to board coordinates
                    start_square = chess.square_name(move.from_square)
                    end_square = chess.square_name(move.to_square)

                    # Convert algebraic notation to board coordinates
                    start_col = ord(start_square[0]) - ord('a')
                    start_row = 8 - int(start_square[1])
                    end_col = ord(end_square[0]) - ord('a')
                    end_row = 8 - int(end_square[1])

                    # Make the move
                    self.root.after(0, lambda: self.make_engine_move(
                        (start_row, start_col), (end_row, end_col)))

            finally:
                self.engine_thinking = False
                self.root.after(0, lambda: self.engine_button.config(state='normal'))

        # Run engine analysis in separate thread
        threading.Thread(target=engine_think, daemon=True).start()

    def make_engine_move(self, start, end):
        """Execute the engine's move"""
        if self.is_valid_move(start, end):
            self.move_piece(start, end)

            # Switch turns
            opposite_color = "black" if self.current_player == "white" else "white"
            if self.is_checkmate(opposite_color):
                self.game_over(self.current_player)
            else:
                self.current_player = opposite_color
                self.turn_label.config(text=f"{self.current_player.capitalize()}'s turn")

            self.selected_piece = None
            self.draw_board()
            self.update_evaluation_display()

    def __del__(self):
        # Clean up engine when game is closed
        if hasattr(self, 'engine'):
            self.engine.close()

    def is_draw(self):
        """Check all draw conditions"""
        if self.is_stalemate(self.current_player):
            self.draw_game("Stalemate")
            return True
        if self.is_insufficient_material():
            self.draw_game("Insufficient Material")
            return True
        if self.is_threefold_repetition():
            self.draw_game("Threefold Repetition")
            return True
        if self.is_fifty_move_rule():
            self.draw_game("Fifty-Move Rule")
            return True
        if self.is_dead_position():
            self.draw_game("Dead Position")
            return True
        return False

    def is_insufficient_material(self):
        """Check if there's insufficient material for checkmate"""
        pieces = {'white': [], 'black': []}
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece:
                    pieces[piece.color].append(piece.name)

        # Remove kings from the count
        for color in pieces:
            pieces[color].remove('king')

        # Check insufficient material conditions
        for color in pieces:
            if not pieces[color]:  # Only king
                continue
            if len(pieces[color]) == 1:
                if pieces[color][0] in ['bishop', 'knight']:  # King and bishop/knight
                    continue
            return False
        return True

    def is_threefold_repetition(self):
        """Check if the current position has occurred three times"""
        position = self.get_position_string()
        self.position_counts[position] = self.position_counts.get(position, 0) + 1
        return self.position_counts[position] >= 3

    def is_fifty_move_rule(self):
        """Check if fifty moves have been made without pawn movement or capture"""
        return self.halfmove_clock >= 100  # 50 moves = 100 halfmoves

    def is_dead_position(self):
        """Check if the position is dead (impossible to checkmate)"""
        pieces = {'white': [], 'black': []}
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece:
                    pieces[piece.color].append(piece.name)

        # King vs King
        if len(pieces['white']) == 1 and len(pieces['black']) == 1:
            return True

        # King and bishop/knight vs King
        for color in ['white', 'black']:
            other = 'black' if color == 'white' else 'white'
            if len(pieces[color]) == 2 and len(pieces[other]) == 1:
                if 'bishop' in pieces[color] or 'knight' in pieces[color]:
                    return True

        return False

    def get_position_string(self):
        """Convert current board position to a string for comparison"""
        position = ""
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece:
                    position += f"{piece.color}_{piece.name}_{row}_{col}_"
        position += f"{self.current_player}"
        return position

    def draw_game(self, reason):
        """Handle the draw game window"""
        draw_window = tk.Toplevel(self.root)
        draw_window.title("Game Draw")
        draw_window.geometry("300x200")
        draw_window.transient(self.root)
        draw_window.grab_set()

        # Center the window
        draw_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50))

        # Show draw message
        tk.Label(draw_window,
                 text=f"Draw!\n{reason}",
                 font=("Arial", 24, "bold")).pack(pady=10)

        def new_game():
            draw_window.destroy()
            self.reset_game()

        def return_to_main():
            draw_window.destroy()
            self.return_to_menu()

        # Add buttons
        tk.Button(draw_window,
                  text="New Game",
                  font=("Arial", 12),
                  command=new_game).pack(pady=10)

        tk.Button(draw_window,
                  text="Return to Menu",
                  font=("Arial", 12),
                  command=return_to_main).pack(pady=10)

        # Disable the main game window
        self.canvas.unbind('<Button-1>')

    def offer_draw(self):
        """Handle draw offers"""
        response = messagebox.askyesno(
            "Draw Offer",
            f"{self.current_player.capitalize()} offers a draw.\nDoes {('Black' if self.current_player == 'white' else 'White')} accept?",
            parent=self.root
        )
        if response:
            self.draw_game("Draw by Agreement")

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

        # Basic checks
        if king.has_moved or self.is_in_check(king.color):
            return False

        # Determine rook position and target squares
        if end_col > start_col:  # Kingside castling
            rook_col = 7
            path_cols = [5, 6]  # Squares that must be empty and safe
            through_squares = [(start_row, 5), (start_row, 6)]  # Squares the king moves through
        else:  # Queenside castling
            rook_col = 0
            path_cols = [1, 2, 3]  # Squares that must be empty and safe
            through_squares = [(start_row, 2), (start_row, 3)]  # Squares the king moves through

        # Check if rook is in position and hasn't moved
        rook = self.board[start_row][rook_col]
        if not rook or rook.name != "rook" or rook.has_moved:
            return False

        # Check if squares between king and rook are empty
        for col in path_cols:
            if self.board[start_row][col] is not None:
                return False

        # Check if the king moves through or ends up on any square that is under attack
        for square in through_squares:
            # Temporarily move king to check if square is safe
            original_king = self.board[start_row][start_col]
            self.board[start_row][start_col] = None
            self.board[square[0]][square[1]] = king

            # Check if this square is under attack
            square_under_attack = False
            for r in range(self.board_size):
                for c in range(self.board_size):
                    piece = self.board[r][c]
                    if piece and piece.color != king.color:
                        if self.is_valid_basic_move((r, c), square):
                            square_under_attack = True
                            break
                if square_under_attack:
                    break

            # Move king back
            self.board[start_row][start_col] = original_king
            self.board[square[0]][square[1]] = None

            if square_under_attack:
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

        # Update evaluation immediately after the move
        self.update_evaluation_display()

    def add_draw_button(self):
        """Add draw offer button to control panel"""
        self.draw_button = tk.Button(
            self.control_panel,
            text="Offer Draw",
            command=self.offer_draw,
            font=('Helvetica', 12),
            bg='#34495E',
            fg='white',
            activebackground='#2C3E50',
            activeforeground='white',
            bd=0,
            cursor='hand2'
        )
        self.draw_button.pack(side=tk.LEFT, padx=10)

    def on_square_click(self, event):
        try:
            col = event.x // self.cell_size
            row = event.y // self.cell_size

            # Validate coordinates
            if not (0 <= row < self.board_size and 0 <= col < self.board_size):
                return

            # First click - Selecting a piece
            if self.selected_piece is None:
                piece = self.board[row][col]
                # Can only select pieces of current player's color
                if piece and piece.color == self.current_player:
                    self.selected_piece = (row, col)
                    self.draw_board()
                return

            # Second click - Moving the piece
            start_row, start_col = self.selected_piece

            # If clicking the same square, deselect the piece
            if row == start_row and col == start_col:
                self.selected_piece = None
                self.draw_board()
                return

            # If clicking another piece of same color, switch selection
            piece = self.board[row][col]
            if piece and piece.color == self.current_player:
                self.selected_piece = (row, col)
                self.draw_board()
                return

            # Attempt to move the piece
            if self.is_valid_move(self.selected_piece, (row, col)):
                # Make the move
                self.move_piece(self.selected_piece, (row, col))

                # Check for checkmate
                opposite_color = "black" if self.current_player == "white" else "white"
                if self.is_checkmate(opposite_color):
                    self.game_over(self.current_player)
                else:
                    # If no checkmate, switch turns
                    self.current_player = opposite_color
                    self.turn_label.config(text=f"{self.current_player.capitalize()}'s turn")

                # Reset selection
                self.selected_piece = None
                self.draw_board()

                # Update evaluation
                self.update_evaluation_display()
            else:
                # Invalid move, just deselect the piece
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
        if not start or not end:
            return False

        start_row, start_col = start
        end_row, end_col = end
        piece = self.board[start_row][start_col]

        # Basic boundary checks
        if not (0 <= start_row < self.board_size and
                0 <= start_col < self.board_size and
                0 <= end_row < self.board_size and
                0 <= end_col < self.board_size):
            return False

        # For castling moves
        if piece and piece.name == "king" and abs(end_col - start_col) == 2:
            return self.is_valid_castling(start, end)

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

    def get_piece_value(self, piece):
        """Return the standard piece values"""
        values = {
            "pawn": 1,
            "knight": 3,
            "bishop": 3.25,  # Slightly higher than knight
            "rook": 5,
            "queen": 9,
            "king": 0  # King's value isn't counted in material
        }
        return values.get(piece.name, 0)

    def evaluate_position(self):
        """
        Evaluate the current position
        Returns a score (positive favors white, negative favors black)
        """
        white_score = 0
        black_score = 0

        # Material counting
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece:
                    value = self.get_piece_value(piece)

                    # Add position-based bonuses
                    if piece.name == "pawn":
                        # Pawns are worth more as they advance
                        if piece.color == "white":
                            value += (7 - row) * 0.1
                        else:
                            value += row * 0.1
                    elif piece.name in ["knight", "bishop"]:
                        # Minor pieces are worth more in the center
                        center_distance = abs(3.5 - row) + abs(3.5 - col)
                        value += (4 - center_distance) * 0.1

                    if piece.color == "white":
                        white_score += value
                    else:
                        black_score += value

        # Check and checkmate evaluation
        if self.is_in_check("black"):
            if self.is_checkmate("black"):
                white_score += 100  # Checkmate
            else:
                white_score += 0.5  # Check

        if self.is_in_check("white"):
            if self.is_checkmate("white"):
                black_score += 100  # Checkmate
            else:
                black_score += 0.5  # Check

        return white_score - black_score

    def evaluate_position(self):
        """
        Evaluate the current position
        Returns a score (positive favors white, negative favors black)
        """
        white_score = 0
        black_score = 0

        # Material counting
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece:
                    value = self.get_piece_value(piece)
                    if piece.color == "white":
                        white_score += value
                    else:
                        black_score += value

        # Position evaluation (basic)
        # Center control
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for row, col in center_squares:
            piece = self.board[row][col]
            if piece:
                bonus = 0.2
                if piece.color == "white":
                    white_score += bonus
                else:
                    black_score += bonus

        # King safety
        white_king_pos = self.find_king("white")
        black_king_pos = self.find_king("black")

        if white_king_pos:
            if self.is_in_check("white"):
                white_score -= 0.5
        if black_king_pos:
            if self.is_in_check("black"):
                black_score -= 0.5

        return white_score - black_score

    def update_evaluation_display(self):
        """Update the evaluation bar and material count"""
        eval_score = self.evaluate_position()

        # Calculate material count
        white_material = 0
        black_material = 0
        for row in self.board:
            for piece in row:
                if piece:
                    value = self.get_piece_value(piece)
                    if piece.color == "white":
                        white_material += value
                    else:
                        black_material += value

        # Update material count labels with piece symbols
        # Convert to int for string multiplication
        white_symbols = '♙' * int(white_material // 3)
        black_symbols = '♟' * int(black_material // 3)

        self.white_material_label.config(
            text=f"White: {white_material:.1f}"
        )
        self.black_material_label.config(
            text=f"Black: {black_material:.1f}"
        )

        # Update evaluation bar
        max_height = 500  # Match canvas height
        middle = max_height / 2

        # Convert evaluation score to visual representation
        bar_height = middle + (middle * eval_score / 10)  # Scale factor of 10
        bar_height = max(0, min(max_height, bar_height))

        # Clear previous bar
        self.eval_canvas.delete("all")

        # Draw middle line
        self.eval_canvas.create_line(
            0, middle, 60, middle,
            fill='#95A5A6',
            width=1
        )

        # Draw evaluation bar
        if eval_score >= 0:
            # White advantage - draw from middle up
            self.eval_canvas.create_rectangle(
                5, middle - (bar_height - middle),
                55, middle,
                fill="#27AE60",  # Green for white advantage
                outline="#2ECC71"
            )
        else:
            # Black advantage - draw from middle down
            self.eval_canvas.create_rectangle(
                5, middle,
                55, bar_height,
                fill="#E74C3C",  # Red for black advantage
                outline="#C0392B"
            )

        # Add evaluation text
        self.eval_canvas.create_text(
            30, 250,  # Centered
            text=f"{abs(eval_score):.1f}",
            fill="white",
            font=("Helvetica", 12, "bold")
        )

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
        # Update evaluation after reset
        self.update_evaluation_display()

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
        self.game_window.geometry("1200x900")  # Increased window size
        self.game_window.configure(bg='#2C3E50')
        self.game_window.resizable(False, False)  # Prevent window resizing

        # Create and start the game
        chess_game = ChessGame(self.game_window, self)


    def show_menu(self):
        if self.game_window:
            self.game_window.destroy()
            self.game_window = None
        self.root.deiconify()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()