from spark.etl.pipeline import YellowTaxiETLPipeline

def main():
    pipeline = YellowTaxiETLPipeline()
    pipeline.run()

if __name__ == "__main__":
    main()
