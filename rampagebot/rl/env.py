import numpy as np
import uvicorn
from gymnasium.spaces import Box, Discrete
from ray.rllib.env.external_multi_agent_env import ExternalMultiAgentEnv

from rampagebot.main import app
from rampagebot.rl.models import GymAction, Observation


class RampageBotEnv(ExternalMultiAgentEnv):
    def __init__(self, config):
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

        super().__init__(
            action_space=action_space,
            observation_space=observation_space,
        )

    def run(self):
        app.state.rl_class = self

        uvicorn.run(app, port=8080, log_level="warning")
