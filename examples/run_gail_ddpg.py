import roboschool
import gym

from tf2rl.algos.ddpg import DDPG
from tf2rl.algos.gail import GAIL
from tf2rl.experiments.trainer import Trainer
from tf2rl.experiments.irl_trainer import IRLTrainer
from tf2rl.experiments.utils import restore_latest_n_traj


if __name__ == '__main__':
    parser = IRLTrainer.get_argument()
    parser = GAIL.get_argument(parser)
    parser.add_argument('--env-name', type=str, default="RoboschoolReacher-v1")
    args = parser.parse_args()

    if args.expert_path_dir is None:
        print("Plaese generate demonstrations first")
        print("python examples/run_sac.py --env-name=RoboschoolReacher-v1 --save-test-path --test-interval=50000")
        exit()

    units = [100, 100]

    env = gym.make(args.env_name)
    test_env = gym.make(args.env_name)
    policy = DDPG(
        state_shape=env.observation_space.shape,
        action_dim=env.action_space.high.size,
        max_action=env.action_space.high[0],
        gpu=args.gpu,
        actor_units=units,
        critic_units=units,
        n_warmup=1000,
        batch_size=32)
    irl = GAIL(
        state_shape=env.observation_space.shape,
        action_dim=env.action_space.high.size,
        units=units,
        enable_sn=args.enable_sn,
        gpu=args.gpu)
    expert_trajs = restore_latest_n_traj(
        args.expert_path_dir, n_path=20, max_steps=100)
    trainer = IRLTrainer(policy, env, args, irl, expert_trajs["obses"],
                         expert_trajs["acts"], test_env)
    trainer()

# python examples/run_gail_ddpg.py --expert-path-dir /path/to/expert_dir
