import openai

openai.api_key = os.environ.get('API_KEY')


def codeme(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Please write a Python function that calculates the factorial of a given number.",
            },
            {
                "role": "assistant",
                "content": "Sure, here's a Python function that calculates the factorial of a number:",
            },
            {
                "role": "assistant",
                "content": "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)",
            },
            {
                "role": "user",
                "content": "Can you modify the function to calculate the factorial using a loop instead of recursion?",
            },
            {
                "role": "assistant",
                "content": "Certainly, here's the modified function:",
            },
            {
                "role": "assistant",
                "content": "def factorial(n):\n    result = 1\n    for i in range(1, n+1):\n        result *= i\n    return result",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        top_p=0.925,
        max_tokens=1500,
        presence_penalty=0,
        logit_bias={1640: 10, 361: 10, 7783: 5},
    )

    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    prompt = (
        "Function to calculate the nth Fibonacci number:"
        "1. Recursive implementation with O(2^n) time complexity and O(n) space complexity:"
        "function fibonacciRecursive(n) {"
        "  if (n <= 1) {"
        "    return n;"
        "  }"
        "  return fibonacciRecursive(n - 1) + fibonacciRecursive(n - 2);"
        "}"
        "2. Iterative implementation with O(n) time complexity and O(1) space complexity:"
        "function fibonacciIterative(n) {"
        "  if (n <= 1) {"
        "    return n;"
        "  }"
        "  let prevPrev = 0;"
        "  let prev = 1;"
        "  let current = 0;"
        "  for (let i = 2; i <= n; i++) {"
        "    current = prev + prevPrev;"
        "    prevPrev = prev;"
        "    prev = current;"
        "}"
        "  return current;"
        "}"
        "3. Memoized recursive implementation with O(n) time complexity and O(n) space complexity:"
        "function fibonacciMemoized(n, memo = {}) {"
        "  if (n in memo) {"
        "    return memo[n];"
        "  }"
        "  if (n <= 1) {"
        "    return n;"
        "  }"
        "  memo[n] = fibonacciMemoized(n - 1, memo) + fibonacciMemoized(n - 2, memo);"
        "  return memo[n];"
        "}"
        "4. Matrix exponentiation implementation with O(log n) time complexity and O(1) space complexity:"
        "function fibonacciMatrixExponentiation(n) {"
        "  if (n <= 1) {"
        "    return n;"
        "  }"
        "  const matrix = [[1, 1], [1, 0]];"
        "  matrixPower(matrix, n - 1);"
        "  return matrix[0][0];"
        "}"
        "function matrixPower(matrix, n) {"
        "  if (n <= 1) {"
        "    return;"
        "  }"
        "  matrixPower(matrix, Math.floor(n / 2));"
        "  multiplyMatrix(matrix, matrix);"
        "  if (n % 2 === 1) {"
        "    const baseMatrix = [[1, 1], [1, 0]];"
        "    multiplyMatrix(matrix, baseMatrix);"
        "  }"
        "}"
        "function multiplyMatrix(matrix1, matrix2) {"
        "  const a = matrix1[0][0];"
        "  const b = matrix1[0][1];"
        "  const c = matrix1[1][0];"
        "  const d = matrix1[1][1];"
        "  const e = matrix2[0][0];"
        "  const f = matrix2[0][1];"
        "  const g = matrix2[1][0];"
        "  const h = matrix2[1][1];"
        "  matrix1[0][0] = a * e + b * g;"
        "  matrix1[0][1] = a * f + b * h;"
        "  matrix1[1][0] = c * e + d * g;"
        "  matrix1[1][1] = c * f + d * h;"
        "}"
        "Which implementation of the Fibonacci function is the best?"
    )

    response = codeme(prompt)
    print(response)
