const HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');
const dotenv = require('dotenv');
const webpack = require('webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');

// Load environment variables
const env = dotenv.config().parsed;
const envKeys = Object.keys(env).reduce((prev, next) => {
    prev[`process.env.${next}`] = JSON.stringify(env[next]);
    return prev;
}, {});
module.exports = {
    entry: './index.js',
    mode: 'development',
    output: {
        path: path.resolve(__dirname, './dist'),
        filename: 'index_bundle.js',
    },
    target: 'web',
    devServer: {
        port: '5000',
        static: {
            directory: path.join(__dirname, 'public'),
            publicPath: '/public',
            serveIndex: true,
        },
        open: true,
        hot: true,
        liveReload: true,
        historyApiFallback: true,
        proxy: {
            '/oneview/api': {
                target: 'http://127.0.0.1:5002',
            }
        },

    },
    resolve: {
        extensions: ['.js', '.jsx', '.json'],
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: 'babel-loader',
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader'],
            },
        ],
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: path.join(__dirname, 'public', 'index.html')
        }),
        new webpack.DefinePlugin(envKeys),
        new CopyWebpackPlugin({
            patterns: [
                { from: 'public/.htaccess', to: '.' } // copies .htaccess from public to the root of the dist directory
            ],
        }),

    ]
};