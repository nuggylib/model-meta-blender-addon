import json

# Under the 64 KiB line limit of model-meta's asyncio reader, with room for the envelope.
PAGE_BYTES = 32_000


def page(count, build, cursor):
    """`build(i)` makes item `i`. Returns (items, the next cursor, or None after the last item).

    Always holds at least one item while any remain, even one over `PAGE_BYTES`.
    """
    items, size, index = [], 0, cursor
    while index < count:
        item = build(index)
        item_size = len(json.dumps(item, separators=(",", ":"))) + 1
        if items and size + item_size > PAGE_BYTES:
            break
        items.append(item)
        size += item_size
        index += 1
    return items, (index if index < count else None)
