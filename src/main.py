import sys
import os

# ensure src directory is on sys.path when running from project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from game import Game


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('游戏启动出错:', e)
        sys.exit(1)
