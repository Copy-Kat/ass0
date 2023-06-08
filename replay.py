import polars as pl
import vi

df = pl.read_csv("data.csv")

replay = vi.TimeMachine(df, ["images/bird.png"], window=vi.Window())

replay.run()

