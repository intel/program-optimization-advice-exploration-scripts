const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const Dotenv = require('dotenv-webpack');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
    entry: './src/index.js',
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: 'bundle.js'
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: 'babel-loader'
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader'],
            },
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './public/index.html'
        }),
        new Dotenv(),
        new CopyPlugin({
            patterns: [
                { from: './public/.htaccess', to: '.' } // copy .htaccess from public directory to dist directory
            ]
        })

    ],
    devServer: {
        static: {
            directory: path.join(__dirname, 'dist')
        },
        historyApiFallback: true,
        compress: true,
        port: 3000
    }
};
