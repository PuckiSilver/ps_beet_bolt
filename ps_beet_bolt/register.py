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
