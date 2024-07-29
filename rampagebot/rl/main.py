import numpy as np
import ray
from gymnasium.spaces import Box, Discrete
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.policy_server_input import PolicyServerInput
from ray.rllib.examples._old_api_stack.policy.random_policy import RandomPolicy
from ray.rllib.policy.policy import PolicySpec
from ray.tune.logger import pretty_print

from rampagebot.rl.models import GymAction, Observation

SERVER_ADDRESS = "localhost"
SERVER_PORT = 9090


def main():
    ray.init()

    low = []
    high = []
    for field_info in Observation.model_fields.values():
        low_constraint = float("-inf")
        high_constraint = float("inf")
        for constraint in field_info.metadata:
            if hasattr(constraint, "ge"):
                low_constraint = float(constraint.ge)
            elif hasattr(constraint, "le"):
                high_constraint = float(constraint.le)
        low.append(low_constraint)
        high.append(high_constraint)
    observation_space = Box(np.array(low), np.array(high))
    action_space = Discrete(len(GymAction))

    config = (
        PPOConfig()
        .environment(
            env=None,
            observation_space=observation_space,
            action_space=action_space,
        )
        .framework("torch")
        .offline_data(
            input_=lambda ioctx: PolicyServerInput(
                ioctx,
                SERVER_ADDRESS,
                SERVER_PORT,
            )
        )
        .env_runners(
            num_env_runners=0,
            enable_connectors=False,
        )
        .evaluation(off_policy_estimation_methods={})
        .multi_agent(
            policies={
                "main": PolicySpec(
                    observation_space=observation_space,
                    action_space=action_space,
                ),
                "random": PolicySpec(
                    policy_class=RandomPolicy,
                    observation_space=observation_space,
                    action_space=action_space,
                ),
            },
            policy_mapping_fn=lambda agent_id, *args, **kwargs: (
                "main" if agent_id.startswith("radiant") else "random"
            ),
            policies_to_train=["main"],
        )
        .debugging(log_level="INFO")
    )
    config.update_from_dict(
        {
            "model": {"use_lstm": True},
        }
    )

    algo = config.build()
    while True:
        try:
            result = algo.train()
            print(pretty_print(result))
            checkpoint_dir = algo.save().checkpoint.path
            print(f"Checkpoint saved in directory {checkpoint_dir}")
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
