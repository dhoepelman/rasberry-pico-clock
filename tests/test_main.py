from hamcrest import assert_that, equal_to

from main import gmt_to_local, is_dst


def test_is_dst():
    assert_that(is_dst((2022, 1, 1, 1, 0, 0, 0, 0)), equal_to(False))
    assert_that(is_dst((2022, 8, 1, 1, 0, 0, 0, 0)), equal_to(True))
    assert_that(is_dst((2022, 11, 1, 1, 0, 0, 0, 0)), equal_to(False))

    assert_that(is_dst((2022, 3, 27, 0, 59, 59, 0, 0)), equal_to(False))
    assert_that(is_dst((2022, 3, 27, 1, 0, 0, 0, 0)), equal_to(True))
    assert_that(is_dst((2023, 3, 26, 0, 59, 59, 0, 0)), equal_to(False))
    assert_that(is_dst((2023, 3, 26, 1, 0, 0, 0, 0)), equal_to(True))

    assert_that(is_dst((2022, 10, 30, 0, 59, 59, 0, 0)), equal_to(True))
    assert_that(is_dst((2022, 10, 30, 1, 0, 0, 0, 0)), equal_to(False))
    assert_that(is_dst((2023, 10, 29, 0, 59, 59, 0, 0)), equal_to(True))
    assert_that(is_dst((2023, 10, 29, 1, 0, 0, 0, 0)), equal_to(False))


def test_gmt_to_local():
    assert_that(gmt_to_local((2022, 1, 1, 1, 0, 0, 0, 0), 2), equal_to((2022, 1, 1, 3, 0, 0, 0, 0)))
    assert_that(gmt_to_local((2022, 1, 1, 23, 0, 0, 0, 0), 2), equal_to((2022, 1, 2, 1, 0, 0, 0, 0)))
    assert_that(gmt_to_local((2022, 1, 31, 23, 0, 0, 0, 0), 2), equal_to((2022, 2, 1, 1, 0, 0, 0, 0)))
    assert_that(gmt_to_local((2022, 12, 31, 20, 1, 2, 0, 0), 8), equal_to((2023, 1, 1, 4, 1, 2, 0, 0)))
