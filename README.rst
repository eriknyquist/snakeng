snakeng
-------

``snakeng`` is an implementation of the back-end of the classic "snake" game. It provides
an interface to inject directional inputs (up/down/right/left), and produces a data structure
representing the game state, for each frame of gameplay. This allows snake to be quickly
implemented and played on various platforms.

Features:

* Configurable game area width/height
* Configurable wall behaviour (teleport/wrap or death)
* Serializable game state object (if you want to e.g. save/load game states to .json files)
* Configurable snake speed options (fixed speed, or automatically increase speed as snake grows)

Sample implementation
---------------------

Additionally, a sample terminal-based implementation of a snake game is provided,
which can be accessed by running ``snakeng`` as a module:

::

    python -m snakeng

.. image:: https://github.com/eriknyquist/snakeng/raw/master/images/terminal_example.gif

The terminal-based implementation accepts several arguments, detailed here:

::

	usage: snakeng [-h] [-x WIDTH] [-y HEIGHT] [-s {slow,medium,fast,faster}]
				   [-f FPS]

	Simple terminal-based snake game showing how to use snakeng to implement a
	game

	options:
	  -h, --help            show this help message and exit
	  -x WIDTH, --width WIDTH
							Game area width in characters (default: 40)
	  -y HEIGHT, --height HEIGHT
							Game area height in characters (default: 30)
	  -s {slow,medium,fast,faster}, --fixed-speed {slow,medium,fast,faster}
							Sets the snake speed for the whole game. If unset, the
							snake speed will automatically increase as the snake
							size increases. (default: None)
	  -f FPS, --fps FPS     Framerate in frames per second (default: 24)

NOTE: the sample implementation uses an ANSI escape sequence to clear the terminal screen,
so it won't work in terminals that don't support ANSI escape sequences.

Contributions
-------------

Contributions are welcome, please open a pull request at `<https://github.com/eriknyquist/snakeng>`_.

If you have any questions about / need help with contributions, please contact Erik at eknyquist@gmail.com.
