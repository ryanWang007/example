"""使用临时数据库测试，不会删除你自己的穿搭数据。"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from app import app


class LookbookTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.old_database = app.config["DATABASE"]
        app.config.update(TESTING=True, DATABASE=Path(self.temp.name) / "test.db")
        self.client = app.test_client()
        self.client.get("/")
        with self.client.session_transaction() as session:
            self.token = session["csrf_token"]

    def tearDown(self):
        app.config.update(TESTING=False, DATABASE=self.old_database)
        self.temp.cleanup()

    def post(self, path, **values):
        return self.client.post(path, data={"csrf_token": self.token, **values}, follow_redirects=True)

    def test_crud_and_persistence(self):
        response = self.post("/outfits/new", title="周末休闲装", occasion="周末", notes="白 T 恤")
        self.assertEqual(response.status_code, 200)
        self.assertIn("周末休闲装", response.get_data(as_text=True))
        # 新客户端仍能看到数据：数据保存于 SQLite，不是浏览器内存。
        self.assertIn("周末休闲装", app.test_client().get("/").get_data(as_text=True))
        self.assertEqual(self.client.get("/outfits/1/edit").status_code, 200)
        response = self.post("/outfits/1/edit", title="上课穿搭", occasion="学校", notes="蓝色牛仔裤")
        self.assertIn("上课穿搭", response.get_data(as_text=True))
        self.assertNotIn("周末休闲装", response.get_data(as_text=True))
        response = self.post("/outfits/1/delete")
        self.assertNotIn("上课穿搭", response.get_data(as_text=True))
        self.assertEqual(self.client.get("/outfits/1/edit").status_code, 404)

    def test_validation_and_safe_rendering(self):
        self.assertEqual(self.post("/outfits/new", title=" ", occasion="学校").status_code, 400)
        self.assertEqual(self.post("/outfits/new", title="x" * 81, occasion="学校").status_code, 400)
        response = self.post("/outfits/new", title="<script>alert(1)</script>", occasion="O'Brien")
        self.assertIn("&lt;script&gt;", response.get_data(as_text=True))
        self.assertNotIn("<script>alert(1)</script>", response.get_data(as_text=True))
        self.assertEqual(self.client.post("/outfits/1/delete").status_code, 400)
        self.assertEqual(self.client.get("/outfits/1/delete").status_code, 405)
        self.assertEqual(self.post("/outfits/999/delete").status_code, 404)


if __name__ == "__main__":
    unittest.main()
