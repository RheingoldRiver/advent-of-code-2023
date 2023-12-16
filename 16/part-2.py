import json
import re
from copy import copy, deepcopy

from utils.grid.cell import Cell
from utils.grid.errors import MoveError
from utils.grid.grid import Grid
from utils.grid.pointer import Pointer


class Solver:
    empty_space = '.'
    mirror1 = '/'
    mirror2 = '\\'
    splitter_col = '|'
    splitter_row = '-'

    def __init__(self):
        with open('input.txt', 'r', encoding='utf-8') as f:
            self.lines = [line.strip() for line in f.readlines()]
        self._grid = Grid.read_from_lines(self.lines)
        self.grid = deepcopy(self._grid)

    def run(self):
        max_value = 0
        for i in range(self.grid.max_row + 1):
            result = self.run_trial(Cell(i, 0), 'RIGHT')
            max_value = max(max_value, result)
            result = self.run_trial(Cell(i, self.grid.max_col), 'LEFT')
            max_value = max(max_value, result)
        for i in range(self.grid.max_col + 1):
            result = self.run_trial(Cell(0, i), 'DOWN')
            max_value = max(max_value, result)
            result = self.run_trial(Cell(self.grid.max_row, i), 'UP')
            max_value = max(max_value, result)
        return max_value

    def run_trial(self, starting_square: Cell, starting_direction):
        self.grid = deepcopy(self._grid)
        total = 0
        first_pointer = self.grid.new_pointer(data=starting_direction)
        first_pointer.move_to(starting_square.row, starting_square.col)
        ptrs = [first_pointer]
        while True:
            ptrs_to_add = []
            ptrs_to_rm = []
            found_new_cell_this_round = False
            for ptr in ptrs:
                cur_direction = ptr.ptr_data
                square = ptr.cell

                # don't continue cycles
                if square.data.get(cur_direction) is not None:
                    ptrs_to_rm.append(ptr)
                    continue
                found_new_cell_this_round = True
                square.data.update({
                    cur_direction: True,
                    'found': True,
                })
                if square.value == self.empty_space:
                    continue
                if square.value == '-' and (cur_direction == 'LEFT' or cur_direction == 'RIGHT'):
                    continue
                if square.value == '|' and (cur_direction == 'UP' or cur_direction == 'DOWN'):
                    continue
                elif square.value == self.mirror1:  # '/'
                    if cur_direction == 'UP':
                        self.change_direction(ptr, 'RIGHT')
                    elif cur_direction == 'DOWN':
                        self.change_direction(ptr, 'LEFT')
                    elif cur_direction == 'LEFT':
                        self.change_direction(ptr, 'DOWN')
                    elif cur_direction == 'RIGHT':
                        self.change_direction(ptr, 'UP')
                elif square.value == self.mirror2:  # '\'
                    if cur_direction == 'UP':
                        self.change_direction(ptr, 'LEFT')
                    elif cur_direction == 'DOWN':
                        self.change_direction(ptr, 'RIGHT')
                    elif cur_direction == 'LEFT':
                        self.change_direction(ptr, 'UP')
                    elif cur_direction == 'RIGHT':
                        self.change_direction(ptr, 'DOWN')
                elif square.value == '|':
                    self.change_direction(ptr, 'UP')
                    new_ptr = ptr.clone()
                    self.change_direction(new_ptr, 'DOWN')
                    ptrs_to_add.append(new_ptr)
                elif square.value == '-':
                    self.change_direction(ptr, 'LEFT')
                    new_ptr = ptr.clone()
                    self.change_direction(new_ptr, 'RIGHT')
                    ptrs_to_add.append(new_ptr)
            if not found_new_cell_this_round:
                break
            ptrs = ptrs + ptrs_to_add
            for ptr in ptrs:
                cur_direction = ptr.ptr_data
                if cur_direction == 'RIGHT':
                    try:
                        ptr.move_right()
                    except MoveError:
                        if ptr not in ptrs_to_rm:
                            ptrs_to_rm.append(ptr)
                        continue
                elif cur_direction == 'UP':
                    try:
                        ptr.move_up()
                    except MoveError:
                        if ptr not in ptrs_to_rm:
                            ptrs_to_rm.append(ptr)
                        continue
                elif cur_direction == 'DOWN':
                    try:
                        ptr.move_down()
                    except MoveError:
                        if ptr not in ptrs_to_rm:
                            ptrs_to_rm.append(ptr)
                        continue
                elif cur_direction == "LEFT":
                    try:
                        ptr.move_left()
                    except MoveError:
                        if ptr not in ptrs_to_rm:
                            ptrs_to_rm.append(ptr)
                        continue
            for ptr in ptrs_to_rm:
                ptrs.remove(ptr)

        # count cells
        for cell in self.grid.all_grid_cells():
            if cell.data.get('found'):
                total += 1
        return total

    def change_direction(self, ptr: Pointer, new_direction):
        ptr.set_ptr_data(new_direction)

if __name__ == '__main__':
    print(Solver().run())
