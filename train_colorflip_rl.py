import os

import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

from environment import ColorFlipEnv  # noqa: F401


def main():
    env_id = "ColorFlip-v0"
    vec_env = make_vec_env(env_id, n_envs=4, env_kwargs={"size": 4, "seed": 0})

    model = PPO("MlpPolicy", vec_env, verbose=1, learning_rate=3e-4, n_steps=2048, batch_size=64)
    model.learn(total_timesteps=20000)

    model.save("models/colorflip_ppo")
    print("Training complete. Model saved to models/colorflip_ppo")


if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    main()
