from functools import cache
import numpy as np

@cache
def get_adjacency_matrix(size: int) -> np.ndarray:
    total = size * size

    A = np.zeros((total, total), dtype=int)

    for row in range(size):
        for col in range(size):

            i = row * size + col

            A[i, i] = 1

            for drow, dcol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nrow, ncol = row + drow, col + dcol
                if 0 <= nrow < size and 0 <= ncol < size:
                    j = nrow * size + ncol
                    A[i, j] = 1

    return A

def solve_gf2(A: np.ndarray, b: np.ndarray) -> np.ndarray | None:

    m = len(b)

    # Augmented matrix [A | b]
    M = np.hstack([A, b.reshape(-1, 1)]).astype(np.uint8) % 2

    pivot_row = 0
    pivot_cols = []

    for col in range(m):
        if pivot_row >= m:
            break

        # Find rows with a 1 in current column below pivot row
        rows_with_one = np.where(M[pivot_row:, col] == 1)[0]
        if len(rows_with_one) == 0:
            continue # No pivot in this column, move to next column

        swap_row = pivot_row + rows_with_one[0]
        if swap_row != pivot_row:
            M[[pivot_row, swap_row]] = M[[swap_row, pivot_row]]

        # Eliminate column c in other rows using XOR operator
        for row in range(m):
            if row != pivot_row and M[row, col] == 1:
                M[row] ^= M[pivot_row]

        pivot_cols.append(col)
        pivot_row += 1

    # Check for inconsistency
    for row in range(pivot_row, m):
        if M[row, -1] == 1:
            return None # No solution

    # Extract solution vector
    x = np.zeros(m, dtype=np.uint8)
    for row, col in enumerate(pivot_cols):
        x[col] = M[row, -1]

    return x
