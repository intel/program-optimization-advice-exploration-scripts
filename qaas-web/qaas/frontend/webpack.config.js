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
    mode: process.env.NODE_ENV || 'development',
    devtool: process.env.NODE_ENV === 'production' ? 'source-map' : 'inline-source-map',

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
            {
                test: /\.(png|svg|jpg|jpeg|gif)$/i,
                type: 'asset/resource',
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
        port: 3000,
        hot: true

    }
};
