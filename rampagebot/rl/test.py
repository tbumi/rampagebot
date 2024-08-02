import numpy as np
from ray.rllib.env.policy_client import PolicyClient

from rampagebot.rl.models import Observation

SERVER_ADDRESS = "localhost"
SERVER_PORT = 9090


def calculate_rewards(rng):
    rew = {}
    for team in ("radiant", "dire"):
        for i in range(1, 6):
            rew[f"{team}_{i}"] = rng.random()
    return rew


def generate_rl_observations(rng, low, high):
    obs = {}
    for team in ("radiant", "dire"):
        for i in range(1, 6):
            result = []
            for j in range(len(low)):
                result.append(rng.uniform(low[j], high[j]))
            obs[f"{team}_{i}"] = np.array(result)
    return obs


def main():
    low = []
    high = []
    for field_info in Observation.model_fields.values():
        low_constraint = -9999
        high_constraint = 9999
        for constraint in field_info.metadata:
            if hasattr(constraint, "ge"):
                low_constraint = float(constraint.ge)
            elif hasattr(constraint, "le"):
                high_constraint = float(constraint.le)
        low.append(low_constraint)
        high.append(high_constraint)

    rl_client = PolicyClient(
        f"http://{SERVER_ADDRESS}:{SERVER_PORT}", inference_mode="remote"
    )
    rng = np.random.default_rng()

    for _ in range(11):
        episode_id = rl_client.start_episode()
        print(f"{episode_id=}")

        for _ in range(400):
            observations = generate_rl_observations(rng, low, high)
            # print(f"{observations=}")

            rl_client.get_action(episode_id, observations)
            # print(f"{actions=}")

            rewards = calculate_rewards(rng)
            # print(f"{rewards=}")
            rl_client.log_returns(episode_id, rewards)

        rl_client.end_episode(episode_id, observations)


if __name__ == "__main__":
    # observations = generate_rl_observations()
    # print(observations)
    main()
