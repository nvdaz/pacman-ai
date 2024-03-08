from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import (
    CheckpointCallback,
    EvalCallback,
)
from gymnasium.wrappers.time_limit import TimeLimit
from stable_baselines3.common.vec_env import VecFrameStack, SubprocVecEnv
from stable_baselines3.common.monitor import Monitor
from .env import PacbotEnv
from stable_baselines3.common.env_checker import check_env

check_env(PacbotEnv())


def make_env():
    env = PacbotEnv()
    env = TimeLimit(env, max_episode_steps=50000)
    env = Monitor(env, info_keywords=("score",))

    return env


num_envs = 12
env = SubprocVecEnv([make_env for _ in range(num_envs)])
env = VecFrameStack(env, n_stack=4)

LOG_DIR = "./logs/"
CHECKPOINT_DIR = "./checkpoints/"

checkpoint_callback = CheckpointCallback(save_freq=10000, save_path=CHECKPOINT_DIR)
eval_callback = EvalCallback(
    env,
    best_model_save_path=CHECKPOINT_DIR,
    log_path=CHECKPOINT_DIR,
    eval_freq=1000,
    deterministic=True,
    render=False,
)


def linear_schedule(initial_value: float):
    def func(progress_remaining):
        return progress_remaining * initial_value

    return func


model = PPO(
    "MlpPolicy",
    env,
    verbose=1,
    tensorboard_log=LOG_DIR,
    learning_rate=linear_schedule(3e-4),
    n_steps=128,
    n_epochs=4,
    batch_size=256,
    gamma=0.99,
    clip_range=linear_schedule(0.1),
    ent_coef=0.05,
    vf_coef=0.5,
)

model.learn(
    total_timesteps=1e6,
    callback=[checkpoint_callback, eval_callback],
)

model.save("model")
