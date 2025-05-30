import torch
import torch.nn as nn
import numpy as np
from config import HyperParams
from utils import Transition
import gymnasium as gym
from torchvision import transforms
from models import ActorNet, CriticNet, BackboneNet
from torch.distributions import Normal


class Trainer:
    def __init__(
        self,
        env: gym.Env,
        opt: torch.optim.Optimizer,
        backbone_net: BackboneNet,
        actor_net: ActorNet,
        critic_net: CriticNet,
        target_net: CriticNet,
    ):
        self.env = env
        self.backbone_net = backbone_net
        self.actor_net = actor_net
        self.critic_net = critic_net
        self.target_net = target_net
        self.opt = opt

        self.transform = transforms.Compose(
            [
                transforms.ToTensor(),
            ]
        )

    def start_training(self):
        transitions = []

        obs = self._reset_env()

        for epoch in range(HyperParams.epochs):
            self._rollout(obs)
            self._train()
            self._opt_step()

    def _rollout(self, obs: torch.Tensor):
        for rollout in range(HyperParams.n_rollout):
            throttle_dist, steer_dist = self.actor_net(obs)

            throttle = throttle_dist.sample()
            throttle_log_prob = throttle_dist.log_prob(throttle)
            steer = steer_dist.sample()
            steer_log_prob = steer_dist.log_prob(steer)

            action = [throttle, steer]

            next_obs, reward, terminated, truncated, _ = self.env.step(action)
            print("we need to know how observations look like???")

    def _train(self):
        pass

    def _opt_step(self):
        pass

    def _reset_env(self) -> torch.Tensor:
        obs, _ = self.env.reset()
        return self._decode_obs(obs)

    def _decode_obs(self, obs: dict):
        """
        returns camera, lidar, birdeye, satate in tensor forms
        Height = Width = 256 (display parameter)
        C = 3 (channels)
        """
        camera: np.ndarray = obs["camera"]  # (D, D, C)
        lidar: np.ndarray = obs["lidar"]  # (D, D, C)
        birdeye: np.ndarray = obs["birdeye"]  # (D, D, C)
        state: np.ndarray = obs["state"]  # (4,)

        camera = self.transform(camera).unsqueeze(0)  # type: ignore BxCxHxW
        lidar = self.transform(lidar).unsqueeze(0)  # type: ignore BxCxHxW
        birdeye = self.transform(birdeye).unsqueeze(0)  # type: ignore BxCxHxW
        state = torch.tensor([state])  # type: ignore Bx4

        return camera, lidar, birdeye, state
