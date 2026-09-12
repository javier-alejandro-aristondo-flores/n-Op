"""the token count a channel axis divides into at a given hidden width"""


def Token_Count(channel_count: int, hidden_channels: int) -> int:
    """how many tokens a channel axis holds at this hidden width, refusing what does not divide evenly"""
    if channel_count % hidden_channels != 0:
        raise ValueError(f"{channel_count} channels do not divide evenly into blocks of {hidden_channels}")
    return channel_count // hidden_channels
