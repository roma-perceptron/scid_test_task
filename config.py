import yaml
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    host: str = 'localhost'
    port: int = 3306
    user: str = 'user'
    password: str = 'password'
    database: str = 'database'

    def to_dict(self):
        return self.__dict__


@dataclass
class Config:
    database_test: DatabaseConfig
    database_prod: DatabaseConfig


def get_config(config_path: str = 'config.yml'):
    """
    Чтение и распарсинг yaml файла с данными конфигов БД
    :param config_path: имя yaml файла
    :return: датакласс с данными для подключения к тестовой и боевой БД
    """
    with open(config_path, mode='r') as f:
        raw_config = yaml.safe_load(f)

    return Config(
        database_test=DatabaseConfig(
            host=raw_config['database_test']['host'],
            port=raw_config['database_test']['port'],
            user=raw_config['database_test']['user'],
            password=raw_config['database_test']['password'],
            database=raw_config['database_test']['database'],
        ),
        database_prod=DatabaseConfig(
            host=raw_config['database_prod']['host'],
            port=raw_config['database_prod']['port'],
            user=raw_config['database_prod']['user'],
            password=raw_config['database_prod']['password'],
            database=raw_config['database_prod']['database'],
        )
    )
