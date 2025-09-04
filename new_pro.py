def find_route(matrix, target_values):
    rows = len(matrix)
    cols = len(matrix[0])

    def dfs(row, col, path):
        if matrix[row][col] in target_values:
            path.append(matrix[row][col])
            return True

        if matrix[row][col] != 1 or visited[row][col]:
            return False

        visited[row][col] = True
        path.append(matrix[row][col])

        if col + 1 < cols and dfs(row, col + 1, path):
            return True  # Move right
        if row + 1 < rows and dfs(row + 1, col, path):
            return True  # Move down

        path.pop()
        return False

    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] == 7:
                visited = [[False] * cols for _ in range(rows)]
                path = []
                if dfs(i, j, path):
                    return path

# Given matrix A
A = [
    [7, 0, 0, 0],
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [4, 0, 0, 6]
]

# Target values (4 or 6)
target_values = {4, 6}

# Find the best route
route = find_route(A, target_values)
print(route)
