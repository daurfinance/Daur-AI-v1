#!/usr/bin/env python3

import unittest
import os
import sys

# Добавляем корень проекта в пути импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class SimpleTest(unittest.TestCase):
    def test_simple(self):
        """Простой тест для проверки работы unittest"""
        self.assertEqual(1 + 1, 2)
        self.assertTrue(True)
        print("Простой тест выполнен успешно!")

if __name__ == '__main__':
    unittest.main(verbosity=2)
