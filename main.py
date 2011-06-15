from game import seq_game
import sys

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		raise Exception("Test mode not yet implemented")
	else:
		s = seq_game.Sequtus()
		s.start()
