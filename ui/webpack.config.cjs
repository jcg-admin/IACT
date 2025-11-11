const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');
const fs = require('fs');

const defaultFlags = {
  UI_BACKEND_CONFIG_SOURCE: 'mock',
  UI_BACKEND_PERMISSIONS_SOURCE: 'mock',
  UI_BACKEND_CALLS_SOURCE: 'mock',
};

const envFiles = [
  `.env.${process.env.NODE_ENV || 'development'}`,
  '.env',
];

const parseEnvFile = (filePath) => {
  const content = fs.readFileSync(filePath, 'utf-8');
  return content.split('\n').reduce((envAcc, line) => {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) {
      return envAcc;
    }
    const [key, ...rest] = trimmed.split('=');
    const value = rest.join('=').trim();
    envAcc[key.trim()] = value.replace(/^"|"$/g, '').replace(/^'|'$/g, '');
    return envAcc;
  }, {});
};

const resolvedEnv = envFiles.reduce((acc, fileName) => {
  const filePath = path.resolve(__dirname, fileName);
  if (fs.existsSync(filePath)) {
    const parsed = parseEnvFile(filePath);
    return { ...acc, ...parsed };
  }
  return acc;
}, {});

const definedEnv = Object.entries({ ...defaultFlags, ...resolvedEnv }).reduce((acc, [key, value]) => {
  acc[`process.env.${key}`] = JSON.stringify(value);
  return acc;
}, {});

module.exports = {
  entry: './src/index.jsx',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    clean: true,
    publicPath: '/',
  },
  resolve: {
    extensions: ['.js', '.jsx'],
    alias: {
      '@app': path.resolve(__dirname, 'src/app'),
      '@modules': path.resolve(__dirname, 'src/modules'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@styles': path.resolve(__dirname, 'src/styles'),
      '@state': path.resolve(__dirname, 'src/state'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@mocks': path.resolve(__dirname, 'src/mocks'),
    },
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
      inject: true,
    }),
    new webpack.DefinePlugin(definedEnv),
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
      serveIndex: false,
      watch: {
        ignored: '*.txt',
        usePolling: false,
      },
    },
    compress: true,
    port: 3000,
    hot: true,
    historyApiFallback: true,
    proxy: [
      {
        context: ['/api'],
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
        secure: false,
      },
    ],
    setupExitSignals: true,
    watchFiles: {
      paths: ['src/**/*', 'public/**/*'],
      options: {
        usePolling: false,
      },
    },
    webSocketServer: 'ws',
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
        },
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
        },
      },
    },
  },
};