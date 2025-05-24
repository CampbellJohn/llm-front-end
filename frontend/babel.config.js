module.exports = (api) => {
  const isTest = api.env('test');
  
  return {
    presets: [
      ['@babel/preset-env', {
        modules: isTest ? 'commonjs' : false,
        targets: isTest ? { node: 'current' } : 'defaults',
        useBuiltIns: 'usage',
        corejs: 3,
      }],
      ['@babel/preset-react', { runtime: 'automatic' }],
    ],
    plugins: [
      '@babel/plugin-transform-runtime',
      '@babel/plugin-proposal-class-properties',
      '@babel/plugin-syntax-jsx',
      isTest && 'babel-plugin-transform-import-meta',
    ].filter(Boolean),
  };
};
