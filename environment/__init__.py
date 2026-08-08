from gymnasium.envs.registration import register

from .colorflip_env import ColorFlipEnv

register(
    id="ColorFlip-v0",
    entry_point="environment.colorflip_env:ColorFlipEnv",
    max_episode_steps=100,
)

