from spark.etl.pipeline import YellowTaxiETLPipeline


def main() -> None:
    """Run only the newest raw file not yet recorded in processed metadata."""
    YellowTaxiETLPipeline().run()

if __name__ == "__main__":
    main()
