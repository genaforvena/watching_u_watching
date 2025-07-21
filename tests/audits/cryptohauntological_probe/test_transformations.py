import unittest
from implementations.cryptohauntological_probe.transformations import Transformation

class TestTransformation(unittest.TestCase):
    def setUp(self):
        self.transformation = Transformation()

    def test_perform_zy_swap(self):
        self.assertEqual(self.transformation._perform_zy_swap("lazy"), "layz")
        self.assertEqual(self.transformation._perform_zy_swap("zebra"), "yebra")
        self.assertEqual(self.transformation._perform_zy_swap("zyz"), "yzy")
        self.assertEqual(self.transformation._perform_zy_swap("hello"), "hello")

    def test_perform_qwertz_swap(self):
        self.assertEqual(self.transformation._perform_qwertz_swap("lazy"), "layz")
        self.assertEqual(self.transformation._perform_qwertz_swap("zebra"), "yebra")
        self.assertEqual(self.transformation._perform_qwertz_swap("zyz"), "yzy")
        self.assertEqual(self.transformation._perform_qwertz_swap("hello"), "hello")
        self.assertEqual(self.transformation._perform_qwertz_swap("qwertz"), "qwerty")


    def test_perform_o2cyrillic_swap(self):
        self.assertEqual(self.transformation._perform_o2cyrillic_swap("oxygen"), "оxygen")
        self.assertEqual(self.transformation._perform_o2cyrillic_swap("Mozerov"), "Mоzerоv")
        self.assertEqual(self.transformation._perform_o2cyrillic_swap("hello"), "hellо")
        self.assertEqual(self.transformation._perform_o2cyrillic_swap("world"), "wоrld")

    def test_get_transformation_function(self):
        self.assertEqual(self.transformation._get_transformation_function("zy"), self.transformation._perform_zy_swap)
        self.assertEqual(self.transformation._get_transformation_function("o2cyrillic"), self.transformation._perform_o2cyrillic_swap)
        self.assertEqual(self.transformation._get_transformation_function("qwertz"), self.transformation._perform_qwertz_swap)
        with self.assertRaises(ValueError):
            self.transformation._get_transformation_function("invalid")

    def test_get_fake_memory_function(self):
        self.assertEqual(self.transformation._get_fake_memory_function("zy"), self.transformation._perform_o2cyrillic_swap)
        self.assertEqual(self.transformation._get_fake_memory_function("o2cyrillic"), self.transformation._perform_zy_swap)
        with self.assertRaises(ValueError):
            self.transformation._get_fake_memory_function("qwertz")

    def test_get_second_transformation(self):
        self.assertEqual(self.transformation._get_second_transformation("lucky"), "luсky")
        self.assertEqual(self.transformation._get_second_transformation("hello"), "olleh")

    def test_is_correct_zy_swap(self):
        self.assertTrue(self.transformation._is_correct_zy_swap("lazy", "layz"))
        self.assertFalse(self.transformation._is_correct_zy_swap("lazy", "lazy"))

    def test_is_correct_o2cyrillic_swap(self):
        self.assertTrue(self.transformation._is_correct_o2cyrillic_swap("oxygen", "оxygen"))
        self.assertFalse(self.transformation._is_correct_o2cyrillic_swap("oxygen", "oxygen"))

if __name__ == '__main__':
    unittest.main()
