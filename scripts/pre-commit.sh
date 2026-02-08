#!/bin/bash
# Pre-commit hook for agent-bridge
# Install: ln -s ../../scripts/pre-commit.sh .git/hooks/pre-commit

echo "🔍 Running pre-commit checks..."

# Run Ruff linter
echo "📝 Checking code style..."
ruff check src/
if [ $? -ne 0 ]; then
    echo "❌ Ruff linter failed. Run 'make format' to fix."
    exit 1
fi

# Run mypy
echo "🔎 Checking types..."
mypy src/
if [ $? -ne 0 ]; then
    echo "❌ Type check failed. Fix type errors before committing."
    exit 1
fi

echo "✅ All checks passed!"
exit 0
