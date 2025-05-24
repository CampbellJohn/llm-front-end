const babelJest = require('babel-jest').default;

const babelOptions = {
  presets: [
    ['@babel/preset-env', {
      modules: 'commonjs',
      targets: { node: 'current' },
      useBuiltIns: 'usage',
      corejs: 3,
    }],
    ['@babel/preset-react', { runtime: 'automatic' }],
  ],
  plugins: [
    '@babel/plugin-transform-runtime',
    '@babel/plugin-proposal-class-properties',
    '@babel/plugin-syntax-jsx',
    'babel-plugin-transform-import-meta',
  ],
};

module.exports = babelJest.createTransformer(babelOptions);
