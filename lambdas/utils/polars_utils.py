import polars as pl
import polars.selectors as column_select

CastDecimalToFloat: pl.Expr = column_select.by_dtype(pl.datatypes.Decimal).cast(
    pl.Float64
)
