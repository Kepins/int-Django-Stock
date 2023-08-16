import datetime
import json
from unittest import mock

from django.contrib.auth import authenticate
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from .factories import UserFactory, setup_test_environment, StockFactory, StockTimeSeriesFactory

from ..models import User, Stock, StockTimeSeries, Follow
from ..tasks import update_time_series


class UserListTest(TestCase):
    NUM_USERS = 10

    def setUp(self):
        setup_test_environment()
        self.admin = UserFactory(is_admin=True)
        self.admin.set_password("adminpasswd")
        self.admin.save()
        self.bearer_header = {"Authorization": f"Bearer {AccessToken.for_user(self.admin)}"}
        for _ in range(self.NUM_USERS - 1):
            UserFactory().save()

    def test_get(self):
        resp = self.client.get(
            "/users/",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(len(resp.data), self.NUM_USERS)

    def test_post(self):
        resp = self.client.post(
            "/users/",
            json.dumps(
                {
                    "first_name": "Maciej",
                    "last_name": "Tester",
                    "email": "Tester@EXample.com",
                    "password": "Password123",
                }
            ),
            content_type="application/json",
        )
        self.assertEquals(resp.status_code, 201)
        self.assertEquals(resp.data["first_name"], "Maciej")
        self.assertEquals(resp.data["last_name"], "Tester")
        self.assertEquals(resp.data["email"], "Tester@example.com")
        self.assertEquals(resp.data["is_admin"], False)
        self.assertIsNotNone(authenticate(username="Tester@example.com", password="Password123"))
        user = User.objects.get(pk=resp.data["id"])
        self.assertEquals(user.first_name, "Maciej")
        self.assertEquals(user.last_name, "Tester")
        self.assertEquals(user.is_active, True)
        self.assertEquals(user.is_admin, False)


class UserDetailTest(TestCase):
    def setUp(self):
        setup_test_environment()
        self.user = UserFactory()
        self.user.save()
        self.bearer_header = {"Authorization": f"Bearer {AccessToken.for_user(self.user)}"}

    def test_get(self):
        resp = self.client.get(
            f"/users/{self.user.id}/",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["id"], self.user.id)

    def test_post(self):
        resp = self.client.post(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciej",
                    "last_name": "Tester",
                    "email": "Tester@EXample.com",
                    "password": "Password123",
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        resp = self.client.put(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciej",
                    "last_name": "Tester",
                    "email": "Tester@EXample.com",
                    "password": "Password123",
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):
        resp = self.client.patch(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciejo",
                    "last_name": "Testero",
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.data["first_name"], "Maciejo")
        self.assertEquals(resp.data["last_name"], "Testero")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.user.id)
        self.assertEquals(user.first_name, "Maciejo")
        self.assertEquals(user.last_name, "Testero")

    def test_patch2(self):
        resp = self.client.patch(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciejo",
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.data["first_name"], "Maciejo")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.user.id)
        self.assertEquals(user.first_name, "Maciejo")

    def test_patch3(self):
        resp = self.client.patch(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciejo",
                    "last_name": "Testero",
                    "password": "new_passwd",
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.data["first_name"], "Maciejo")
        self.assertEquals(resp.data["last_name"], "Testero")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(authenticate(username=self.user.email, password="new_passwd"))
        user = User.objects.get(pk=self.user.id)
        self.assertEquals(user.first_name, "Maciejo")
        self.assertEquals(user.last_name, "Testero")

    def test_delete(self):
        resp = self.client.delete(
            f"/users/{self.user.id}/",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.user.id)


