import chess.pgn
import chess.svg
import subprocess
import lichess.pgn
import lichess.api
import os
import io
import imageio
import numpy as np
import cv2
from tqdm import tqdm
import sys

lichess_link = sys.argv[1] if len(sys.argv) > 1 else None

# animation speed
frame_rate = 0.5
# board orientation
as_black = False

# input / output files
game_pgn_file = "game.pgn"
gif_file = "game.gif"

# temporary files
html_file = "pos.html"
image_file = "pos.png"

# function for converting html to image
#bash = ("webkit2png "+html_file+" -o "+image_file).split()
path = os.getcwd()
html_file_full = "file://"+path+"/"+html_file
bash = ("firefox --headless --screenshot "+image_file+" "+html_file_full).split()
html2image = lambda: subprocess.Popen(bash).communicate()

def get_frames(game):
    """ get image frames in chess game """
    images = []
    board = game.board()
    images.append(write_board(board))
    moves = list(game.mainline_moves())
    prog_bar = tqdm(range(len(moves)))
    for i in prog_bar:
        board.push(moves[i]) # next move
        images.append(write_board(board))
    return np.array(images)

def write_board(board):
    """ get the image of a board position """
    # write html board position
    pos = chess.svg.board(board,flipped=as_black)
    f = open(html_file,"wb")
    f.write(bytes(pos, 'UTF-8'))
    # write image board position
    html2image()
    # read and return image
    return cv2.imread(image_file)

def cleanup():
    """ remove temporary files """
    os.remove(html_file)
    os.remove(image_file)
    #os.remove("webkit2png.log")

if __name__ == "__main__":

    if lichess_link:
        # get pgn from lichess.org
        game_id = lichess_link.split("/")[-1][0:8]
        lichess_game = lichess.api.game(game_id,with_moves=1)
        pgn = lichess.pgn.from_game(lichess_game)
        game = chess.pgn.read_game(io.StringIO(pgn))
    else:
        # read chess pgn file
        with open(game_pgn_file) as pgn:
            game = chess.pgn.read_game(pgn)

    # get image frames per move
    frames = get_frames(game)
    # write images to gif file
    imageio.mimsave(gif_file,frames,duration=frame_rate)
    # remove temporary files
    cleanup()