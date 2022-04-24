from apgorm import Model, types

from ivycraft.database.converters import DecimalC


class User(Model):
    discord_id = types.Numeric().field().with_converter(DecimalC)
    minecraft_uuid = types.Text().nullablefield()

    primary_key = (discord_id,)
