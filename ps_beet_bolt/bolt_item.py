from hashlib import sha512
from typing import Hashable

component_names = [
    "attribute_modifiers",
    "axolotl/variant",
    "banner_patterns",
    "base_color",
    "bees",
    "block_entity_data",
    "block_state",
    "blocks_attacks",
    "break_sound",
    "bucket_entity_data",
    "bundle_contents",
    "can_break",
    "can_place_on",
    "cat/collar",
    "cat/variant",
    "charged_projectiles",
    "consumable",
    "container",
    "container_loot",
    "creative_slot_lock",
    "custom_data",
    "custom_model_data",
    "custom_name",
    "damage",
    "damage_resistant",
    "death_protection",
    "debug_stick_state",
    "dyed_color",
    "enchantable",
    "enchantment_glint_override",
    "enchantments",
    "entity_data",
    "equippable",
    "firework_explosion",
    "fireworks",
    "food",
    "fox/variant",
    "frog/variant",
    "glider",
    "horse/variant",
    "instrument",
    "intangible_projectile",
    "item_model",
    "item_name",
    "jukebox_playable",
    "llama/variant",
    "lock",
    "lodestone_tracker",
    "lore",
    "map_color",
    "map_decorations",
    "map_id",
    "map_post_processing",
    "max_damage",
    "max_stack_size",
    "mooshroom/variant",
    "note_block_sound",
    "ominous_bottle_amplifier",
    "painting/variant",
    "parrot/variant",
    "pig/variant",
    "pot_decorations",
    "potion_contents",
    "potion_duration_scale",
    "profile",
    "provides_banner_patterns",
    "provides_trim_material",
    "rabbit/variant",
    "rarity",
    "recipes",
    "repair_cost",
    "repairable",
    "salmon/size",
    "sheep/color",
    "shulker/color",
    "stored_enchantments",
    "suspicious_stew_effects",
    "tool",
    "tooltip_display",
    "tooltip_style",
    "trim",
    "tropical_fish/base_color",
    "tropical_fish/pattern",
    "tropical_fish/pattern_color",
    "unbreakable",
    "use_cooldown",
    "use_remainder",
    "villager/variant",
    "weapon",
    "wolf/collar",
    "wolf/variant",
    "writable_book_content",
    "written_book_content"
]

#>########### classes ###########<#

class Components:
    __initialized__ = False

    def __init__(self, namespace: str, id: str, hash: int, base_item: str, components: dict):
        self.namespace = namespace
        self.id = id
        self.hash = hash
        self.base_item = base_item
        for name, value in components.items():
            setattr(self, name, value)
        self.__initialized__ = True

    def __setattr__(self, name, value):
        if self.__initialized__ and name not in component_names:
            raise Exception(f'[bolt-item]: "{name}" is not a valid component')
        self.__dict__[name] = value

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def get(self, name, default = None):
        return getattr(self, name, default)

    def merge(self, name, value):
        setattr(self, name, deep_merge(self.get(name), value))

#>########### decorators ###########<#

def bolt_item(cls: type):
    components, callables = _get_components_and_callables_from_parents(cls)

    if not 'base_item' in cls.__dict__:
        cls.base_item = "poisonous_potato"
    if not 'removed_components' in cls.__dict__:
        cls.removed_components = ["food","consumable"]

    cls.id = camel_case_to_snake_case(cls.__name__)
    cls.namespace = cls.__module__.split(':')[0]
    cls.hash = _int_hash(f"{cls.namespace}:{cls.id}")
    cls.component_proxy = Components(cls.namespace, cls.id, cls.hash, cls.base_item, components)

    _run_callables(cls, callables['before_all'])
    _run_callables(cls, callables['regular'])
    _run_callables(cls, callables['after_all'])

    cls.component_proxy.merge("custom_data", {"bolt-item":{"id":f"{cls.namespace}:{cls.id}","hash":cls.hash}})

    cls.components = _get_mc_components(cls.component_proxy, cls.removed_components)

    return cls

def transformer(component: str):
    if component not in component_names:
        raise Exception(f'[bolt-item]: "{component}" is not a valid component name')
    def decorator(func):
        func.transforms_component = component
        return func
    return decorator

def custom_component(component: str):
    def decorator(func):
        func.custom_component = component
        return func
    return decorator

def event_decorator(func):
    def decorator(bolt_func):
        def run_it(p):
            func(bolt_func, p)
        run_it.decorator = True
        return run_it
    return decorator

def before_all(func):
    func.before_all = True
    return func

def after_all(func):
    func.after_all = True
    return func

#>########### helpers ###########<#

def deep_merge(base, result):
    if base == None:
        return result
    if result == None:
        return base
    if not (isinstance(base, dict) and isinstance(result, dict)):
        if isinstance(base, list) and isinstance(result, list):
            return _combine_lists(base, result)
        return result
    for k, v in result.items():
        if k in base:
            if isinstance(v, dict) and isinstance(base[k], dict):
                base[k] = deep_merge(base[k], v)
            elif isinstance(v, list) and isinstance(base[k], list):
                base[k] = _combine_lists(base[k], v)
            else:
                base[k] = v
        else:
            base[k] = v
    return base

def _run_callables(cls, callables):
    for c in callables:
        if 'transforms_component' in c.__dict__:
            cls.component_proxy[c.transforms_component] = c(cls.component_proxy, cls.component_proxy.get(c.transforms_component))
        if 'custom_component' in c.__dict__:
            c(cls.component_proxy, getattr(cls, c.custom_component, None))
        if 'decorator' in c.__dict__:
            c(cls.component_proxy)

def _get_components_and_callables_from_parents(cls):
    components = {}
    callables = {
        "before_all": [],
        "regular": [],
        "after_all": [],
    }
    # get info of parent classes recursively
    for parent in reversed(cls.__bases__):
        if parent != object:
            cmp, cal = _get_components_and_callables_from_parents(parent)
            for ck, cv in cmp.items():
                components[ck] = cv
            callables['before_all'] += cal['before_all']
            callables['after_all'] += cal['after_all']
            callables['regular'] += cal['regular']
    # get info of this class
    for k, v in cls.__dict__.items():
        if k in component_names or k in components: #! custom components are currently ignored
            components[k] = v
        if callable(v) and ('transforms_component' in v.__dict__ or 'custom_component' in v.__dict__ or 'decorator' in v.__dict__):
            if 'custom_component' in v.__dict__:
                components[v.custom_component] = getattr(cls, v.custom_component, None)
            if getattr(v, 'before_all', False):
                callables["before_all"].append(v)
            elif getattr(v, 'after_all', False):
                callables["after_all"].append(v)
            else:
                callables["regular"].append(v)
    return (components, callables)

def _combine_lists(l1, l2):
    for e in (l1 + l2):
        if not isinstance(e, Hashable):
            return l1 + l2
    return list(set(l1 + l2))

def camel_case_to_snake_case(name: str) -> str:
    out_id = name[0].lower()
    for c in name[1:]:
        if c.isupper():
            out_id += '_' + c.lower()
        else:
            out_id += c
    return out_id

def _int_hash(s: str) -> int:
    hash_object = sha512()
    hash_object.update(s.encode('utf-8'))
    hex_digest = hash_object.hexdigest()
    int_digest = int(hex_digest, 16)
    truncated_int = int_digest & 4294967295
    if truncated_int > 2147483647:
        truncated_int -= 4294967296
    return truncated_int

def _get_mc_components(item: Components, removed_components: list[str]) -> dict:
    cmpnts = {}

    for k, v in item.__dict__.items():
        if k in component_names and v != None:
            cmpnts["minecraft:" + k] = v

    for remcmp in removed_components:
        if f'minecraft:{remcmp}' not in cmpnts:
            cmpnts[f'!minecraft:{remcmp}'] = {}

    return cmpnts
