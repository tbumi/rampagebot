import numpy as np
from ray.rllib.env.policy_client import PolicyClient

SERVER_ADDRESS = "localhost"
SERVER_PORT = 9090


def calculate_rewards(rng):
    rew = {}
    for team in ("radiant", "dire"):
        for i in range(1, 6):
            rew[f"{team}_{i}"] = rng.random()
    return rew


def generate_rl_observations(rng):
    obs = {}
    for team in ("radiant", "dire"):
        for i in range(1, 6):
            obs[f"{team}_{i}"] = rng.random((56,))
    return obs


def main():
    rl_client = PolicyClient(
        f"http://{SERVER_ADDRESS}:{SERVER_PORT}", inference_mode="remote"
    )
    rng = np.random.default_rng()

    episode_id = rl_client.start_episode()

    for _ in range(200):
        observations = generate_rl_observations(rng)
        print(f"{observations=}")

        actions = rl_client.get_action(episode_id, observations)
        print(f"{actions=}")

        rewards = calculate_rewards(rng)
        print(f"{rewards=}")
        rl_client.log_returns(episode_id, rewards)

    rl_client.end_episode(episode_id, observations)


if __name__ == "__main__":
    # observations = generate_rl_observations()
    # print(observations)
    main()
