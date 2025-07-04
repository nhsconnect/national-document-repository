from itertools import islice
from typing import Iterable, Iterator, List, TypeVar

T = TypeVar("T")


def batch(iterable: Iterable[T], size: int) -> Iterator[List[T]]:
    """
    Splits an iterable into chunks (batches) of a specified size.

    Args:
        iterable: An iterable of any type to be batched.
        size: The maximum size of each batch.

    Yields:
        Lists of up to `size` items of type T each.
    """
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk
