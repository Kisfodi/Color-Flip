import gymnasium as gym
import numpy as np
from gymnasium import spaces

from backend.game import Game


class ColorFlipEnv(gym.Env):
    """A Gymnasium environment for training agents on the Color Flip puzzle."""

    _metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, size=4, seed=None, mode="mixed", render_mode=None, fps=None, max_episode_steps=100):
        super().__init__()
        self._size = size
        self._seed = seed
        self._mode = mode
        self._render_mode = render_mode
        self._fps = fps if fps is not None else self._metadata["render_fps"]
        self._max_episode_steps = max_episode_steps
        self._step_count = 0

        self._game = Game(size=self._size, seed=self._seed, mode=self._mode)

        self.action_space = spaces.Discrete(self._size * self._size)
        self.observation_space = spaces.Box(low=0, high=1, shape=(self._size, self._size), dtype=np.uint8)

    def _get_observation(self):
        return np.array(self._game.board, dtype=np.uint8)

    def _get_info(self):
        state = self._game.get_game_state()
        return {
            "moves_made": state["moves_made"],
            "solved": bool(state["game_over"]),
            "board_size": state["board_size"],
            "mode": state["mode"],
        }

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._seed = self._seed if seed is None else seed
        self._game = Game(size=self._size, seed=self._seed, mode=self._mode)
        self._step_count = 0
        return self._get_observation(), self._get_info()

    def step(self, action):
        if not isinstance(action, (int, np.integer)):
            raise TypeError("Action must be an integer index")
        if not 0 <= int(action) < self.action_space.n:
            raise ValueError(f"Action {action} is out of bounds for board size {self._size}")

        row = int(action) // self._size
        col = int(action) % self._size

        self._game.step(row, col)
        self._step_count += 1

        terminated = self._game.is_solved()
        truncated = self._step_count >= self._max_episode_steps
        reward = 1.0 if terminated else -0.01

        return self._get_observation(), reward, terminated, truncated, self._get_info()

    def render(self, mode="human"):
        if mode != "human":
            raise NotImplementedError("Only human rendering is supported")
        print(np.array(self._game.board, dtype=np.uint8))

    def close(self):
        return None