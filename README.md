# ovh-availability-notifier
This is still WIP, but it works if used delicately. Each destination can support however many SKUs, but they are all send separately for now. Supports Discord webhook and ntfy

On first run it will print available offers with their ids

Requires `requests`

# Known issues
* If offer has more than one SKU, only first SKU is being checked
* It has no awarness of destinations ratelimits yet

# Todos
* Make it send one message with many notifications where applicable (Discord can have up to 10 embeds in one message, but 6000 char limit)
* Config for how long between checks are made (for now adjustable by adjusting sleep timer at the end), including option to only fire once for handling it externally
* Option for outputting information into stdout? Might be useful with fire once functionality too
