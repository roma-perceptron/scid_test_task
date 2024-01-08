import config
from manager import MergeManager


def demo():
    configs = config.get_config()

    demo_manager = MergeManager(configs_for_demo=configs)
    demo_manager.show_demo()


if __name__ == '__main__':
    demo()
