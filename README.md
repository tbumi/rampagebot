# RampageBot

A Dota 2 bot to be trained with _deep reinforcement learning_ using RLlib and
run in conjunction with the
[5v5dota2ai-addon](https://github.com/tbumi/5v5dota2ai-addon).

This project is built as part of a dissertation submitted for a Master's degree
in Artificial Intelligence.

## How to run

Clone the repo, install dependencies with `poetry install`, and run either
`rampagebot/rl/main_dqn.py` or `rampagebot/rl/main_ppo.py` depending on which
algorithm you want to train. Then launch Dota 2 Workshop Tools, and run the
dota2ai custom game.

## Inquiries?

Curious about this project, its background, or anything else? Feel free to
submit an issue in this repo and I will try to make time to answer there.

## License

This project is released to the public under the GNU GPL-3.0 license, in the
hopes that it may be useful to as many people as possible.
