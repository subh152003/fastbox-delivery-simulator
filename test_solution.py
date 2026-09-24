import os
import unittest
from solution import calculate_distance, parse_and_normalize_data, run_simulation


class TestFastBoxSimulator(unittest.TestCase):

  def test_calculate_distance(self):
    dist = calculate_distance([0, 0], [3, 4])
    self.assertAlmostEqual(dist, 5.0, places=2)

  def test_parse_list_schema(self):
    raw_data = {
        'warehouses': [{'id': 'W1', 'location': [0, 0]}],
        'agents': [{'id': 'A1', 'location': [5, 5]}],
        'packages': [
            {'id': 'P1', 'warehouse_id': 'W1', 'destination': [10, 10]}
        ],
    }
    warehouses, agents, packages = parse_and_normalize_data(raw_data)
    self.assertEqual(warehouses['W1'], [0, 0])
    self.assertEqual(agents['A1'], [5, 5])
    self.assertEqual(packages[0]['warehouse'], 'W1')

  def test_parse_dict_schema(self):
    raw_data = {
        'warehouses': {'W1': [0, 0]},
        'agents': {'A1': [5, 5]},
        'packages': [{'id': 'P1', 'warehouse': 'W1', 'destination': [10, 10]}],
    }
    warehouses, agents, packages = parse_and_normalize_data(raw_data)
    self.assertEqual(warehouses['W1'], [0, 0])
    self.assertEqual(agents['A1'], [5, 5])
    self.assertEqual(packages[0]['warehouse'], 'W1')

  def test_simulation_execution(self):
    report = run_simulation('base_case.json', 'test_output.json')
    self.assertIsNotNone(report)
    self.assertIn('best_agent', report)
    if os.path.exists('test_output.json'):
      os.remove('test_output.json')


if __name__ == '__main__':
  unittest.main()
