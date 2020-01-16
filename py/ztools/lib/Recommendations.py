import rawgpy

def get_suggestions(game=None,titleid=None,slug=None,number=10,platform="Switch"):
	game=str(game).lower()
	number=int(number)
	