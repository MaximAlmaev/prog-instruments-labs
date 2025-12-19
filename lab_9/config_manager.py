import yaml
import os


class LayeredConfig:
    def __init__(self, base_file="config/base.yaml", active_layer=None):
        self.base_file = base_file
        self.active_layer = active_layer
        self.config = {}
        self.load()
    
    def load(self):
        # Загружаем базовый конфиг
        self.config = self._load_yaml(self.base_file)
        
        # Если указан активный слой - наслаиваем его
        if self.active_layer:
            layer_path = f"config/{self.active_layer}"
            if os.path.exists(layer_path):
                layer_config = self._load_yaml(layer_path)
                
                # Проверяем, есть ли указание на другой родительский конфиг
                if "_extends" in layer_config:
                    parent = layer_config.pop("_extends")
                    parent_path = f"config/{parent}"
                    if os.path.exists(parent_path):
                        parent_config = self._load_yaml(parent_path)
                        self._merge_dicts(parent_config, self.config)
                
                # Наслаиваем конфиг поверх базового
                self._merge_dicts(layer_config, self.config)
    
    def _load_yaml(self, path):
        if not os.path.exists(path):
            return {}
        
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def _merge_dicts(self, source, target):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dicts(value, target[key])
            else:
                target[key] = value
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_layer(self, layer_name):
        self.active_layer = layer_name
        self.load()
    
    def save_layer(self, layer_name, config_dict):
        path = f"config/{layer_name}"
        with open(path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)


class GameConfig(LayeredConfig):
    def __init__(self, layer=None):
        super().__init__("config/base.yaml", layer)
        
        # Доступ к частым параметрам через свойства
        self.window_width = self.get("window.width", 600)
        self.window_height = self.get("window.height", 499)
        self.fps = self.get("window.fps", 32)
        self.title = self.get("window.title", "Flappy Bird")
        self.elevation = self.window_height * self.get("game.elevation_factor", 0.8)
        
        self.bird_jump = self.get("bird.jump_power", -8)
        self.bird_gravity = self.get("bird.gravity", 1)
        self.bird_max_speed = self.get("bird.max_speed_down", 10)
        self.bird_min_speed = self.get("bird.min_speed_up", -8)
        
        self.pipe_speed = self.get("game.pipe_speed", -4)
        self.pipe_gap = self.get("pipes.gap", 150)
        self.pipe_spacing = self.get("pipes.spacing", 300)
    
    def get_image_path(self, key):
        return self.get(f"paths.{key}", "")
    
    def get_color(self, key, default=(255, 255, 255)):
        colors = self.get("colors", {})
        return colors.get(key, default)
    
    def get_control_keys(self, action):
        controls = self.get("controls", {})
        keys = controls.get("keys", {})
        return keys.get(action, [])
