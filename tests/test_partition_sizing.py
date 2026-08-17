from spark.etl.load import calculate_write_partitions

MIB = 1024 * 1024


def test_calculates_partitions_from_raw_batch_size():
    assert calculate_write_partitions(128 * MIB, 256 * MIB) == 1
    assert calculate_write_partitions(256 * MIB, 256 * MIB) == 1
    assert calculate_write_partitions(257 * MIB, 256 * MIB) == 2
    assert calculate_write_partitions(1024 * MIB, 256 * MIB) == 4


def test_honours_partition_bounds():
    assert calculate_write_partitions(1, 256 * MIB, min_partitions=2) == 2
    assert calculate_write_partitions(10 * 256 * MIB, 256 * MIB, max_partitions=3) == 3


def test_rejects_invalid_target_size():
    try:
        calculate_write_partitions(1, 0)
    except ValueError as error:
        assert "target_size_bytes" in str(error)
    else:
        raise AssertionError("expected invalid target size to fail")