class UserListNotAuthenticatedTest(TestCase):
    NUM_USERS = 10
    wrong_bearer_header = {"Authorization": f"Bearer 1234"}

    def setUp(self):
        setup_test_environment()
        for _ in range(self.NUM_USERS):
            UserFactory().save()

    def test_get_no_header(self):
        resp = self.client.get(
            "/users/",
        )
        self.assertEquals(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_wrong_header(self):
        resp = self.client.get(
            "/users/",
            headers=self.wrong_bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class UserListNotAdminTest(TestCase):
    def setUp(self):
        setup_test_environment()
        self.user = UserFactory(is_admin=False)
        self.user.save()
        self.bearer_header = {"Authorization": f"Bearer {AccessToken.for_user(self.user)}"}

    def test_get(self):
        resp = self.client.get(
            "/users/",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_403_FORBIDDEN)


class UserDetailNotAuthenticatedTest(TestCase):
    wrong_bearer_header = {"Authorization": f"Bearer 1234"}

    def setUp(self):
        setup_test_environment()
        self.user = UserFactory()
        self.user.save()

    def test_get_no_header(self):
        resp = self.client.get(
            f"/users/{self.user.id}/",
        )
        self.assertEquals(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_wrong_header(self):
        resp = self.client.get(
            f"/users/{self.user.id}/",
            headers=self.wrong_bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_no_header(self):
        resp = self.client.patch(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciejo",
                    "last_name": "Testero",
                }
            ),
            content_type="application/json",
        )
        self.assertEquals(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_wrong_header(self):
        resp = self.client.patch(
            f"/users/{self.user.id}/",
            json.dumps(
                {
                    "first_name": "Maciejo",
                    "last_name": "Testero",
                }
            ),
            content_type="application/json",
            headers=self.wrong_bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_no_header(self):
        resp = self.client.delete(
            f"/users/{self.user.id}/",
        )
        self.assertEquals(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_wrong_header(self):
        resp = self.client.delete(
            f"/users/{self.user.id}/",
            headers=self.wrong_bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailForbiddenTest(TestCase):
    def setUp(self):
        setup_test_environment()
        self.user_accessed = UserFactory()
        self.user_accessed.save()
        self.user_accessing = UserFactory()
        self.user_accessing.save()
        self.bearer_header = {"Authorization": f"Bearer {AccessToken.for_user(self.user_accessing)}"}

    def test_get(self):
        resp = self.client.get(
            f"/users/{self.user_accessed.id}/",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch(self):
        resp = self.client.patch(
            f"/users/{self.user_accessed.id}/",
            json.dumps(
                {
                    "first_name": "Maciejo",
                    "last_name": "Testero",
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete(self):
        resp = self.client.delete(
            f"/users/{self.user_accessed.id}/",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_403_FORBIDDEN)


class TaskUpdateTimeSeriesValidTest(TestCase):
    def setUp(self):
        setup_test_environment()
        self.stock = StockFactory()
        self.stock.save()
        self.response_mock = mock.Mock()
        self.response_mock.json = lambda: {
            "meta": {
                "symbol": self.stock.symbol,
                "interval": "1day",
                "currency": self.stock.currency,
                "exchange_timezone": "America/New_York",
                "exchange": self.stock.exchange_name,
                "mic_code": "XNCM",
                "type": self.stock.type_of_stock,
            },
            "values": [
                {
                    "datetime": "2023-08-08",
                    "open": "2.36000",
                    "high": "2.42000",
                    "low": "2.18000",
                    "close": "2.18000",
                    "volume": "6200",
                },
                {
                    "datetime": "2023-08-07",
                    "open": "2.45000",
                    "high": "2.65000",
                    "low": "2.31000",
                    "close": "2.31000",
                    "volume": "18500",
                },
                {
                    "datetime": "2023-08-04",
                    "open": "2.51000",
                    "high": "2.86000",
                    "low": "2.50000",
                    "close": "2.51000",
                    "volume": "36700",
                },
            ],
            "status": "ok",
        }
        self.response_mock.status_code = 200

    @mock.patch("requests.get")
    def test_update_first(self, mock_get):
        self.stock.last_update_date = None
        self.stock.save()

        mock_get.return_value = self.response_mock
        update_time_series.delay(self.stock.symbol)

        stock_time_series = StockTimeSeries.objects.all()
        self.assertEquals(len(stock_time_series), 3)
        self.assertEquals(stock_time_series[0].recorded_date, datetime.date(year=2023, month=8, day=8))
        self.assertEquals(stock_time_series[0].stock, self.stock)
        self.assertAlmostEquals(stock_time_series[0].open, 2.36)
        self.assertAlmostEquals(stock_time_series[0].close, 2.18)
        self.assertAlmostEquals(stock_time_series[0].low, 2.18)
        self.assertAlmostEquals(stock_time_series[0].high, 2.42)
        self.assertEquals(stock_time_series[0].volume, 6200)
        self.assertEquals(stock_time_series[1].recorded_date, datetime.date(year=2023, month=8, day=7))
        self.assertEquals(stock_time_series[2].recorded_date, datetime.date(year=2023, month=8, day=4))

    @mock.patch("requests.get")
    def test_update_already_up_to_date(self, mock_get):
        self.stock.last_update_date = datetime.date(year=2023, month=8, day=8)
        self.stock.save()

        sts = StockTimeSeriesFactory()
        sts.stock = self.stock
        sts.recorded_date = datetime.date(year=2023, month=8, day=8)
        sts.save()

        mock_get.return_value = self.response_mock
        update_time_series.delay(self.stock.symbol)

        stock_time_series = StockTimeSeries.objects.all()
        self.assertEquals(len(stock_time_series), 1)
        self.assertEquals(stock_time_series.first(), sts)

    @mock.patch("requests.get")
    def test_update_one_new(self, mock_get):
        self.stock.last_update_date = datetime.date(year=2023, month=8, day=7)
        self.stock.save()

        sts = StockTimeSeriesFactory()
        sts.stock = self.stock
        sts.recorded_date = datetime.date(year=2023, month=8, day=7)
        sts.save()

        mock_get.return_value = self.response_mock
        update_time_series.delay(self.stock.symbol)

        stock_time_series = StockTimeSeries.objects.all()
        self.assertEquals(len(stock_time_series), 2)
        self.assertEquals(stock_time_series[1].recorded_date, datetime.date(year=2023, month=8, day=8))
        self.assertEquals(stock_time_series[1].stock, self.stock)
        self.assertAlmostEquals(stock_time_series[1].open, 2.36)
        self.assertAlmostEquals(stock_time_series[1].close, 2.18)
        self.assertAlmostEquals(stock_time_series[1].low, 2.18)
        self.assertAlmostEquals(stock_time_series[1].high, 2.42)
        self.assertEquals(stock_time_series[1].volume, 6200)
        self.assertEquals(stock_time_series[0], sts)

    @mock.patch("requests.get")
    def test_update_more_new(self, mock_get):
        self.stock.last_update_date = datetime.date(year=2023, month=8, day=4)
        self.stock.save()

        sts = StockTimeSeriesFactory()
        sts.stock = self.stock
        sts.recorded_date = datetime.date(year=2023, month=8, day=4)
        sts.save()

        mock_get.return_value = self.response_mock
        update_time_series.delay(self.stock.symbol)

        stock_time_series = StockTimeSeries.objects.all()
        self.assertEquals(len(stock_time_series), 3)
        sts_08_08 = StockTimeSeries.objects.get(recorded_date=datetime.date(year=2023, month=8, day=8))
        self.assertEquals(sts_08_08.stock, self.stock)
        self.assertAlmostEquals(sts_08_08.open, 2.36)
        self.assertAlmostEquals(sts_08_08.close, 2.18)
        self.assertAlmostEquals(sts_08_08.low, 2.18)
        self.assertAlmostEquals(sts_08_08.high, 2.42)
        self.assertEquals(sts_08_08.volume, 6200)
        sts_08_07 = StockTimeSeries.objects.get(recorded_date=datetime.date(year=2023, month=8, day=7))
        self.assertEquals(sts_08_07.stock, self.stock)
        self.assertAlmostEquals(sts_08_07.open, 2.45)
        self.assertAlmostEquals(sts_08_07.close, 2.31)
        self.assertAlmostEquals(sts_08_07.low, 2.31)
        self.assertAlmostEquals(sts_08_07.high, 2.65)
        self.assertEquals(sts_08_07.volume, 18500)
        self.assertEquals(stock_time_series[0], sts)


class StockPricesTest(TestCase):
    def setUp(self):
        setup_test_environment()
        self.admin = UserFactory(is_admin=True)
        self.admin.set_password("adminpasswd")
        self.admin.save()
        self.bearer_header = {"Authorization": f"Bearer {AccessToken.for_user(self.admin)}"}

    def test(self):
        # stock1
        stock1 = StockFactory()
        stock1.last_update_date = datetime.date(year=2023, month=8, day=8)
        stock1.save()

        timeseries1_1 = StockTimeSeriesFactory()
        timeseries1_1.volume = 999
        timeseries1_1.recorded_date = datetime.date(year=2023, month=8, day=7)
        timeseries1_1.stock = stock1
        timeseries1_1.save()

        timeseries1_2 = StockTimeSeriesFactory()
        timeseries1_2.volume = 80
        timeseries1_2.recorded_date = datetime.date(year=2023, month=8, day=8)
        timeseries1_2.stock = stock1
        timeseries1_2.save()

        # stock2
        stock2 = StockFactory()
        stock2.last_update_date = None
        stock2.save()

        # stock3
        stock3 = StockFactory()
        stock3.last_update_date = datetime.date(year=2023, month=8, day=7)
        stock3.save()

        timeseries3_1 = StockTimeSeriesFactory()
        timeseries3_1.volume = 80
        timeseries3_1.recorded_date = datetime.date(year=2023, month=8, day=6)
        timeseries3_1.stock = stock3
        timeseries3_1.save()

        timeseries3_2 = StockTimeSeriesFactory()
        timeseries3_2.volume = 100
        timeseries3_2.recorded_date = datetime.date(year=2023, month=8, day=7)
        timeseries3_2.stock = stock3
        timeseries3_2.save()

        resp = self.client.get(
            "/stock/prices/",
            headers=self.bearer_header,
        )

        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(len(resp.data["results"]), 2)
        self.assertEquals(resp.data["results"][0]["latest_data"]["volume"], 100)
        self.assertEquals(resp.data["results"][1]["latest_data"]["volume"], 80)

    def test_unauthorized(self):
        resp = self.client.get(
            "/stock/prices/",
        )
        self.assertEquals(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination(self):
        for i in range(47):
            stock = StockFactory()
            stock.last_update_date = datetime.date(year=2023, month=8, day=8)
            stock.save()
            timeseries = StockTimeSeriesFactory()
            timeseries.stock = stock
            timeseries.recorded_date = datetime.date(year=2023, month=8, day=8)
            timeseries.save()

        resp = self.client.get(
            "/stock/prices/",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(len(resp.data["results"]), 20)

        resp = self.client.get(
            "/stock/prices/?page=1",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(len(resp.data["results"]), 20)

        resp = self.client.get(
            "/stock/prices/?page=2",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(len(resp.data["results"]), 20)

        resp = self.client.get(
            "/stock/prices/?page=3",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(len(resp.data["results"]), 7)


class FollowTest(TestCase):
    def setUp(self):
        setup_test_environment()
        self.user = UserFactory(is_admin=True)
        self.user.set_password("adminpasswd")
        self.user.save()
        self.bearer_header = {"Authorization": f"Bearer {AccessToken.for_user(self.user)}"}

    def test_follow_stock_exists_not_following(self):
        stock = StockFactory()
        stock.save()

        resp = self.client.post(
            f"/stock/follow/",
            json.dumps(
                {
                    "stock": stock.pk,
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )

        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(Follow.objects.get(user=self.user, stock=stock))

    def test_follow_stock_exists_already_following(self):
        stock = StockFactory()
        stock.save()

        self.user.follows.add(stock)
        self.user.save()

        resp = self.client.post(
            f"/stock/follow/",
            json.dumps(
                {
                    "stock": stock.pk,
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )

        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(Follow.objects.get(user=self.user, stock=stock))

    def test_follow_stock_not_exists(self):
        resp = self.client.post(
            f"/stock/follow/",
            json.dumps(
                {
                    "stock": 1,
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )

        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_exists(self):
        stock = StockFactory()
        stock.save()

        self.user.follows.add(stock)
        self.user.save()

        resp = self.client.delete(
            f"/stock/follow/",
            json.dumps(
                {
                    "stock": stock.pk,
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )

        self.assertEquals(resp.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Follow.DoesNotExist):
            Follow.objects.get(user=self.user, stock=stock)

    def test_unfollow_doesnt_exist(self):
        stock = StockFactory()
        stock.save()

        resp = self.client.delete(
            f"/stock/follow/",
            json.dumps(
                {
                    "stock": stock.pk,
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )

        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)
        with self.assertRaises(Follow.DoesNotExist):
            Follow.objects.get(user=self.user, stock=stock)


class RequestTest(TestCase):
    def setUp(self):
        setup_test_environment()
        self.user = UserFactory(is_admin=True)
        self.user.set_password("adminpasswd")
        self.user.save()
        self.bearer_header = {"Authorization": f"Bearer {AccessToken.for_user(self.user)}"}

    @mock.patch("requests.get")
    def test_stock_available_in_api(self, mock_get):
        stock = StockFactory.build()

        stocks_response_mock = mock.Mock()
        stocks_response_mock.status_code = 200
        stocks_response_mock.json = lambda: {
            "data": [
                {
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "currency": stock.currency.name,
                    "exchange": stock.exchange_name,
                    "mic_code": "XNCM",
                    "country": stock.country.name,
                    "type": stock.type_of_stock,
                }
            ],
            "status": "ok",
        }
        stocktimeseries_response_mock = mock.Mock()
        stocktimeseries_response_mock.status_code = 200
        stocktimeseries_response_mock.json = lambda: {
            "meta": {
                "symbol": stock.symbol,
                "interval": "1day",
                "currency": stock.currency,
                "exchange_timezone": "America/New_York",
                "exchange": stock.exchange_name,
                "mic_code": "XNCM",
                "type": stock.type_of_stock,
            },
            "values": [
                {
                    "datetime": "2023-08-08",
                    "open": "2.36000",
                    "high": "2.42000",
                    "low": "2.18000",
                    "close": "2.18000",
                    "volume": "6200",
                }
            ],
            "status": "ok",
        }
        mock_get.side_effect = [stocks_response_mock, stocktimeseries_response_mock]

        resp = self.client.post(
            f"/stock/request/",
            json.dumps(
                {
                    "symbol": stock.symbol,
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )

        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)
        stock = Stock.objects.get(symbol=stock.symbol)
        self.assertEquals(stock.latest_time_series.recorded_date, datetime.date(year=2023, month=8, day=8))

    @mock.patch("requests.get")
    def test_stock_not_available_in_api(self, mock_get):
        stock = StockFactory.build()

        stocks_response_mock = mock.Mock()
        stocks_response_mock.status_code = 200
        stocks_response_mock.json = lambda: {
            "data": [],
            "status": "ok",
        }
        mock_get.side_effect = [stocks_response_mock]

        resp = self.client.post(
            f"/stock/request/",
            json.dumps(
                {
                    "symbol": stock.symbol,
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )

        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)
        with self.assertRaises(Stock.DoesNotExist):
            Stock.objects.get(symbol=stock.symbol)

    def test_stock_already_in_db(self):
        stock = StockFactory()
        stock.save()

        resp = self.client.post(
            f"/stock/request/",
            json.dumps(
                {
                    "symbol": stock.symbol,
                }
            ),
            content_type="application/json",
            headers=self.bearer_header,
        )
        self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized(self):
        stock = StockFactory.build()

        resp = self.client.post(
            f"/stock/request/",
            json.dumps(
                {
                    "symbol": stock.symbol,
                }
            ),
            content_type="application/json",
        )
        self.assertEquals(resp.status_code, status.HTTP_401_UNAUTHORIZED)
