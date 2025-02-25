# Chess Game

This project is a GUI-based chess game developed using Python and `tkinter`. It features a playable chessboard with customizable pieces represented by shapes or Unicode symbols, full chess rules, and a polished graphical interface.

## Features

- **Interactive Gameplay**: Two-player chess game with valid move enforcement.
- **Visual Representation**: Chess pieces are represented using `tkinter` shapes or symbols, and the board alternates between light and dark squares.
- **Highlights & Selection**: Selected pieces and valid moves are visually highlighted.
- **Game State Management**: Supports check, checkmate, and stalemate detection.
- **Castling & En Passant**: Implements special moves like castling and en passant.
- **Pawn Promotion**: Promotes pawns upon reaching the opposite side of the board.
- **Menu System**: Includes a main menu with options to play a new game or quit.
- **Customizable Appearance**: Colors and styles can be modified easily.

## How to Run

1. Ensure you have Python 3.x installed.
2. Install the required dependencies:
   ```bash
   pip install pillow
   ```
3. Run the game:
   ```bash
   python chess_game.py
   ```

## Controls

- **Mouse Click**: Select a piece, then click on a valid square to move it.
- **Main Menu**: Return to the main menu to start a new game or quit.

## File Structure

- **`chess_game.py`**: Main game logic and GUI implementation.
- **`main_menu.py`**: Main menu system for starting or quitting the game.
- **`assets/`**: (Optional) Folder for storing additional resources like images (if added).

## Customization

- To modify the board size, piece colors, or other appearance details, edit the respective constants in `chess_game.py`.
- To replace shapes with Unicode or image-based pieces, adjust the `draw` methods in the `ChessPiece` class.

## Future Enhancements

- Implement an AI opponent for single-player mode.
- Add a move history feature with undo functionality.
- Introduce time control for competitive games.

## License

This project is licensed under the [MIT License](LICENSE).
