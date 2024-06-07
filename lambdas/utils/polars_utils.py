from typing import Callable

import polars as pl
import polars.selectors as column_select

CastDecimalToFloat: pl.Expr = column_select.by_dtype(pl.datatypes.Decimal).cast(
    pl.Float64
)


def handle_empty_input(lambda_func: Callable):
    def interceptor(df: pl.DataFrame) -> pl.DataFrame:
        if df.is_empty():
            return df
        return lambda_func(df)

    return interceptor
