# ps_beet_bolt

A collection of my beet and bolt plugins

## bolt-item

To be able to use `on_equip`, `on_unequip`, `on_attack`, `on_attacked`, `on_consume` or `on_tick`, you have to require the specific plugin in your beet json/yaml/yml file.

You also need to add the respecive library for `on_attack` and `on_attacked` ([argon](https://github.com/PuckiSilver/mc-argon)) or `on_equip` and `on_unequip` ([tungsten](https://github.com/ps-dps/mc-Tungsten)) to work
```yml
require:
  - bolt
  - ps_beet_bolt.register.bolt_item # on_consume, on_tick
  - ps_beet_bolt.register.tungsten # on_equip, on_unequip
  - ps_beet_bolt.register.argon # on_attack, on_attacked

data_pack:
  load:
    - libraries/mc-tungsten* # on_equip, on_unequip
    - libraries/mc-argon* # on_attack, on_attacked
    - src
```

Example code with explanations:
```py
from ps_beet_bolt.bolt_item import bolt_item, transformer, custom_component, event_decorator
from tungsten:decorators import on_equip, on_unequip
from argon:decorators import on_attack, on_attacked
from bolt_item:decorators import on_consume, on_tick


@event_decorator
def on_block_interact(func, item):
    """
    You can use the @event_decorator to add any functionality you like. You can modify
    the items components, and read any information.
    """
    path = f'{item.namespace}:bolt-item/item/{item.id}/on_block_interact/{func.__name__}'
    advancement path { "criteria": { "criteria": {
        "trigger": "minecraft:item_used_on_block",
        "conditions": { "location": [{
            "condition": "minecraft:match_tool",
            "predicate": {
                "items": item.base_item,
                "components": {
                    "custom_data": {
                        "bolt-item": { "id": f'{item.namespace}:{item.id}' }
                    }
                }
            }}]
        }}},
        "rewards": { "function": path }
    }
    function path:
        advancement revoke @s only path
        func()

class ParentItem:
    """
    All the special decorators, vanilla components and custom components get
    inherited, even if the parent class is not an item itself.
    """
    lore = [{"text":"MyPack","color":"blue"}]

    @transformer(component = "item_name")
    def item_name_transformer(item, item_name):
        """
        A @transformer takes the previous value of a components and sets it to the return value.
        You can chain as many transformer after each other as you like.
        They are applied from parent to child, from top to bottom.
        """
        return {"text":item_name,"color":"red"}

@bolt_item
class ActualItem(ParentItem):
    """
    Any classes with the @bolt_item decorator are treated as item and get a .components and a .base_item
    attribute set. Those can be used to create loot tables or other stuff.
    """
    item_name = "Awesome Item"
    story = "This item special"
    consumable = {}
    equippable = {"slot":"head"}

    @on_block_interact
    def say_hi_it_interacted_with_block():
        """
        This is the custom event decorator added earlier in the file, for more examples look through
        this libraries bolt code.
        """
        say I INTERACTED WITH THE BLOCK USING THIS ITEM

    @custom_component(component = "story")
    def story_handler(item, story):
        """
        @custom_component handlers take an attribute and can modify the item's components based on
        that input.
        """
        item.lore = [{"text":story, "color":"gray"}] + item.get("lore", [])

    @on_consume(return_item = True)
    def infinitely_eddible():
        """
        @on_consume runs when the item is consumed. If return_item is set to True, the item stays in
        the players inventory. This can be used for right click abilities with cooldown provided by
        the use_cooldown component.
        """
        say THIS ITEM WAS CONSUMED, THIS ITEM IS NOT REMOVED FROM THE INVENTORY HOWEVER SINCE RETURN ITEM IS TRUE, THIS CAN BE USED TO TRIGGER A COOL DOWN ON RIGHT CLICK

    @on_tick(interval = "10s", full_slot = "armor.head")
    def yap_every_10_seconds():
        """
        This uses schedules to run this command in the given interval when it's equipped on the given slot.
        """
        say ANOTHER 10 SECONDS HAVE PASSED AND I AM WEARING THIS ITEM ON MY HEAD

    @on_equip(slot = "head")
    def add_resistance():
        """
        @on_unequip requires tungsten. This function runs when a player unequips this item from the given slot.
        """
        effect give @s resistance infinite 1

    @on_unequip(slot = "head")
    def remove_resistance():
        """
        @on_equip requires tungsten. This function runs when a player equips this item in the given slot.
        """
        effect clear @s resistance

    @on_attack(slot = "mainhand")
    def attack_my_enemies():
        """
        @on_attack requires argon. This function runs when a player attacks an enemy with this item in
        the given slot. @s is enemy; on attacker is player.
        """
        say I AM AN ATTACKED ENEMY
        on attacker say I AM THE PLAYER WHO ATTACKED THE ENEMY WITH THIS ITEM IN THEIR MAINHAND

    @on_attacked(full_slot = "weapon.mainhand")
    def attacked_by_enemies():
        """
        @on_attacked requires argon. This function runs when a player is attacked with this item in
        the given slot. @s is player; on attacker is enemy.
        """
        say I AM THE PLAYER WHO GOT ATTACKED WHILE HOLDING THIS ITEM IN MY MAINHAND
        on attacker say I AM THE ENEMY WHO DID IT
```
