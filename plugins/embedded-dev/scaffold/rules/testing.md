---
paths:
  - "test/**/*.c"
  - "tests/**/*.c"
---

# Testing Rules (Embedded C)

- Use Unity or CUnit test framework
- Test each module in isolation with mock HAL layers
- Mirror src/ structure in test/
- Use assert macros for all test conditions
- Build tests with cmake before running
