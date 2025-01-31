from beet import Context
from beet.contrib.load import load

def tungsten(ctx: Context):
    ctx.require(
        load(
            data_pack={
                "data/tungsten/modules": "@ps_beet_bolt/tungsten",
            },
        ),
    )

def argon(ctx: Context):
    ctx.require(
        load(
            data_pack={
                "data/argon/modules": "@ps_beet_bolt/argon",
            },
        ),
    )

def bolt_item(ctx: Context):
    ctx.require(
        load(
            data_pack={
                "data/bolt_item/modules": "@ps_beet_bolt/bolt_item",
            },
        ),
    )
