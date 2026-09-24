import csv
import json
import math
import os
import random


def calculate_distance(p1, p2):
  """Calculates Euclidean distance between two 2D points [x, y]."""
  return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def render_ascii_map(warehouses, agents, packages):
  """Renders a 10x10 ASCII map showing positions."""
  grid_size = 10
  grid = [[' . ' for _ in range(grid_size)] for _ in range(grid_size)]

  def scale(val):
    return min(grid_size - 1, max(0, int(val / 11)))

  for w_id, pos in warehouses.items():
    grid[scale(pos[1])][scale(pos[0])] = ' W '
  for a_id, pos in agents.items():
    grid[scale(pos[1])][scale(pos[0])] = ' A '
  for pkg in packages:
    dest = pkg['destination']
    grid[scale(dest[1])][scale(dest[0])] = ' D '

  print('\n--- ASCII MAP (A: Agent | W: Warehouse | D: Destination) ---')
  for row in reversed(grid):
    print(''.join(row))
  print('------------------------------------------------------------\n')


def parse_and_normalize_data(raw_data):
  """Normalizes both schema formats (base_case.json and data.json)."""
  warehouses = {}
  agents = {}
  packages = []

  if isinstance(raw_data.get('warehouses'), list):
    for w in raw_data['warehouses']:
      warehouses[w['id']] = w['location']
  elif isinstance(raw_data.get('warehouses'), dict):
    warehouses = raw_data['warehouses']

  if isinstance(raw_data.get('agents'), list):
    for a in raw_data['agents']:
      agents[a['id']] = a['location']
  elif isinstance(raw_data.get('agents'), dict):
    agents = raw_data['agents']

  for pkg in raw_data.get('packages', []):
    wh_id = pkg.get('warehouse') or pkg.get('warehouse_id')
    packages.append({
        'id': pkg['id'],
        'warehouse': wh_id,
        'destination': pkg['destination'],
    })

  return warehouses, agents, packages


def run_simulation(input_file, output_file='report.json'):
  """Reads the input JSON file, simulates delivery assignment & movement."""
  print(f'>>> Running Simulation for File: {input_file}')

  with open(input_file, 'r') as f:
    raw_data = json.load(f)

  warehouses, agents, packages = parse_and_normalize_data(raw_data)

  new_agent_id = 'A4'
  if new_agent_id not in agents:
    agents[new_agent_id] = [50, 50]
    print(f'[Event] New Agent {new_agent_id} joined mid-day at [50, 50].')

  render_ascii_map(warehouses, agents, packages)

  agent_positions = {a_id: list(pos) for a_id, pos in agents.items()}
  agent_metrics = {
      a_id: {'packages_delivered': 0, 'total_distance': 0.0}
      for a_id in agents
  }

  for pkg in packages:
    pkg_id = pkg['id']
    wh_id = pkg['warehouse']
    wh_pos = warehouses[wh_id]
    dest_pos = pkg['destination']

    best_agent = None
    min_pickup_dist = float('inf')

    for a_id, curr_pos in agent_positions.items():
      dist_to_wh = calculate_distance(curr_pos, wh_pos)
      if dist_to_wh < min_pickup_dist:
        min_pickup_dist = dist_to_wh
        best_agent = a_id

    pickup_dist = min_pickup_dist
    dropoff_dist = calculate_distance(wh_pos, dest_pos)
    trip_dist = pickup_dist + dropoff_dist
    delay_minutes = random.randint(3, 12)

    agent_metrics[best_agent]['packages_delivered'] += 1
    agent_metrics[best_agent]['total_distance'] += trip_dist
    agent_positions[best_agent] = list(dest_pos)

    print(
        f"  - Package {pkg_id} ({wh_id} -> {dest_pos}) assigned to"
        f' {best_agent} | Trip Distance: {trip_dist:.2f} | Delay:'
        f' {delay_minutes} min'
    )

  report = {}
  best_agent = None
  best_efficiency = float('inf')

  for a_id, stats in agent_metrics.items():
    pkgs = stats['packages_delivered']
    tot_dist = stats['total_distance']
    efficiency = round(tot_dist / pkgs, 2) if pkgs > 0 else 0.0

    report[a_id] = {
        'packages_delivered': pkgs,
        'total_distance': round(tot_dist, 2),
        'efficiency': efficiency,
    }

    if pkgs > 0 and efficiency < best_efficiency:
      best_efficiency = efficiency
      best_agent = a_id

  report['best_agent'] = best_agent

  with open(output_file, 'w') as f:
    json.dump(report, f, indent=4)
  print(f"\n[Success] Report saved to '{output_file}'")

  if best_agent:
    csv_filename = f"top_performer_{os.path.basename(input_file).split('.')[0]}.csv"
    with open(csv_filename, 'w', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(
          ['Agent', 'Packages Delivered', 'Total Distance', 'Efficiency']
      )
      writer.writerow([
          best_agent,
          report[best_agent]['packages_delivered'],
          report[best_agent]['total_distance'],
          report[best_agent]['efficiency'],
      ])
    print(
        f"[Success] Exported top performer ({best_agent}) to '{csv_filename}'\n"
    )

  return report


if __name__ == '__main__':
  base_case_data = {
      'warehouses': [
          {'id': 'W1', 'location': [0, 0]},
          {'id': 'W2', 'location': [50, 75]},
          {'id': 'W3', 'location': [100, 25]},
      ],
      'agents': [
          {'id': 'A1', 'location': [5, 5]},
          {'id': 'A2', 'location': [60, 60]},
          {'id': 'A3', 'location': [95, 30]},
      ],
      'packages': [
          {'id': 'P1', 'warehouse_id': 'W1', 'destination': [30, 40]},
          {'id': 'P2', 'warehouse_id': 'W2', 'destination': [70, 90]},
          {'id': 'P3', 'warehouse_id': 'W3', 'destination': [105, 20]},
          {'id': 'P4', 'warehouse_id': 'W1', 'destination': [10, 10]},
          {'id': 'P5', 'warehouse_id': 'W2', 'destination': [40, 80]},
      ],
  }
  with open('base_case.json', 'w') as f:
    json.dump(base_case_data, f, indent=4)

  pdf_data = {
      'warehouses': {'W1': [0, 0], 'W2': [50, 75], 'W3': [100, 25]},
      'agents': {'A1': [5, 5], 'A2': [60, 60], 'A3': [95, 30]},
      'packages': [
          {'id': 'P1', 'warehouse': 'W1', 'destination': [30, 40]},
          {'id': 'P2', 'warehouse': 'W2', 'destination': [70, 90]},
          {'id': 'P3', 'warehouse': 'W3', 'destination': [105, 20]},
          {'id': 'P4', 'warehouse': 'W1', 'destination': [10, 10]},
          {'id': 'P5', 'warehouse': 'W2', 'destination': [40, 80]},
      ],
  }
  with open('data.json', 'w') as f:
    json.dump(pdf_data, f, indent=4)

  report_base = run_simulation('base_case.json', 'report_base_case.json')
  report_data = run_simulation('data.json', 'report_data.json')

  print('================ FINAL REPORT SUMMARY ================')
  print(json.dumps(report_base, indent=4))
