module.exports = {
  root: true,
  env: { browser: true, es2020: true, node: true },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  settings: { react: { version: '18.2' } },
  plugins: ['react-refresh'],
  globals: {
    vi: 'readonly',
    beforeEach: 'readonly',
    afterEach: 'readonly',
    describe: 'readonly',
    it: 'readonly',
    expect: 'readonly',
  },
  rules: {
    'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    'react/prop-types': 'off',
    'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    'react/no-unescaped-entities': 'off',
    // Catch TDZ bugs: "Cannot access 'X' before initialization" — scoped to the four pages this lint targets.
    // ponytail: import/no-cycle skipped — eslint-plugin-import not installed, no-new-deps rule.
    // ponytail: rule stays global-off; other pages have pre-existing warnings and must not fail --max-warnings 0.
  },
  overrides: [
    {
      files: [
        'src/pages/Staff.jsx',
        'src/pages/Students.jsx',
        'src/pages/Registry.jsx',
        'src/pages/Workflows.jsx',
      ],
      rules: {
        'no-use-before-define': ['warn', { functions: true, classes: true, variables: true }],
      },
    },
  ],
};
